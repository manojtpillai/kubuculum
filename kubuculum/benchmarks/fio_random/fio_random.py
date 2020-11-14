
import logging
import os
import subprocess
import time
from kubuculum.servers.server_fio import server_fio
from kubuculum.dropcaches import dropcaches
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class fio_random:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        self.tag = 'fio_random' # TODO: make it unique

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params; this will override some of the defaults
        labels_path = ['benchmarks', 'fio_random']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag
        logger.debug (f'parameters: {self.params}')

        # create directory for self
        util_functions.create_dir (self.params['dir'])

        # create handle for dropping caches
        #
        self.dc_handle = dropcaches.dropcaches \
            (self.params['dir'], params_dict, globals)

        # create a handle for the fio server object
        #
        self.serverhandle = server_fio.server_fio \
            (self.params['dir'], params_dict, globals)

        #
        # derive parameters for fio server for later use
        #

        # pass on basic parameters
        self.serverparams = { 
            'nservers': self.params['ninstances']
        }

        # derive space requirements 
        if 'pvcsize_gb' in self.params:
            self.serverparams['pvcsize_gb'] = self.params['pvcsize_gb']
        else:
            pvcsize_gb = self.params['numjobs'] * self.params['filesize_gb']
            self.serverparams['pvcsize_gb'] = int (pvcsize_gb * \
                self.params['scalefactor'] + self.params['extraspace_gb'])

        # pass on storageclass, if specified
        if 'storageclass' in self.params:
            self.serverparams['storageclass'] = self.params['storageclass']

        # pass on nodeselector, if specified
        if 'server_nodeselector' in self.params:
            self.serverparams['nodeselector'] = \
                self.params['server_nodeselector']


    # prepare phase: create data set
    def prepare (self):

        # shortcuts for commonly used parameters
        namespace = self.params['namespace']
        run_dir = self.params['dir']
        preparep_dir = run_dir + '/prepare_phase'
        podlabel = self.params['prep_podlabel']

        # create directory for prepare_phase output
        util_functions.create_dir (preparep_dir)

        # start the servers
        logger.info (f'starting server_fio pods')
        conn_params = self.serverhandle.start (self.serverparams)

        # update self.params with parameters required for server_fio
        util_functions.deep_update (self.params, conn_params)

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['prepare_template']
        yaml_file = run_dir + '/' + self.params['prepare_yaml']

        # create yaml for prepare phase
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.info (f'creating prep pod')

        # create prep pod, and wait for its completion
        # expected pod count is 1, pause of 5 sec, 0 retries
        k8s_wrappers.createpods_sync (namespace, yaml_file, podlabel, \
            1, 5, 0, self.params['maxruntime_sec'])
        logger.info (f'prep pod completed')

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], preparep_dir)
        logger.info (f'copied output from prep pod')

        # delete prep pod
        k8s_wrappers.deletefrom_yaml (yaml_file, namespace)
        logger.info (f'deleted prep pod')

    # run single iteration/test against previously created data set
    def _run (self, run_dir):

        # shortcuts for commonly used parameters
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['run_template']
        yaml_file = run_dir + '/' + self.params['run_yaml']

        # create yaml for run phase
        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        logger.info (f'creating pod to run test')

        # create pod, and wait for its completion
        # expected pod count is 1, pause of 5 sec, 0 retries
        k8s_wrappers.createpods_sync (namespace, yaml_file, podlabel, \
            1, 5, 0, self.params['maxruntime_sec'])

        logger.info (f'pod completed')

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], run_dir)
        logger.info (f'copied output from pod')

        # delete run phase pod
        k8s_wrappers.deletefrom_yaml (yaml_file, namespace)
        logger.info (f'deleted pod')

    # prepare for next iteration of run phase
    def _setup_next (self):
        self.dc_handle.drop_caches ()
        k8s_wrappers.await_termination (self.params['namespace'], \
            self.params['podlabel'])

    # run phase : execute test(s) on previously created data set
    def run (self):

        # will there be multiple iterations?
        num_iterations = len(self.params['bs_kb_list']) * \
            len(self.params['iodepth_list'])

        # rate_iops_list is optional
        if 'rate_iops_list' in self.params:
            num_inner = len (self.params['rate_iops_list'])
            num_iterations *= num_inner
        else:
            num_inner = 1

        logger.info (f'tests to be performed: {num_iterations}')

        iter = 0
        for bs_kb in self.params['bs_kb_list']:
            self.params['bs_kb'] = bs_kb
            bs_dirtag = 'bs_kb-' + str (bs_kb)

            for iodepth in self.params['iodepth_list']:
                self.params['iodepth'] = iodepth
                iod_dirtag = '_iodepth-' + str (iodepth)

                i_inner = 0
                while i_inner < num_inner:
                    if 'rate_iops_list' in self.params:
                        rate_iops = self.params['rate_iops_list'][i_inner]
                        self.params['rate_iops'] = rate_iops
                        run_dir = bs_dirtag + iod_dirtag \
                            + '_rate_iops-' + str (rate_iops)
                    else:
                        run_dir = bs_dirtag + iod_dirtag

                    if num_iterations > 1:
                        run_dirpath = self.params['dir'] + '/' + run_dir
                        util_functions.create_dir (run_dirpath)
                    else:
                        run_dirpath = self.params['dir']

                    logger.info (f'starting test : {iter}')
                    self._run (run_dirpath)
                    logger.info (f'completed test : {iter}')

                    iter += 1
                    i_inner += 1
                    if iter < num_iterations:
                        self._setup_next ()

        logger.info (f'tests performed: {iter}')

        # gather info from server pods
        self.serverhandle.gather ()

        logger.info (f'stopping server_fio pods')
        self.serverhandle.stop ()



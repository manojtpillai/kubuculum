
import logging
import os
import subprocess
import time
from kubuculum.server_fio import server_fio
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class fio_random:

    # p has params that override the defaults for this class
    def __init__ (self, p):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params; this will override some of the defaults
        util_functions.deep_update (self.params, p)

        #
        # derive parameters for fio server
        #

        # pass on basic parameters
        self.serverparams = { 
            'namespace': self.params['namespace'],
            'nservers': self.params['ninstances']
        }

        # specify output directory for callee
        self.serverparams['dir'] = self.params['dir'] + '/' + 'server_fio'

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


    # prepare phase: create data set
    def prepare (self):

        # shortcuts for commonly used parameters
        namespace = self.params['namespace']
        run_dir = self.params['dir']
        preparep_dir = run_dir + "/prepare_phase"
        podlabel = self.params['prep_podlabel']

        # create directory for callee
        util_functions.create_dir (self.serverparams['dir'])

        # create directory for prepare_phase output
        util_functions.create_dir (preparep_dir)

        # start the servers
        self.serverhandle = server_fio.server_fio (self.serverparams)
        conn_params = self.serverhandle.start ()

        # update self.params with parameters required for server_fio
        self.params.update (conn_params)

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['prepare_template']
        yaml_file = run_dir + '/' + self.params['prepare_yaml']

        # create yaml for prepare phase
        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        # create prep pod, and wait for its completion
        # expected pod count is 1, pause of 5 sec, 0 retries
        k8s_wrappers.createpods_sync (namespace, yaml_file, podlabel, \
            1, 5, 0, self.params['maxruntime_sec'])
        logger.info ("fio_random prepare pod completed")

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], preparep_dir)
        logger.info ("copied output from fio_random prepare pod")

        # delete prep pod
        k8s_wrappers.deletefrom_yaml (namespace, yaml_file)
        logger.info ("deleted fio_random prepare pod")

    # run phase : execute test on previously created data set
    def run (self):

        # shortcuts for commonly used parameters
        namespace = self.params['namespace']
        run_dir = self.params['dir']
        podlabel = self.params['podlabel']

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['run_template']
        yaml_file = run_dir + '/' + self.params['run_yaml']

        # create yaml for run phase
        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        # create pod, and wait for its completion
        # expected pod count is 1, pause of 5 sec, 0 retries
        k8s_wrappers.createpods_sync (namespace, yaml_file, podlabel, \
            1, 5, 0, self.params['maxruntime_sec'])
        logger.info ("fio_random run pod completed")

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], run_dir)
        logger.info ("copied output from fio_random run pod")

        # delete prep pod
        k8s_wrappers.deletefrom_yaml (namespace, yaml_file)
        logger.info ("deleted fio_random run pod")

        logger.info ("stopping server_fio pods")
        self.serverhandle.stop ()



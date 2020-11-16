
import logging
import os
from kubuculum.servers.server_fio import server_fio
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class fio_iops:

    instance_counter = 0

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # get a unique id and tag
        self.id = fio_iops.instance_counter
        self.tag = 'calm-fioiops-' + str (self.id)
        fio_iops.instance_counter += 1

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params; this will override some of the defaults
        labels_path = ['calm', 'fio_iops']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag
        self.params['name'] = self.tag
        self.params['podlabel'] = "name=" + self.tag

        logger.debug (f'parameters: {self.params}')

        # create directory for self
        util_functions.create_dir (self.params['dir'])

        # create a handle for the fio server object
        #
        self.serverhandle = server_fio.server_fio \
            (self.params['dir'], params_dict, globals)

        #
        # derive parameters for fio server for later use
        #

        # pass on basic parameters
        self.serverparams = { 
            'nservers': self.params['ninstances'],
            'fio_image': self.params['fio_image']
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


    # start fio servers and client
    def start (self):

        # shortcuts for commonly used parameters
        namespace = self.params['namespace']
        run_dir = self.params['dir']
        podlabel = self.params['podlabel']

        # start the servers
        logger.info (f'{self.tag}: starting server_fio pods')
        conn_params = self.serverhandle.start (self.serverparams)

        # update self.params with parameters required for server_fio
        util_functions.deep_update (self.params, conn_params)

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['template']
        yaml_file = run_dir + '/' + self.params['yaml_file']

        # create yaml for prepare phase
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.info (f'{self.tag}: creating pod')

        # create pod, and continue without waiting for ready
        k8s_wrappers.createpods_async (namespace, yaml_file)

    # wait for pod to reach ready state, if necessary
    def ensure_ready (self):

        logger.info (f'{self.tag}: wait for prep to complete')

        # shortcuts
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']

        # wait for pod to reach ready state
        # expected pod count is 1, pause of 2 sec, 0 retries
        # maxpreptime as timeout
        k8s_wrappers.ensure_ready (namespace, podlabel, \
            1, 2, 0, self.params['maxpreptime_sec'])

        logger.info (f'{self.tag} is active')

    # delete pods 
    def stop (self):

        # shortcuts 
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']
        run_dir = self.params['dir']
        yaml_file = run_dir + '/' + self.params['yaml_file']

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], run_dir)

        # delete client pod
        k8s_wrappers.deletefrom_yaml (yaml_file, namespace)

        # gather info from server pods
        self.serverhandle.gather ()

        logger.info (f'{self.tag}: stopping server_fio pods')
        self.serverhandle.stop ()

        logger.info (f'{self.tag} stopped')



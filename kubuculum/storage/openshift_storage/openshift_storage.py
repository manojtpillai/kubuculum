
import logging
import os
import kubuculum.dropcaches.util_functions
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class openshift_storage:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params; doesn't need kubuculum namespace
        labels_path = ['storage', 'openshift_storage']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        self.params['dir'] = run_dir + '/openshift_storage'

    def update_params (self, passed_params):
        util_functions.deep_update (self.params, passed_params)
        logger.debug (f'openshift_storage parameters: {self.params}')

    def drop_caches (self):

        # shortcuts
        namespace = self.params['ocs_namespace']

        # get the tools pod; there is only one
        podlist = k8s_wrappers.get_podlist (namespace, \
            self.params['podlabel'])

        if len(podlist) >= 1:
            tools_pod = podlist[0] 
            mds_command = 'ceph tell mds.* cache drop'
            osd_command = 'ceph tell osd.* cache drop'

            logger.debug (f'dropping ceph caches')
            k8s_wrappers.exec_command (mds_command, tools_pod, namespace)
            k8s_wrappers.exec_command (osd_command, tools_pod, namespace)
            logger.info (f'ceph caches dropped')
        else:
            logger.warning (f'tools pod not found; ceph caches not dropped')




import logging
import os
from kubuculum import util_functions
from kubuculum import k8s_wrappers

class setup_run:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        self.params['namespace'] = globals['namespace']

        # change to absolute paths for yaml files
        self.params['rolebinding_yaml'] = \
            self.params['yaml_dir'] + '/' + self.params['namespace'] \
            + '.' + self.params['rolebinding_yaml']

        self.params['role_yaml'] = \
            self.params['yaml_dir'] + '/' + self.params['namespace'] \
            + '.' + self.params['role_yaml']

    def do_setup (self):

        # log only in setup
        # cleanup may be called when logging not enabled
        logger = logging.getLogger (__name__)

        # shortcuts
        namespace = self.params['namespace']

        logger.info (f'creating namespace: {namespace}')
        k8s_wrappers.create_namespace (namespace)

        templates_dir = self.dirpath + '/' + self.params['templates_dir']

        template_file = self.params['role_template']
        yaml_file = self.params['role_yaml']
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'creating role')
        k8s_wrappers.createfrom_yaml (yaml_file)

        template_file = self.params['rolebinding_template']
        yaml_file = self.params['rolebinding_yaml']
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'creating rolebinding')
        k8s_wrappers.createfrom_yaml (yaml_file)

    def cleanup (self):

        # delete rolebinding
        k8s_wrappers.deletefrom_yaml (self.params['rolebinding_yaml'])

        # delete role
        k8s_wrappers.deletefrom_yaml (self.params['role_yaml'])

        # delete namespace
        k8s_wrappers.delete_namespace (self.params['namespace'])


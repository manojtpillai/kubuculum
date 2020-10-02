
import logging
import os
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # output directory for self
        self.tag = 'setup_run' 

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        self.params['namespace'] = globals['namespace']
        self.params['dir'] = run_dir + '/' + self.tag
        logger.debug (f'setup_run parameters: {self.params}')

    def do_setup (self):

        # shortcuts
        namespace = self.params['namespace']
        run_dir = self.params['dir']

        # create directory for self
        util_functions.create_dir (run_dir)

        logger.info (f'creating namespace: {namespace}')
        k8s_wrappers.create_namespace (namespace)

        templates_dir = self.dirpath + '/' + self.params['templates_dir']

        template_file = self.params['role_template']
        yaml_file = '/tmp' + self.params['role_yaml']
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'creating role')
        k8s_wrappers.createfrom_yaml (yaml_file)

        template_file = self.params['rolebinding_template']
        yaml_file = '/tmp' + self.params['rolebinding_yaml']
        util_functions.instantiate_template (templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'creating rolebinding')
        k8s_wrappers.createfrom_yaml (yaml_file)

    def cleanup (self):

        run_dir = self.params['dir']
        namespace = self.params['namespace']

        logger.debug (f'deleting rolebinding')
        yaml_file = '/tmp' + self.params['rolebinding_yaml']
        k8s_wrappers.deletefrom_yaml (yaml_file)

        logger.debug (f'deleting role')
        yaml_file = '/tmp' + self.params['role_yaml']
        k8s_wrappers.deletefrom_yaml (yaml_file)

        logger.info (f'deleting namespace: {namespace}')
        k8s_wrappers.delete_namespace (namespace)


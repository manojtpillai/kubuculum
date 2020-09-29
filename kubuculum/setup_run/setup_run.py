
import subprocess
import time
import logging
import copy
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, run_dir, params_dict, globals):

        self.ns = globals['namespace']
        logger.debug (f'setup_run parameters: {self.ns}')

    def do_setup (self):

        # TODO: add roles and rolebindings
        logger.info (f'creating namespace: {self.ns}')
        k8s_wrappers.create_namespace (self.ns)

    def cleanup (self):

        logger.info (f'deleting namespace: {self.ns}')
        k8s_wrappers.delete_namespace (self.ns)



import subprocess
import time
import logging
import copy
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, p):

        self.params = copy.deepcopy (p)
        logger.debug (f'setup_run parameters: {self.params}')

    def do_setup (self):

        # TODO: add roles and rolebindings
        logger.info (f'creating namespace: {self.params["namespace"]}')
        k8s_wrappers.create_namespace (self.params['namespace'])

    def cleanup (self):

        logger.info (f'deleting namespace: {self.params["namespace"]}')
        k8s_wrappers.delete_namespace (self.params['namespace'])



import subprocess
import time
import logging
import copy

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, p):

        self.params = copy.deepcopy (p)
        logger.debug (f'setup parameters: {self.params}')

    def do_setup (self):

        logger.info (f'creating namespace: {self.params["namespace"]}')
        subprocess.run (["kubectl", "create", "namespace", self.params['namespace']])

    def cleanup (self):

        logger.info (f'deleting namespace: {self.params["namespace"]}')
        subprocess.run (["kubectl", "delete", "namespace", self.params['namespace']])



import subprocess
import time
import logging
from kubuculum import util_functions

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, p):

        # TODO: read from defaults file
        # TODO: add roles and rolebindings
        self.params = {
            'namespace': 'nm-kubuculum',
            'dir': '/tmp'
        }
        util_functions.deep_update (self.params, p)
        logger.debug (f'setup parameters: {self.params}')

    def do_setup (self):

        logger.info (f'creating namespace: {self.params["namespace"]}')
        subprocess.run (["kubectl", "create", "namespace", self.params['namespace']])

    def cleanup (self):

        logger.info (f'deleting namespace: {self.params["namespace"]}')
        subprocess.run (["kubectl", "delete", "namespace", self.params['namespace']])


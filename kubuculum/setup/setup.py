
import subprocess
import time
import logging

logger = logging.getLogger (__name__)

class environs:

    def __init__ (self, p):

        # TODO: read from defaults file
        # TODO: add roles and rolebindings
        self.params = {
            'namespace': 'nm-kubuculum',
            'dir': '/tmp'
        }
        self.params.update (p)

    def do_setup (self):

        logger.info ("creating namespace: %s", self.params['namespace'])
        subprocess.run (["kubectl", "create", "namespace", self.params['namespace']])

    def cleanup (self):

        logger.info ("deleting namespace: %s", self.params['namespace'])
        subprocess.run (["kubectl", "delete", "namespace", self.params['namespace']])


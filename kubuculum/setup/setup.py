
import subprocess
import time

class environs:

    def __init__ (self, p):

        self.params = {
            'namespace': 'nm-kubuculum',
            'dir': '/tmp'
        }
        self.params.update (p)

    def do_setup (self):

        subprocess.run (["kubectl", "create", "namespace", self.params['namespace']])

    def cleanup (self):

        subprocess.run (["kubectl", "delete", "namespace", self.params['namespace']])


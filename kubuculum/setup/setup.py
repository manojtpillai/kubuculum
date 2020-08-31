
import subprocess
import time

class environment:

    def __init__ (self, p={}):

        self.params = {
            'namespace': 'nm-kubuculum',
            'basedir': '/tmp'
        }
        self.params.update (p)

    def do_setup(self):

        subprocess.run (["kubectl", "create", "namespace", self.params['namespace']])

        ts = str (time.time ())
        subdir = self.params['basedir'] + "/run_" + ts
        subprocess.run (["mkdir", subdir])

    def cleanup(self):

        subprocess.run (["kubectl", "delete", "namespace", self.params['namespace']])


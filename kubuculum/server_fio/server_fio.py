
import os
import subprocess
from kubuculum import util_functions

class server_fio:

    # p has params that override the defaults for this class
    def __init__ (self, p):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        self.params.update(p)

    # start: create StatefulSet
    def start (self):

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['template_file']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        # create the pods
        subprocess.run (["kubectl", "create", "-f", yaml_file, "-n", \
            self.params['namespace']])


    # stop operation: delete StatefulSet and PVCs
    def stop (self):

        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # delete the pods
        subprocess.run (["kubectl", "delete", "-f", yaml_file, "-n", \
            self.params['namespace']])

        # delete the PVCs
        subprocess.run (["kubectl", "delete", "pvc", "-l", \
            self.params['podlabel'], "-n", self.params['namespace']])




import os
import subprocess
from kubuculum import util_functions
from kubuculum import k8s_wrappers

class server_fio:

    # p has params that override the defaults for this class
    def __init__ (self, p):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # TODO: deep update
        # update params
        self.params.update(p)

        # parameters clients need in order to use this object
        self.returnparams = {}
        self.returnparams['datadir'] = self.params['datadir']
        self.returnparams['serverlist'] = [] # populated at start

    # start: create StatefulSet
    def start (self):

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['template_file']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        # create the pods
        # expected count is nservers
        # set retries to nservers with pause of 30 sec
        # timeout of 300 sec; TODO: use a param here
        k8s_wrappers.createpods_sync (self.params['namespace'], \
            yaml_file, self.params['podlabel'], \
            self.params['nservers'], 30, self.params['nservers'], 300)

        # TODO: use list of pods as returned by k8s
        # update returnparams with server list
        for inst in range (self.params['nservers']):
            new_elem = 'server-fio-' + str (inst) + '.server-fio'
            self.returnparams['serverlist'].append (new_elem)

        return self.returnparams


    # stop operation: delete StatefulSet and PVCs
    def stop (self):

        namespace = self.params['namespace']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # delete the pods
        k8s_wrappers.deletefrom_yaml (namespace, yaml_file)

        # delete the PVCs
        k8s_wrappers.deletefrom_label (namespace, \
            self.params['podlabel'], "pvc")




import logging
import os
import subprocess
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class server_fio:

    instance_counter = 0

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # get a unique id and tag
        self.id = server_fio.instance_counter
        self.tag = 'server-fio' + str (self.id)
        server_fio.instance_counter += 1

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        labels_path = ['servers', 'server_fio']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag
        self.params['name'] = self.tag
        self.params['podlabel'] = "name=" + self.tag

        # parameters clients need in order to use this object
        self.returnparams = {}
        self.returnparams['datadir'] = self.params['datadir']
        self.returnparams['serverlist'] = [] # populated at start

    # start: create StatefulSet
    def start (self, passed_params):

        logger.debug (f'{self.tag} start')
        util_functions.deep_update (self.params, passed_params)
        logger.debug (f'{self.tag} parameters: {self.params}')

        # create directory for self
        util_functions.create_dir (self.params['dir'])

        # shortcuts
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['template_file']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'starting {self.tag} pods')
        # create the pods
        # expected count is nservers
        # set retries to nservers with pause of 30 sec
        # timeout of 300 sec; TODO: use a param here
        k8s_wrappers.createpods_sync (namespace, yaml_file, podlabel, \
            self.params['nservers'], 30, self.params['nservers'], 300)
        logger.debug (f'{self.tag} pods ready')

        # get pod locations
        k8s_wrappers.get_podlocations (podlabel, namespace, \
            self.params['dir'])

        # TODO: use list of pods as returned by k8s
        # update returnparams with server list
        for inst in range (self.params['nservers']):
            new_elem = self.tag + '-' + str (inst) + '.' + self.tag
            self.returnparams['serverlist'].append (new_elem)

        return self.returnparams

    # gather output
    def gather (self, tag=""):

        # shortcuts
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']

        if tag == "":
            gather_dir = self.params['dir']
        else:
            # TODO: gather_dir should not exist
            gather_dir = self.params['dir'] + tag
            util_functions.create_dir (gather_dir)

        # form list of commands 
        ls_command = 'ls -l' + ' ' + self.params['datadir']
        command_list = [(ls_command, 'ls_l.txt'), \
            ('df -h', 'df_h.txt'), ('mount', 'mount.txt')]

        # gather output of commands
        k8s_wrappers.command_tofile (command_list, podlabel, \
            namespace, gather_dir)


    # stop operation: delete StatefulSet and PVCs
    def stop (self):

        namespace = self.params['namespace']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # delete the pods
        k8s_wrappers.deletefrom_yaml (yaml_file, namespace)

        # delete the PVCs
        k8s_wrappers.deletefrom_label (namespace, \
            self.params['podlabel'], "pvc")



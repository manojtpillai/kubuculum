
import logging
import os
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class sysstat:

    instance_counter = 0

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # get a unique id and tag
        self.id = sysstat.instance_counter
        self.tag = 'sysstat-' + str (self.id)
        sysstat.instance_counter += 1

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        labels_path = ['statistics', 'sysstat']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag
        self.params['name'] = self.tag
        self.params['podlabel'] = "name=" + self.tag

    # extra parameters passed by caller
    # TODO: log warning and ignore if already started
    def update_params (self, passed_params):
        util_functions.deep_update (self.params, passed_params)
        logger.debug (f'sysstat parameters: {self.params}')

    # start: create daemonset
    def start (self):

        logger.info (f'{self.tag} start')

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

        logger.debug (f'{self.tag}: starting sysstat pods')
        # create the pods
        # expected count is unknown, use 0; so retries not relevant
        # pause of 10 sec
        # timeout of 300 sec; TODO: use a param here
        k8s_wrappers.createpods_sync (namespace, yaml_file, \
            podlabel, 0, 10, 0, 300)
        logger.debug (f'{self.tag}: pods ready')

        # get pod locations
        k8s_wrappers.get_podlocations (podlabel, namespace, \
            self.params['dir'])

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

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], gather_dir)
        logger.info (f'{self.tag} gather: copied output from sysstat pods')

    # stop operation: delete daemonset
    def stop (self):

        namespace = self.params['namespace']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # delete the pods
        k8s_wrappers.deletefrom_yaml (yaml_file, namespace)
        logger.info (f'{self.tag} stopped')


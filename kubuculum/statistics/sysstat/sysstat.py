
import logging
import os
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class sysstat:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # output directory for self
        self.tag = 'sysstat' # TODO: make it unique

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        labels_path = ['statistics', 'sysstat']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag

    # start: create daemonset
    def start (self, passed_params={}):

        logger.debug (f'sysstat start')
        util_functions.deep_update (self.params, passed_params)
        logger.debug (f'sysstat parameters: {self.params}')

        # create directory for self
        util_functions.create_dir (self.params['dir'])

        templates_dir = self.dirpath + '/' + self.params['templates_dir']
        template_file = self.params['template_file']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        util_functions.instantiate_template ( templates_dir, \
            template_file, yaml_file, self.params)

        logger.debug (f'starting sysstat pods')
        # create the pods
        # expected count is unknown, use 0; so retries not relevant
        # pause of 10 sec
        # timeout of 300 sec; TODO: use a param here
        k8s_wrappers.createpods_sync (self.params['namespace'], \
            yaml_file, self.params['podlabel'], 3, 10, 3, 300)
        logger.debug (f'sysstat pods ready')

    # gather output
    def gather (self, tag=""):

        # shortcuts
        namespace = self.params['namespace']
        podlabel = self.params['podlabel']

        if tag == "":
            gather_dir = self.params['dir']
        else:
            gather_dir = self.params['dir'] + tag
            util_functions.create_dir (gather_dir)

        # copy output from pod
        k8s_wrappers.copyfrompods (namespace, podlabel, \
            self.params['podoutdir'], gather_dir)
        logger.info ("copied output from sysstat pods")

    # stop operation: delete daemonset
    def stop (self):

        namespace = self.params['namespace']
        yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # delete the pods
        k8s_wrappers.deletefrom_yaml (namespace, yaml_file)



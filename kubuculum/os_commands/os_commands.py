
import logging
import os
from kubuculum import util_functions
from kubuculum import k8s_wrappers

logger = logging.getLogger (__name__)

class os_commands:

    instance_counter = 0

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # get a unique id and tag
        self.id = os_commands.instance_counter
        self.tag = 'oscommands-' + str (self.id)
        os_commands.instance_counter += 1

        # load defaults from file
        yaml_file = self.dirpath + '/defaults.yaml'
        self.params = util_functions.dict_from_file (yaml_file)

        # update params
        labels_path = ['os_commands']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
        util_functions.update_modparams (self.params, globals)
        self.params['dir'] = run_dir + '/' + self.tag
        self.params['name'] = self.tag
        self.params['podlabel'] = 'name=' + self.tag

        self.drop_count = 0

    # extra parmeters passed by caller
    def update_params (self, passed_params):
        util_functions.deep_update (self.params, passed_params)

    # drop_caches: create daemonset of pods to drop os caches
    def drop_caches (self):

        logger.debug (f'{self.tag}: drop_caches')

        # command for pods to execute 
        self.params['command'] = "sync; sysctl vm.drop_caches=3"
        logger.debug (f'{self.tag} parameters: {self.params}')

        # drop_caches might be called multiple times on same object
        if self.drop_count == 0:
            # first call, create directory for self
            # TODO: dir present should not be an error
            util_functions.create_dir (self.params['dir'])

            templates_dir = self.dirpath + '/' + self.params['templates_dir']
            template_file = self.params['template_file']
            yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

            util_functions.instantiate_template ( templates_dir, \
                template_file, yaml_file, self.params)
        else:
            yaml_file = self.params['dir'] + '/' + self.params['yaml_file']

        # create the pods
        # expected count is unknown, use 0; so retries not relevant
        # pause of 10 sec, retries 0
        # timeout of 300 sec; TODO: use a param here
        k8s_wrappers.createpods_sync (self.params['namespace'], \
            yaml_file, self.params['podlabel'], 0, 10, 0, 300)
        logger.debug (f'{self.tag}: pods ready')

        self.drop_count += 1

        # pods ready means task complete
        k8s_wrappers.deletefrom_yaml (yaml_file, self.params['namespace'])
        logger.info (f'{self.tag}: OS caches dropped')



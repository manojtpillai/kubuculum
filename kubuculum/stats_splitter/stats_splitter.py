
import logging
import os
import kubuculum.statistics.util_functions
from kubuculum import util_functions

logger = logging.getLogger (__name__)

class stats_splitter:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        self.tag = 'stats_splitter' 

        # update params
        labels_path = ['stats_splitter']
        self.params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.update_modparams (self.params, globals)

        self.modhandles = []
        for stats_dict in self.params['stats_list']:

            logger.debug (f'stats_splittler: {stats_dict}')
            # stats_dict is of the form: stats_module: {dict_of_params}
            (stats_module, stats_module_params) = \
                list (stats_dict.items())[0]
            handle = kubuculum.statistics.util_functions.create_object \
                (stats_module, run_dir, params_dict, globals)
            handle.update_params (stats_module_params)
            self.modhandles.append (handle)


    def start (self):

        for handle in self.modhandles:
            handle.start ()

    def gather (self, tag=""):

        for handle in self.modhandles:
            handle.gather (tag)

    def stop (self):

        for handle in self.modhandles:
            handle.stop ()


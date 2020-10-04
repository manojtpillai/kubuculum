
import logging
import os
import kubuculum.dropcaches.util_functions
from kubuculum import util_functions

logger = logging.getLogger (__name__)

class dropcaches:

    def __init__ (self, run_dir, params_dict, globals):

        # get directory pathname for module
        self.dirpath = os.path.dirname (os.path.abspath (__file__))

        # update params
        labels_path = ['dropcaches']
        self.params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.update_modparams (self.params, globals)

        self.modhandles = []
        for mod_dict in self.params['module_list']:

            logger.debug (f'dropcaches: {mod_dict}')
            # mod_dict is of the form: module_name: {dict_of_params}
            (dc_module, dc_module_params) = \
                list (mod_dict.items())[0]
            handle = kubuculum.dropcaches.util_functions.create_object \
                (dc_module, run_dir, params_dict, globals)
            handle.update_params (dc_module_params)
            self.modhandles.append (handle)

    def drop_caches (self):

        for handle in self.modhandles:
            handle.drop_caches ()


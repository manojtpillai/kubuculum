
import logging
from kubuculum import util_functions

logger = logging.getLogger (__name__)

class dummy_pause:

    def __init__ (self, run_dir, params_dict, globals):

        # TODO: read from defaults file
        self.params = { 
            'duration_sec': 5 
        }
        labels_path = ['benchmarks', 'dummy_pause']
        new_params = util_functions.get_modparams (params_dict, labels_path)
        util_functions.deep_update (self.params, new_params)
      
        logger.debug (f'dummy_pause parameters: {self.params}')

    # prepare phase: nothing to do 
    def prepare (self):

        pass

    # run phase : sleep for duration
    def run (self):

        # shortcuts
        duration = self.params['duration_sec']

        logger.info (f'run: sleeping for {duration} seconds; ctrl-c to continue')
        util_functions.intr_pause (duration)
        logger.info (f'run: completed')



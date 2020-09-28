
import time
import logging
from kubuculum import util_functions

logger = logging.getLogger (__name__)

class dummy_pause:

    def __init__ (self, p={}):

        # TODO: read from defaults file
        self.params = { 
            'duration': 5 
        }
        util_functions.deep_update (self.params, p)
        logger.debug (f'dummy_pause parameters: {self.params}')

    # prepare phase: nothing to do 
    def prepare (self):

        pass

    # run phase : sleep for duration
    def run (self):

        logger.info ('dummy_pause: run: start')
        time.sleep(self.params['duration'])
        logger.info ('dummy_pause: run: completed')




import time
import logging

logger = logging.getLogger (__name__)

class dummy_pause:

    def __init__ (self, p={}):

        # TODO: read from defaults file
        self.params = { 
            'duration': 5 
        }
        self.params.update(p)

    # prepare phase: nothing to do 
    def prepare (self):

        pass

    # run phase : sleep for duration
    def run (self):

        logger.info ('dummy_pause: run: start')
        time.sleep(self.params['duration'])
        logger.info ('dummy_pause: run: completed')



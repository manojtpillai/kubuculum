
import time

class dummy_pause:

    def __init__ (self, p={}):

        self.params = { 
            'duration': 5 
        }
        self.params.update(p)

    # prepare phase: nothing to do 
    def prepare (self):

        pass

    # run phase : sleep for duration
    def run (self):

        print('sleeping at: %s' % time.ctime())
        time.sleep(self.params['duration'])
        print('woke up at: %s' % time.ctime())



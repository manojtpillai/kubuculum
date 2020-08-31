
import time

class fio_random:

    def __init__ (self, p={}):

        self.params = { 
            'ninstances': 1,
            'bs_kb': 8,
            'filesize_gb': 1,
            'numjobs': 1,
            'runtime_sec': 30 
        }
        self.params.update(p)

    # prepare phase: create data set
    def prepare (self):

        print ("fio_random: prepare")

    # run phase : sleep for duration
    def run (self):

        print (self.params)



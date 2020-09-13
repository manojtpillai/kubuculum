
import subprocess
import time
from kubuculum.server_fio import server_fio
from kubuculum import util_functions

class fio_random:

    # p has params that override the defaults for this class
    def __init__ (self, p):

        self.params = { 
            'dir': '/tmp', # always overriden by caller
            'namespace': 'default', # always overriden by caller
            'ninstances': 1,
            'bs_kb': 8,
            'filesize_gb': 1,
            'numjobs': 1,
            'runtime_sec': 30,
            'scalefactor': 1.25,
            'extraspace_gb': 2,
            'templates_dir': 'templates',
            'prepare_template': 'fioprep.j2',
            'run_template': 'fiorun.j2'
        }
        self.params.update(p)

        #
        # derive parameters for fio server
        #

        # pass on basic parameters
        self.serverparams = { 
            'namespace': self.params['namespace'],
            'nservers': self.params['ninstances']
        }

        # specify output directory for callee
        self.serverparams['dir'] = self.params['dir'] + '/' + 'server_fio'

        # derive space requirements 
        if 'pvcsize_gb' in self.params:
            self.serverparams['pvcsize_gb'] = self.params['pvcsize_gb']
        else:
            pvcsize_gb = self.params['numjobs'] * self.params['filesize_gb']
            self.serverparams['pvcsize_gb'] = int (pvcsize_gb * \
                self.params['scalefactor'] + self.params['extraspace_gb'])

        # will use default storageclass, if not specified
        if 'storageclass' in self.params:
            self.serverparams['storageclass'] = self.params['storageclass']


    # prepare phase: create data set
    def prepare (self):

        # create directory for callee
        util_functions.create_dir (self.serverparams['dir'])

        self.serverhandle = server_fio.server_fio (self.serverparams)
        self.serverhandle.start ()

    # run phase : execute test on previously created data set
    def run (self):

        subprocess.run (["sleep", "60"])
        self.serverhandle.stop ()



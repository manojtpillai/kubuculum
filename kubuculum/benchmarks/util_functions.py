

from kubuculum.benchmarks.dummy_pause.dummy_pause import dummy_pause
from kubuculum.benchmarks.fio_random.fio_random import fio_random

def create_object (class_name, params):

    if class_name == 'dummy_pause':
        object_handle = dummy_pause (params)
    elif class_name == 'fio_random':
        object_handle = fio_random (params)

    return object_handle


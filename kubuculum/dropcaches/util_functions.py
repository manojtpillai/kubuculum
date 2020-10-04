

from kubuculum.os_commands.os_commands import os_commands

def create_object (class_name, run_dir, params_dict, globals):

    if class_name == 'os_commands':
        object_handle = os_commands (run_dir, params_dict, globals)

    # TODO: else handle error
    return object_handle


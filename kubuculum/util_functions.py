
import yaml
import subprocess
import time
import copy
from jinja2 import Environment, FileSystemLoader

# deep update of base_dict with new_dict
# base_dict and new_dict are possibly nested
# new_dict is unchanged
def deep_update (base_dict, new_dict):

    if not new_dict:
        return

    for new_key, new_value in new_dict.items ():
        if new_key in base_dict:
            base_value = base_dict.pop (new_key)
            if isinstance (new_value, dict) and isinstance (base_value, dict):
                deep_update (base_value, new_value)
                base_dict[new_key] = base_value
            else:
                base_dict[new_key] = new_value
        else:
            base_dict[new_key] = new_value


# extract module dictionary from a run dictionary
# label_list has elements on path to the module's dictionary
def get_modparams (run_params, label_list):

    mod_params = run_params
    for label in label_list:
        parent_params = mod_params
        if label in parent_params:
            mod_params = parent_params[label]
            if mod_params is None:
                mod_params = {}
                break
        else:
            mod_params = {}
            break

    # deepcopy not strictly required if callers are well behaved
    # using it to avoid hard-to-track bugs
    new_params = copy.deepcopy (mod_params)

    return new_params


# global_params has namespace and storageclass
def update_modparams (mod_params, global_params):

    for new_key, new_value in global_params.items ():
        if new_key not in mod_params:
            mod_params[new_key] = new_value
        # TODO: log a warning if namespace already in modparams


# instantiate jinja2 template to produce yaml
# uses entries in dict to render the template 
def instantiate_template (template_dir, template_file, dest_file, dict):

    file_loader = FileSystemLoader (template_dir)
    env = Environment (loader=file_loader, trim_blocks=True)
    template = env.get_template (template_file)

    rendered_yaml = template.render (dict)

    yaml_file = open (dest_file, 'w')
    print (rendered_yaml, file = yaml_file)
    yaml_file.close ()

# given a yaml file containing a dict, return the dict
def dict_from_file (filename):

    with open (filename, 'r') as yaml_input:
        params = yaml.safe_load (yaml_input)

    if params is None:
        params = {}

    return params

# given a dict, write it to a yaml file
def dict_to_file (dict, filename):

    with open (filename, 'w') as outfile:
        yaml.dump (dict, outfile, default_flow_style=False, sort_keys=False)

# create a subdirectory based on a tag and current time
def createdir_ts (path, tag):

    ts = str (time.time ())
    subdir = path + '/' + tag + ts

    subprocess.run (["mkdir", subdir])
    return subdir

# TODO: handle exception, if dir exists
# create a directory 
def create_dir (path):
    subprocess.run (["mkdir", path])

# TODO: handle exception, if subdir exists
# create a directory 
def create_subdir (parent, child):
    path = parent + '/' + child
    subprocess.run (["mkdir", path])

    return path

# pause for specified duration
def pause (pause_sec):
    subprocess.run (["sleep", str (pause_sec)])

# pause for specified duration
# supports keyboard interrupt to break out
def intr_pause (pause_sec):
    try:
        subprocess.run (["sleep", str (pause_sec)])
    except KeyboardInterrupt:
        pass



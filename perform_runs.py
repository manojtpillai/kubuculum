#!/usr/bin/env python3

import argparse
import yaml
from kubuculum.multirun_control import multirun_control

parser = argparse.ArgumentParser ()
parser.add_argument ("-i", "--input_file", help="name of yaml file with run parameters") 

args = parser.parse_args ()

if args.input_file:
    yaml_input = open (args.input_file)
    run_params = yaml.safe_load (yaml_input)
    yaml_input.close ()
else:
    run_params = {}

if run_params is None:
    run_params = {}

multirun_control.perform_runs (run_params)

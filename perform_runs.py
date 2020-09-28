#!/usr/bin/env python3

import argparse
import yaml
from kubuculum import process_and_execute

parser = argparse.ArgumentParser ()
parser.add_argument ("-i", "--input_file", help="name of yaml file with run parameters") 

args = parser.parse_args ()

if args.input_file:
    with open (args.input_file, "r") as yaml_input:
        run_params = yaml.safe_load (yaml_input)
    if run_params is None:
        run_params = {}
else:
    run_params = {}

process_and_execute.perform_runs (run_params)


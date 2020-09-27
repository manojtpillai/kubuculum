#!/usr/bin/env python3

import argparse
import os
from kubuculum import process_and_execute

parser = argparse.ArgumentParser ()
parser.add_argument ("-i", "--input_file", help="name of yaml file with run parameters") 

args = parser.parse_args ()

if args.input_file:
    abs_filename = os.path.abspath (args.input_file)
    process_and_execute.perform_runs (abs_filename)
else:
    process_and_execute.perform_runs ()


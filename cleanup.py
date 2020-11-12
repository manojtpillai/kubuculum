#!/usr/bin/env python3

import argparse
from kubuculum.setup_run import setup_run

parser = argparse. ArgumentParser()
parser.add_argument("-n", "--namespace", help="namespace to cleanup")

args = parser.parse_args()
default_namespace = "nm-kubuculum"

if args.namespace:
    environment_params = { 'namespace' : args.namespace }
else:
    environment_params = { 'namespace' : default_namespace }

callee_handle = setup_run.setup_run ("dummy", {}, environment_params)
callee_handle.cleanup()

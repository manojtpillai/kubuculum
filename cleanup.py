#!/usr/bin/env python3

import argparse
from kubuculum.setup import setup

parser = argparse. ArgumentParser()
parser.add_argument("-n", "--namespace", help="namespace to cleanup")

args = parser.parse_args()
default_namespace = "nm-kubuculum"

if args.namespace:
    environment_params = { 'namespace' : args.namespace }
else:
    environment_params = { 'namespace' : default_namespace }

callee_handle = setup.environs (environment_params)
callee_handle.cleanup()
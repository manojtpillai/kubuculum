#!/usr/bin/env python3

import argparse
from kubuculum.setup import setup

parser = argparse. ArgumentParser()
parser.add_argument("-n", "--namespace", help="namespace to cleanup")

args = parser.parse_args()
environment_params = { 'namespace' : args.namespace }

callee_handle = setup.environment (environment_params)
callee_handle.cleanup()

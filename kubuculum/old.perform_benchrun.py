#!/usr/bin/env python3

import sys
import getopt
import yaml

from benchmarks.dummy_pause.dummy_pause import dummy_pause

yaml_file = open('params.yaml')
myparams = yaml.safe_load(yaml_file)
yaml_file.close()

for test in myparams['benchmark_list']:

    bench_name = list(test.keys())[0]
    bench_params = test[bench_name]
    if bench_params == None:
        bench_params = {}

    if bench_name == 'dummy_pause':
        bench = dummy_pause(bench_params)

    bench.prepare()
    bench.run()


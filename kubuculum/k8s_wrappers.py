
import subprocess
import logging
from kubuculum import util_functions

logger = logging.getLogger (__name__)

# create pod(s) from yaml and wait till ready
def createpods_sync (namespace, yaml_file, label, expected_count, pause_sec, retries, timeout_sec):

    # create the pods
    createfrom_yaml (yaml_file, namespace)

    tried = 0
    while True:
        if pause_sec > 0 :
            util_functions.pause (pause_sec)

        # get list of pod names as bytes
        podlist_bytes = subprocess.check_output (["kubectl", "get", "pods", \
            "-l", label, "-n", namespace, "--no-headers", "-o=name"])

        # get podlist into the form [ "pod/podname-a", "pod/podname-b" ]
        podlist = podlist_bytes.decode('utf-8').strip('\n').split('\n')

        actual_count = len (podlist)
        if (expected_count == 0) or (actual_count == expected_count):
            break

        tried += 1
        if (retries == 0) or (tried == retries):
            break

        logger.debug (f'pod count: expected {expected_count} found {actual_count} on try {tried}; retrying ...')

    # TODO: handle error case: pod count != expected count

    # wait for pod to become ready
    timeout_string = "--timeout=" + str(timeout_sec) + "s"
    for pod in podlist:
        result = subprocess.run (["kubectl", "wait", \
            "--for=condition=Ready", pod, "-n", namespace, \
            timeout_string], stdout=subprocess.PIPE)
        logger.debug (f'{result}')


# create resources given yaml 
def createfrom_yaml (yaml_file, namespace=""):

    if namespace == "":
        result = subprocess.run (["kubectl", "create", "-f", \
            yaml_file], stdout=subprocess.PIPE)
    else:
        result = subprocess.run (["kubectl", "create", "-f", \
            yaml_file, "-n", namespace], stdout=subprocess.PIPE)
    logger.debug (f'{result}')

# delete resources given yaml 
def deletefrom_yaml (yaml_file, namespace=""):

    if namespace == "":
        result = subprocess.run (["kubectl", "delete", "-f", \
            yaml_file], stdout=subprocess.PIPE)
    else:
        result = subprocess.run (["kubectl", "delete", "-f", \
            yaml_file, "-n", namespace], stdout=subprocess.PIPE)
    logger.debug (f'{result}')

# delete resources given label
def deletefrom_label (namespace, label, resource_type):
    result = subprocess.run (["kubectl", "delete", resource_type, \
        "-l", label, "-n", namespace], stdout=subprocess.PIPE)
    logger.debug (f'{result}')

def create_namespace (namespace):
    result = subprocess.run (["kubectl", "create", "namespace", \
        namespace], stdout=subprocess.PIPE)
    logger.debug (f'{result}')

def delete_namespace (namespace):
    result = subprocess.run (["kubectl", "delete", "namespace", \
        namespace], stdout=subprocess.PIPE)
    logger.debug (f'{result}')


# get list of pods matching a label
# return value in the form [ "podname-a", "podname-b" ]
def get_podlist (namespace, label):

    # get list of pod names as bytes
    podlist_bytes = subprocess.check_output (["kubectl", "get", "pods", \
        "-l", label, "-n", namespace, \
        "--no-headers", "-o", "custom-columns=:metadata.name"])

    # get podlist into the form [ "podname-a", "podname-b" ]
    podlist = podlist_bytes.decode('utf-8').strip('\n').split('\n')

    return podlist

# copy from directory in pod(s)
# for each pod, creates directory with pod name to store contents
def copyfrompods (namespace, label, poddir, output_dir):

    podlist = get_podlist (namespace, label)

    for pod in podlist:
        src = namespace + "/" + pod + ":" + poddir
        dest = output_dir + "/" + pod

        util_functions.create_dir (dest)

        result = subprocess.run (["kubectl", "cp", src, dest], \
            stdout=subprocess.PIPE)
        logger.debug (f'{result}')

# execute a given command using kubectl-exec
def exec_command (command, pod, namespace):

    full_command = 'kubectl exec ' + pod + ' -n ' + namespace + ' -- ' + command
    result = subprocess.run ([full_command], stdout=subprocess.PIPE, \
        stderr=subprocess.STDOUT, shell=True)

    return result


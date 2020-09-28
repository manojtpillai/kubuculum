
import subprocess
from kubuculum import util_functions

# create pod(s) from yaml and wait till ready
def createpods_sync (namespace, yaml_file, label, expected_count, pause_sec, retries, timeout_sec):

    # create the pods
    subprocess.run (["kubectl", "create", "-f", yaml_file, "-n", \
        namespace])

    tried = 0
    while True:
        if pause_sec > 0 :
            util_functions.pause (pause_sec)

        # get list of pod names as bytes
        podlist_bytes = subprocess.check_output (["kubectl", "get", "pods", \
            "-l", label, "-n", namespace, "--no-headers", "-o=name"])

        # get podlist into the form [ "pod/podname-a", "pod/podname-b" ]
        podlist = podlist_bytes.decode('utf-8').strip('\n').split('\n')

        if (expected_count == 0) or (len (podlist) == expected_count):
            break

        tried += 1
        if (retries == 0) or (tried == retries):
            break

    # TODO: handle error case: pod count != expected count

    # wait for pod to become ready
    timeout_string = "--timeout=" + str(timeout_sec) + "s"
    for pod in podlist:
        subprocess.run (["kubectl", "wait", "--for=condition=Ready", \
            pod, "-n", namespace, timeout_string])


# delete resources given yaml 
def deletefrom_yaml (namespace, yaml_file):

    subprocess.run (["kubectl", "delete", "-f", yaml_file, "-n", \
        namespace])

# delete resources given label
def deletefrom_label (namespace, label, resource_type):

    subprocess.run (["kubectl", "delete", resource_type,  "-l", \
        label, "-n", namespace])

def create_namespace (namespace):
    subprocess.run (["kubectl", "create", "namespace", namespace])

def delete_namespace (namespace):
    subprocess.run (["kubectl", "delete", "namespace", namespace])


# copy from directory in pod(s)
# for each pod, creates directory with pod name to store contents
def copyfrompods (namespace, label, poddir, output_dir):

    # get list of pod names as bytes
    podlist_bytes = subprocess.check_output (["kubectl", "get", "pods", \
        "-l", label, "-n", namespace, \
        "--no-headers", "-o", "custom-columns=:metadata.name"])

    # get podlist into the form [ "podname-a", "podname-b" ]
    podlist = podlist_bytes.decode('utf-8').strip('\n').split('\n')

    for pod in podlist:
        src = namespace + "/" + pod + ":" + poddir
        dest = output_dir + "/" + pod

        util_functions.create_dir (dest)
        subprocess.run (["kubectl", "cp", src, dest])


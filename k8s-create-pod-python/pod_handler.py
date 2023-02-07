from kubernetes import client, config
import os
import argparse

k8s_endpoint = os.getenv('APISERVER')
bearer_token = os.getenv('TOKEN')

def init_client(k8s_endpoint, bearer_token):
    k8s_conf = client.Configuration()
    k8s_conf.host = k8s_endpoint
    k8s_conf.verify_ssl = False
    k8s_conf.api_key = {"authorization": "Bearer " + bearer_token}
    client.Configuration.set_default(k8s_conf)
    v1 = client.CoreV1Api()
    
    return v1

# def init_client():
#     # Configs can be set in Configuration class directly or using helper utility
#     config.load_kube_config()
#     v1 = client.CoreV1Api()
    
#     return v1

def list_pods(v1):
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch = False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# create busybox pod in default namespace
def create_pod(v1):
    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': 'busybox'
        },
        'spec': {
            'containers': [{
                'image': 'busybox',
                'name': 'sleep',
                "args": [
                    "/bin/sh",
                    "-c",
                    "while true;do date;sleep 5; done"
                ]
            }]
        }
    }
    resp = v1.create_namespaced_pod(body = pod_manifest, namespace = 'default')
    print(resp)

def delete_pod(v1):
    resp = v1.delete_namespaced_pod(
        name = 'busybox',
        namespace = "default")
    print(resp)
        

def main():
    v1 = init_client(k8s_endpoint, bearer_token)
    parser = argparse.ArgumentParser()
     
    parser.add_argument("options", help="Pick an option: list | create | delete")
    args = parser.parse_args()
    if args.options == 'list':
        list_pods(v1)
    elif args.options == 'create':
        create_pod(v1)
    elif args.options == 'delete':
        delete_pod(v1)
    else:
        print('You need to pick one of the options: list | create | delete')
if __name__ == '__main__':
    main()

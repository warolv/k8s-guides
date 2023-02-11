![k8s-create-pod-python](images/k8s-create-pod-python-tb.png)

https://youtu.be/tLKUH3HP0Lg

## Create Pod on Kubernetes using python

### Prerequisites: existing k8s cluster, using 'kind' in my case:
https://kind.sigs.k8s.io/docs/user/quick-start/#installation

Mac
```
brew install kind
```

Linux
```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.17.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### start kind k8s cluster
```bash
kind create cluster
kubectl cluster-info
```

### Create serviceAccount: 'python-api-sa'

```bash
kubectl -n default create serviceaccount python-api-sa
```

### Create secret for 'python-api-sa' SA:
Using version 1.24 -> need to create secret manually for SA

```bash
cat <<EoF > python-api-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: python-api-secret
  annotations:
    kubernetes.io/service-account.name: "python-api-sa"
type: kubernetes.io/service-account-token
data:
  extra: YmFyCg==
EoF

kubectl apply -f python-api-secret.yaml
```

### Give to 'python-api-sa' serviceAccount cluster admin permissions
```bash
kubectl create clusterrolebinding python-api-sa --clusterrole=cluster-admin --serviceaccount=default:python-api-sa
```

### Get Token

```bash
export TOKEN=$(kubectl get secret python-api-secret -o jsonpath='{.data.token}' | base64 -D)

export APISERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
```

### Python script Overview

```python
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
```

### List pods

```bash
pip install kubernetes
python pod_handler.py list
```

### Create busybox pod

```bash
pip install kubernetes
python pod_handler create
```

### Delete busybox pod

```bash
pip install kubernetes
python pod_handler delete
```

You can find code of pod_handler.py in k8s-create-pod-python folder.

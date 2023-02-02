## Playing with k8s API using cURL

### Prerequisites: existing k8s cluster, using 'EKS' in my case:


### Create serviceAccount: 'play-with-k8s-api'

```bash
kubectl -n default create serviceaccount play-with-k8s-api
```

### Create secret for 'play-with-k8s-api' SA:
Using version 1.24 -> need to create secret manually for SA

```bash
cat <<EoF > play-with-k8s-api-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: play-with-k8s-api-secret
  annotations:
    kubernetes.io/service-account.name: "play-with-k8s-api"
type: kubernetes.io/service-account-token
data:
  extra: YmFyCg==
EoF

kubectl apply -f play-with-k8s-api-secret.yaml
```

### Give to 'play-with-k8s-api' serviceAccount cluster admin permissions
```bash
kubectl create clusterrolebinding play-with-k8s-api --clusterrole=cluster-admin --serviceaccount=default:play-with-k8s-api
```

### Get Token

```bash
TOKEN=$(kubectl get secret play-with-k8s-api-secret -o jsonpath='{.data.token}' | base64 -D)

APISERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
```

### Get All Pods

```bash
curl -k \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Accept: application/json' \
    $APISERVER/api/v1/pods
```

### Create new Pod: 'busypod'

```bash
curl -k \
    -X POST \
    -d @- \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    $APISERVER/api/v1/namespaces/default/pods <<'EOF'
{
   "kind":"Pod",
   "apiVersion":"v1",
   "metadata":{
      "name":"busypod",
      "namespace":"default",
      "labels":{
         "name":"examplepod"
      }
   },
   "spec":{
      "containers":[
         {
            "name":"busybox",
            "image":"busybox",
            "command":["sleep", "3600"]
         }
      ]
   }
}
EOF
```

### Delete created Pod: 'busypod'

```bash
curl -k \
    -X DELETE \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Accept: application/json' \
    $APISERVER/api/v1/namespaces/default/pods/busypod
```

## Playing with k8s API

### Create serviceAccount: 'play-with-k8s-api'

```bash
kubectl -n default create serviceaccount play-with-k8s-api
```

### Give to 'play-with-k8s-api' serviceAccount cluster admin permissions
```bash
create clusterrolebinding play-with-k8s-api --clusterrole=cluster-admin --serviceaccount=default:play-with-k8s-api
```

### Get Token

```bash
TOKEN=$(kubectl get secret $(kubectl get serviceaccount play-with-k8s-api -n default -o jsonpath='{.secrets[0].name}') -n default -o jsonpath='{.data.token}' | base64 --decode )

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

### Create new Namespace: 'development'

```bash
curl -k \
    -X POST \
    -d @- \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    $APISERVER/api/v1/namespaces <<'EOF'
{
   "kind":"Namespace",
   "apiVersion":"v1",
   "metadata":{
      "name":"development"
   }
}
EOF
```


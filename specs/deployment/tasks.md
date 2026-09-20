# タスク一覧 - Kubernetes Deployment

- [x] APIサーバー用の `Dockerfile` を作成する (Req 1)
- [x] `calculator-api:local` イメージをローカルでビルドする (Req 1)
- [x] `k8s/namespace.yaml` を `specs/deployment/design.md` の内容に従って作成する (Req 2)
- [x] `k8s/deployment.yaml` を `specs/deployment/design.md` の内容に従って作成する(`namespace: calculator-api` を指定) (Req 1, 2, 3, 4, 5)
- [x] Docker Desktopの Kubernetes に `kubectl apply -f k8s/namespace.yaml` でNamespaceを作成する (Req 2)
- [x] `kubectl apply -f k8s/deployment.yaml` でDeploymentをデプロイする (Req 1)
- [x] `kubectl get pods -n calculator-api` でPodが `calculator-api` Namespace上に `1` レプリカで起動していることを確認する (Req 2, 3)
- [x] `kubectl port-forward -n calculator-api` 等でPodに接続し、4エンドポイントが応答することを確認する (Req 1)

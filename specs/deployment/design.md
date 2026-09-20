# 設計書 - Kubernetes Deployment

## Namespace

`k8s/namespace.yaml`(実装時に作成)

専用Namespace名は `calculator-api` とする(アプリ名と統一し、他リソースの命名と一貫性を持たせる)。

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: calculator-api
```

## マニフェスト

`k8s/deployment.yaml`(実装時に作成)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: calculator-api
  namespace: calculator-api
  labels:
    app: calculator-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: calculator-api
  template:
    metadata:
      labels:
        app: calculator-api
    spec:
      containers:
        - name: calculator-api
          image: calculator-api:local  # 実装時にDockerfileでビルドするイメージ名(暫定)
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              cpu: "100m"
              memory: "128Mi"
```

## 設計判断とその理由

| 項目 | 設定値 | 理由 |
|---|---|---|
| `Namespace` | `calculator-api` | 専用Namespaceで動作させる要件のため新設。`default`とは分離し、他リソースと同じ命名(`app: calculator-api`)に揃える。 |
| `spec.replicas` | `1` | リソース節約を最優先。冗長化は行わない。 |
| `livenessProbe` / `readinessProbe` | 設定しない | ヘルスチェックを最小構成(未設定)とする。専用のヘルスチェック用エンドポイント実装やプローブ実行によるリソース消費を避ける。 |
| `resources.requests` | cpu `50m` / memory `64Mi` | 4エンドポイントのみを持つ小規模なFastAPIアプリのため最小限で十分と想定。 |
| `resources.limits` | cpu `100m` / memory `128Mi` | 単一ノードのローカル環境で他プロセスを圧迫しないよう上限を低めに設定。 |
| `image` | `calculator-api:local`(暫定) | Dockerfileが未実装のため名称は仮。実装時に確定する。 |

## 前提

- コンテナは `apps/main.py` の FastAPI アプリをポート `8000` で待ち受ける想定(uvicornの起動コマンドはDockerfile側で定義)。
- `Service`/`Ingress`は用意しないため、動作確認時は `kubectl port-forward deployment/calculator-api 8000:8000 -n calculator-api` などで直接Podにアクセスする。
- `Namespace`は`Deployment`より先に作成する必要がある(`kubectl apply -f k8s/namespace.yaml` → `kubectl apply -f k8s/deployment.yaml` の順、または `kubectl apply -f k8s/` で同時適用)。
- ローカルPCの`8000`番ポートが別プロセス(別プロジェクトの`kubectl port-forward`など)に使用されている場合、`kubectl port-forward`のログが `Forwarding from [::1]:8000 -> 8000` の1行のみになり(`127.0.0.1:8000`側のbindに失敗)、`curl http://localhost:8000/...`がIPv4優先で別プロセスに接続してしまうことがある。この場合はログを確認のうえ、`kubectl port-forward -n calculator-api deployment/calculator-api 8001:8000` のようにローカル側のポートを変更してアクセスする。

## 将来の拡張(スコープ外・参考)

- 本番相当の運用に近づける場合は、`readinessProbe`(例: `tcpSocket` によるポート疎通確認)の追加、レプリカ数の増加、`Service`の追加を検討する。

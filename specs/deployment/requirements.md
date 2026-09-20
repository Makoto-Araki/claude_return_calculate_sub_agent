# 要件定義書 - Kubernetes Deployment

## 概要

四則演算APIサーバーを、ローカルPC上のDocker Desktopで有効化したKubernetes上で、`Deployment`リソースとして動作させる。リソース節約を最優先とし、ヘルスチェックとレプリカ数は最小構成とする。

## 前提とする実行環境

- Docker Desktopの「Kubernetesを有効化」機能で作成される、ローカル単一ノードのKubernetesクラスタ
- 本番運用ではなく、ローカルでの動作確認を目的とする

## 受け入れ基準 (EARS記法)

1. THE `Deployment`リソース SHALL ローカルPCのDocker Desktop上のKubernetesクラスタに`kubectl apply`でデプロイでき、Podが起動する。
2. THE `Deployment`リソース SHALL 専用の`Namespace`(`calculator-api`)上にデプロイし、`default`Namespaceは使用しない。
3. THE `Deployment`リソース SHALL レプリカ数(`spec.replicas`)を `1` に設定する(リソース節約を優先し、冗長構成は取らない)。
4. THE `Deployment`リソース SHALL `livenessProbe`・`readinessProbe`を設定しない(ヘルスチェックを最小=未設定とし、追加のリソース消費や実装(専用ヘルスチェックエンドポイント等)を避ける)。
5. THE コンテナ定義 SHALL CPU・メモリの`requests`/`limits`を必要最小限の値に設定し、リソース消費を抑える。

## スコープ外

- `Service` / `Ingress` などの外部公開用リソース(動作確認は `kubectl port-forward` 等で行う想定)
- オートスケーリング(HPA)
- `ConfigMap` / `Secret` によるアプリ設定の外部化
- 本番運用を想定した高可用性構成(複数レプリカ、ローリングアップデート戦略の調整など)

# 要件定義書 - CI (GitHub Actions)

## 概要

PR作成・`main`へのマージのたびに、lint・型チェック・ユニットテストを自動実行し、品質チェックを人手に頼らず行えるようにする。CD(Kubernetesへの実際のデプロイ)は、ローカルPCのDocker Desktop上のKubernetesが対象であり、CIランナーから到達できないため手動運用のままとし、本要件のスコープには含めない([`specs/deployment/`](../deployment/)を参照)。

## 背景・課題

- `tests/unit/`のテストや`specs/lint/`で導入したlint・型チェックは、現状ローカルで手動実行するのみで、PR作成時に自動で走らない。
- レビュー前に品質チェック漏れのPRがマージされるリスクがある。

## 受け入れ基準 (EARS記法)

1. WHEN `main`ブランチに対するPull Requestが作成・更新された場合、THEN GitHub ActionsがPR用のワークフローを自動実行する SHALL。
2. WHEN `main`ブランチにpush(マージ)された場合、THEN GitHub Actionsが`main`用のワークフローを自動実行し、マージ後の状態を検証する SHALL。
3. THE CI SHALL PR用(`pull_request`トリガー)と`main`用(`push`トリガー)を、それぞれ独立したワークフローファイルに分割する(1ファイルに両トリガーをまとめない)。
4. WHEN いずれかのワークフローが実行される場合、THEN `uv run ruff check .`・`uv run ruff format --check .`・`uv run mypy apps/`・`uv run pytest tests/unit/ -v` を(ローカル開発時と同じコマンドで)実行する SHALL。
5. WHEN いずれかのチェックが失敗した場合、THEN そのワークフローを失敗として終了させ、GitHub上に失敗が分かる形で表示する SHALL。
6. WHEN ワークフローが実行される場合、THEN `docker build` によるイメージビルドの成功確認も行う(イメージのpush・Kubernetesへのデプロイは行わない) SHALL。
7. THE CIワークフロー SHALL プロジェクトと同じPython 3.12系・`uv`を使用し、ローカル開発環境との差異を最小限にする。

## スコープ外

- Kubernetesへの自動デプロイ(CD)。デプロイは`specs/deployment/tasks.md`に従い手動で行う。
- コンテナレジストリへのイメージpush。
- GitHub側の「必須ステータスチェック」等のブランチ保護ルール設定(GitHubリポジトリ設定によるものであり、ワークフローファイルのスコープ外。必要であれば別途手動設定する)。
- テストカバレッジ計測・レポーティング。

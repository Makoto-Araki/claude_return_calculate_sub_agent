# タスク一覧 - CI (GitHub Actions)

- [x] `.github/workflows/ci-pull-request.yml` を `specs/ci/design.md` の内容に従って作成する(`pull_request` トリガー、`main`向け) (Req 1, 3, 4, 6, 7)
- [x] `.github/workflows/ci-main.yml` を `specs/ci/design.md` の内容に従って作成する(`push` トリガー、`main`向け) (Req 2, 3, 4, 6, 7)
- [x] 両ファイルの`test`ジョブ(ruff check / ruff format --check / mypy / pytest)を実装する (Req 4, 5)
- [x] 両ファイルの`docker-build`ジョブ(`docker build`のみ、push・デプロイなし)を実装する (Req 6)
- [x] PRを作成し、`ci-pull-request.yml`のみが自動実行されることを確認する (Req 1, 3)
- [x] `main`へマージ(push)した際に`ci-main.yml`のみが自動実行されることを確認する (Req 2, 3)
- [x] 意図的にlint/型チェック/テストのいずれかを失敗させ、ワークフローが失敗として表示されることを確認する (Req 5)
- [x] `CLAUDE.md`にCI導入済みである旨と、`ci-pull-request.yml`/`ci-main.yml`それぞれの役割を追記する (Req 1, 2, 3, 4, 6)
- [ ] (任意・手動) GitHubリポジトリ設定でブランチ保護ルールを有効化し、`ci-pull-request.yml`の`test`/`docker-build`を必須ステータスチェックに指定する

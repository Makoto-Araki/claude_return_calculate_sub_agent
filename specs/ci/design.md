# 設計書 - CI (GitHub Actions)

## ワークフローファイル構成

PR向けと`main`マージ向けを別ファイルに分割する。ジョブの中身(lint・型チェック・テスト・Dockerビルド)は共通だが、トリガーと用途が異なるため独立して管理する。

```
.github/workflows/
├── ci-pull-request.yml   # main向けPRの作成・更新時に実行
└── ci-main.yml           # mainへのpush(マージ)時に実行
```

### `.github/workflows/ci-pull-request.yml`

```yaml
name: CI (Pull Request)

on:
  pull_request:
    branches: [main]

concurrency:
  group: ci-pr-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v3
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync

      - name: Lint (ruff check)
        run: uv run ruff check .

      - name: Format check (ruff format)
        run: uv run ruff format --check .

      - name: Type check (mypy)
        run: uv run mypy apps/

      - name: Unit tests (pytest)
        run: uv run pytest tests/unit/ -v

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image (push・デプロイはしない)
        run: docker build -t calculator-api:ci .
```

### `.github/workflows/ci-main.yml`

```yaml
name: CI (main)

on:
  push:
    branches: [main]

concurrency:
  group: ci-main-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v3
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync

      - name: Lint (ruff check)
        run: uv run ruff check .

      - name: Format check (ruff format)
        run: uv run ruff format --check .

      - name: Type check (mypy)
        run: uv run mypy apps/

      - name: Unit tests (pytest)
        run: uv run pytest tests/unit/ -v

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image (push・デプロイはしない)
        run: docker build -t calculator-api:ci .
```

## 設計判断とその理由

| 項目 | 設定値 | 理由 |
|---|---|---|
| ファイル分割 | `ci-pull-request.yml` / `ci-main.yml` の2ファイル | PR用とmainマージ用で目的が異なるため分離し、GitHub ActionsのUI上でも実行契機ごとに区別しやすくする。将来どちらかだけ内容を変更・無効化したい場合も影響範囲を分離できる。 |
| ジョブ内容の重複 | 2ファイルにそれぞれ`test`/`docker-build`ジョブを記述(共通化しない) | 現時点ではジョブ数が少なく、`workflow_call`による再利用ワークフロー化は複雑さに見合わないため、まずは単純な複製とする。将来ジョブが増えて重複が問題になれば再利用ワークフローへの切り出しを検討する。 |
| トリガー | PR: `pull_request` (`main`向け) / main: `push` (`main`) | 要件通り、契機ごとに独立させる。 |
| `concurrency` | ワークフロー・ブランチ単位でキャンセル | 同じブランチへの連続pushで古い実行が残り続けないようにし、Actionsの実行時間を節約する。 |
| 依存セットアップ | `astral-sh/setup-uv` + `uv sync` | ローカル開発と同じ`uv`ベースの依存管理をCIでも使用し、環境差異をなくす。 |
| lint/型チェック/テストのコマンド | `CLAUDE.md`記載のローカルコマンドとそのまま同一 | ローカルで通る変更がCIでも同じ結果になることを保証し、コマンドの二重管理を避ける。 |
| `docker-build`ジョブ | `docker build`のみ実行し、push・デプロイはしない | Dockerfileの壊れを早期検知する一方、CD(Kubernetesへの反映)は`specs/deployment/`の方針通り手動のまま維持する。 |

## 前提・注意点

- ワークフローの成功をマージ条件として強制したい場合は、GitHubリポジトリ設定の「Branch protection rules」で`ci-pull-request.yml`のジョブを必須ステータスチェックに指定する必要がある(ワークフローファイル自体には強制力はない。設定はリポジトリ管理者が手動で行う)。
- `docker build`はDockerfile内の`uv sync --no-dev --no-editable`を含めて実行されるため、`pyproject.toml`/`uv.lock`の不整合もこのジョブで検知できる。

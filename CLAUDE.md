# CLAUDE.md

このファイルは、このリポジトリで作業するClaude Code (claude.ai/code) に向けたガイダンスを提供します。

## プロジェクトの現状

四則演算(`add`・`subtract`・`multiply`・`divide`)を行うAPIサーバーを、**サブエージェント(テストエージェント・実装エージェント・レビューエージェント)を使ったTDD**で開発するリポジトリです。**現時点では仕様ドキュメント(`specs/`)のみが存在し、実装コード・テスト・インフラ関連ファイルはすべて未着手です。**

`specs/`(add/subtract/multiply/divide/deployment/ci/lint)は、別リポジトリでTDDによりAPIサーバーを開発した際に作成した要件定義・設計ドキュメントを流用したものです。`requirements.md`・`design.md` は仕様源としてそのまま使います。各 `tasks.md` のチェックボックスは、本リポジトリでの実装状況を表すよう**すべて `[ ]`(未着手)にリセット済み**です。実際に完了した項目から順に `[x]` にしていくこと。

未着手のもの(作成予定):
- `apps/`(`schemas.py`・`main.py`・`routers/*.py`)、`pyproject.toml`(uv管理の依存定義、ruff・mypy設定を含む)
- `tests/unit/test_<operation>.py`
- `Dockerfile`・`k8s/`(`specs/deployment/`)
- CI(`.github/workflows/`、`specs/ci/`)、lint・型チェック設定(`specs/lint/`)
- サブエージェント定義(`.claude/agents/test-agent.md`・`implement-agent.md`・`review-agent.md`)

deployment・CI・lintは、4演算の実装が完了した後に導入する後続フェーズとして位置づける(それまでは仕様のみで、導入済みではない)。

`pyproject.toml` の作成後に使う主なコマンド([uv](https://docs.astral.sh/uv/)を使用):

```bash
uv sync                                    # 依存関係のインストール
uv run uvicorn apps.main:app --reload      # 開発サーバー起動
uv run pytest tests/unit/ -v               # ユニットテスト実行
uv run ruff check .                        # lint実行(lint導入後)
uv run ruff format --check .               # フォーマット差分チェック(適用しない。lint導入後)
uv run mypy apps/                          # 型チェック(appsディレクトリのみ対象。lint導入後)
```

## プロジェクトの目的

2個の**正の整数**パラメータに対して四則演算(加算・減算・乗算・除算)を行うシンプルなAPIサーバー。技術スタックは Python 3.12+、FastAPI、バリデーション用のPydantic v2、テスト用のpytest + httpx。

## specs/ の構成と使い方

各演算・機能は `specs/` 配下にそれぞれ独立したフィーチャーフォルダを持ち、requirements → design → tasks の3ファイル構成に従う。

```
specs/
├── add/
├── subtract/
├── multiply/
├── divide/
│   ├── requirements.md   # EARS記法(WHEN/THEN/SHALL)による受け入れ基準
│   ├── design.md         # エンドポイント仕様、Pydanticモデル、処理フロー、エラーハンドリング
│   └── tasks.md          # 実装チェックリスト。各項目は対応する要件番号を明記
├── deployment/
│   ├── requirements.md   # Kubernetes Deploymentリソースの要件
│   ├── design.md         # Deploymentマニフェストの内容と設計判断の理由
│   └── tasks.md          # Dockerfile作成〜デプロイ確認までのタスク
├── ci/                   # GitHub Actionsの要件・設計・タスク
└── lint/                 # ruff・mypyの要件・設計・タスク
```

`requirements.md`・`design.md` は仕様源として使う(設計をやり直す必要はない)。`tasks.md` は要件の網羅リストであり、完了した項目のみ `[x]` にする。新しい演算・機能を追加する場合も、同様に `specs/<feature>/` に同じ3ファイル構成を作成してこの形式を維持すること。

## サブエージェントによるTDDの進め方

実装は、次の3つのサブエージェントを使い、**演算ごとに1サイクル**で進める。サブエージェントは `.claude/agents/` 配下に定義する。

| エージェント | 定義ファイル | 役割 | 書き込み対象 |
|---|---|---|---|
| テストエージェント | `test-agent.md` | `specs/<operation>/` の仕様と `tasks.md` のテストケース一覧から、ユニットテストを実装する | `tests/unit/test_<operation>.py` のみ |
| 実装エージェント | `implement-agent.md` | 仕様ドキュメントとテストコードを確認し、テストがGreenになるよう `apps/` を実装する | `apps/` のみ(テストは変更しない) |
| レビューエージェント | `review-agent.md` | 仕様ドキュメント・テストコード・実装コードを突き合わせ、矛盾や実装の過不足を確認する | なし(読み取り専用。指摘の報告のみ) |

### 1サイクルの流れ

サブエージェントは他のサブエージェントを起動できないため、各エージェントの呼び出し順序と、各段階の確認・判断は**メインのClaude(オーケストレーター)が担う**。

1. **テスト作成(Red)**: テストエージェントに `specs/<operation>/` を渡し、`tests/unit/test_<operation>.py` を実装させる。メインのClaudeが `uv run pytest tests/unit/ -v` を実行し、**テストが失敗している(Red)ことを確認**してから次に進む。テストが通ってしまう場合や、実装不足以外の理由(構文エラー等)で失敗している場合は、実装に進まずテストエージェントに修正させる。
2. **実装(Green)**: 実装エージェントに、仕様ドキュメントとテストコードを確認させたうえで `apps/` を実装させる。メインのClaudeが `uv run pytest tests/unit/ -v` を実行し、**全テストがGreenであることを確認**する。lint・型チェックが導入済みであれば、`ruff check`・`ruff format --check`・`mypy apps/` も通ることを確認する。
3. **レビュー**: レビューエージェントに、仕様ドキュメント・テストコード・実装コードを確認させ、仕様・テスト・実装の間の矛盾、および実装の過不足(仕様にない機能の追加、仕様の未実装、テストで検証されていない要件)を報告させる。
4. **指摘への対応**: 指摘があれば、内容に応じてテストエージェントまたは実装エージェントに戻して修正し、Red/Greenの確認とレビューをやり直す。指摘がなければ次に進む。
5. **完了**: `specs/<operation>/tasks.md` の該当項目を `[x]` にし、コミット・push・PR作成を行う。

### 守るべきルール

- 進め方の単位は**演算ごとに1サイクル**とし、1つの演算のPRがマージされてから次の演算に進む。4演算分のテストや実装をまとめて先に書く方式は採らない。
- テストは実装より**必ず先**に書く。Redを確認する前に実装エージェントを呼ばないこと。
- 実装エージェントはテストを書き換えて通してはならない。テストが仕様と矛盾していると考える場合は、修正せず報告し、メインのClaudeの判断を仰ぐこと。
- テストエージェントは `apps/` を、実装エージェントは `tests/` を変更しないこと(役割の分離)。
- `specs/<operation>/tasks.md` の記載順(スキーマ定義→ハンドラ実装→テスト実装)は要件の網羅リストとして参照し、実際の着手順序はテスト実装を先に行う。
- テスト関数を含むすべての関数には[Docstringの方針](#docstringの方針)に従いNumPyスタイルのdocstringを付与すること。
- テストケースは各 `specs/<operation>/tasks.md` に列挙された正常系・異常系の項目を網羅すること。

## 4演算に共通する主要な設計判断

- 全エンドポイントは `POST /calculate/<operation>` で、JSONボディ `{"a": integer, "b": integer}` を受け取り、成功時は `{"operation", "a", "b", "result"}` を返す。
- `a`/`b` は**正の整数(> 0)のみ**を許容する(Pydanticの `PositiveInt` を使用)。`0`・負数・小数・非数値・欠落はすべてFastAPI/Pydantic標準の `422` レスポンスに委ねる。独自のバリデーションを実装しないこと。
- `divide` の `b == 0` も上記の正の整数バリデーションで弾かれるため、ゼロ除算専用の `400` エラーハンドリングは実装しない(`ZeroDivisionError` が発生する経路自体が存在しない)。
- 認証・永続化・CORSはスコープ外。

## 実行環境(Kubernetes)に関する設計判断

詳細は [`specs/deployment/`](specs/deployment/) を参照。**未導入**(仕様のみ。4演算の実装完了後に導入する)。

- ローカルPCのDocker Desktopで有効化したKubernetes上に、専用Namespace `calculator-api` 配下で `Deployment`リソースとしてデプロイする(本番運用は想定しない)。`default` Namespaceは使用しない。
- リソース節約を最優先するため、レプリカ数は `1`、`livenessProbe`/`readinessProbe`は設定しない、CPU/メモリの`requests`/`limits`は最小限、という最小構成を維持すること。
- `Service`/`Ingress`・オートスケーリングなどはスコープ外。追加する場合は要件から見直すこと。
- 導入後に演算を追加した際は、`Dockerfile`・`k8s/`マニフェストは変更不要だが、イメージの再ビルド・再デプロイと全演算での動作再確認が必要。

## CI(GitHub Actions)に関する設計判断

詳細は [`specs/ci/`](specs/ci/) を参照。**未導入**(仕様のみ。lint・型チェックの導入後に導入する)。

- `.github/workflows/ci-pull-request.yml`: `main`向けPRの作成・更新時(`pull_request`トリガー)に実行。
- `.github/workflows/ci-main.yml`: `main`へのpush(マージ)時(`push`トリガー)に実行。
- 両ファイルとも`test`ジョブ(`uv run ruff check .`・`uv run ruff format --check .`・`uv run mypy apps/`・`uv run pytest tests/unit/ -v`)と`docker-build`ジョブ(`docker build`のみ、push・デプロイなし)を持つ。
- Kubernetesへの自動デプロイ(CD)・イメージのレジストリpushはスコープ外(`specs/deployment/`に従い手動運用)。

## lint・型チェックに関する設計判断

詳細は [`specs/lint/`](specs/lint/) を参照。**未導入**(仕様のみ)。ruff(lint・フォーマットチェック)とmypy(`apps/`のみ対象)を `pyproject.toml` に設定する。

## 実装時のディレクトリ構成

アプリケーションコードは `app/` ではなく **`apps/`** ディレクトリ配下に実装すること(各 `specs/<operation>/tasks.md` のファイルパスもこれに合わせて記載済み)。`apps/routers/` は `tests/unit/` と同様に**演算ごとにファイルを分割**し、1ファイルに複数演算のハンドラをまとめないこと。

```
.claude/
└── agents/
    ├── test-agent.md
    ├── implement-agent.md
    └── review-agent.md
apps/
├── main.py            # FastAPIアプリ、各ルーターの登録
├── routers/
│   ├── add.py         # POST /calculate/add
│   ├── subtract.py    # POST /calculate/subtract
│   ├── multiply.py    # POST /calculate/multiply
│   └── divide.py      # POST /calculate/divide
└── schemas.py         # Pydanticモデル(リクエスト/レスポンス)
tests/
└── unit/
    ├── test_add.py
    ├── test_subtract.py
    ├── test_multiply.py
    └── test_divide.py
Dockerfile
k8s/
├── namespace.yaml      # 専用Namespace "calculator-api" を定義
└── deployment.yaml     # namespace: calculator-api を指定。specs/deployment/design.md の内容に従う
```

## Docstringの方針

関数・メソッドにはNumPyスタイルのdocstringを付与すること(`Parameters` / `Returns` セクションを`----`の下線で区切る形式)。

```python
def add(a: int, b: int) -> int:
    """2つの整数を加算する。

    Parameters
    ----------
    a : int
        被加数。
    b : int
        加数。

    Returns
    -------
    int
        a + b の結果。
    """
```

## PR作成時の言語

PRのタイトル・本文は日本語で記述すること。

## PR作成の粒度

キリの良い作業単位(1機能・1ドキュメント更新など)が完了するたびに、こまめにコミット・push・PR作成を行うこと。複数の無関係な変更を1つの大きなPRにまとめて溜め込まないこと。このリポジトリはPRがマージされるとブランチが自動削除されるため、新たな作業を始める前には必ず `git fetch origin` して `main` を最新化し、そこから新しいブランチを切ること。

四則演算の実装では、[サブエージェントによるTDDの進め方](#サブエージェントによるtddの進め方)に記載の「演算ごとに1サイクル」が最小のPR単位となる。1つの演算のテスト・実装・レビューが完了しPRがマージされてから、次の演算のブランチを切ること。

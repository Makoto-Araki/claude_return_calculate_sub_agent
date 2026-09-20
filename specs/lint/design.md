# 設計書 - Lint・型チェック

## 採用ツール

| 用途 | ツール | 理由 |
|---|---|---|
| Lint / import整理 / フォーマットチェック | [ruff](https://docs.astral.sh/ruff/) | 単一ツールでlint・import順序チェック・フォーマットまで完結し高速。Rust製で追加のランタイム依存が軽い。 |
| 型チェック | [mypy](https://mypy-lang.org/) | Pydantic v2公式の`pydantic.mypy`プラグインがあり、`BaseModel`のフィールド型を正しく検査できる。FastAPIエコシステムでの採用実績も豊富。 |

## `pyproject.toml` への追加

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]  # pycodestyle, pyflakes, isort, pyupgrade

[tool.mypy]
python_version = "3.12"
plugins = ["pydantic.mypy"]
strict = true
```

## 実行コマンド

```bash
uv run ruff check .              # lint実行
uv run ruff check . --fix        # 自動修正可能な指摘を修正
uv run ruff format --check .     # フォーマット差分チェック(適用しない)
uv run mypy apps/                # 型チェック(appsディレクトリのみ対象)
```

## 対象ディレクトリ

- lint (`ruff check`): `apps/`, `tests/`(テストコードも対象に含め、規約を統一する)
- 型チェック (`mypy`): `apps/` のみ(`tests/`はpytestのfixtureやパラメタライズ記法でmypyとの相性が悪いケースがあるため、初期導入時は対象外とする)
- `ruff format --check .` は `specs/*.md` 内のPythonコードブロックも整形対象に含めてしまうため、`[tool.ruff]` に `extend-exclude = ["specs"]` を設定し、`specs/` を対象外とする(設計ドキュメント内のコード例は実行対象のソースコードではないため)。

## 処理フロー(開発者の運用)

1. 実装・修正後、コミット前に `uv run ruff check .` と `uv run mypy apps/` をローカルで実行する。
2. 指摘があれば修正するか、`ruff check . --fix` で自動修正できるものは反映する。
3. 現時点ではCI・pre-commitフックによる強制はせず、手動運用とする(スコープ外の項目は`requirements.md`を参照)。

## 導入時の対応

- 既存の `apps/`・`tests/` 配下のコードに対して初回のlint・型チェックを実行し、指摘があれば本実装作業の中で修正する。

# タスク一覧 - Lint・型チェック

- [ ] `pyproject.toml` の `dependency-groups.dev` に `ruff`・`mypy` を追加する (Req 3)
- [ ] `pyproject.toml` に `[tool.ruff]` / `[tool.ruff.lint]` 設定を追加する (Req 1, 4)
- [ ] `pyproject.toml` に `[tool.mypy]` 設定(`pydantic.mypy`プラグイン含む)を追加する (Req 2, 4)
- [ ] `uv sync` で追加した開発依存が導入されることを確認する (Req 3)
- [ ] `uv run ruff check .` を実行し、既存の `apps/`・`tests/` の指摘事項を修正する (Req 1, 5)
- [ ] `uv run mypy apps/` を実行し、既存の `apps/` の指摘事項を修正する (Req 2, 5)
- [ ] `CLAUDE.md` の「主なコマンド」にlint・型チェックの実行コマンドを追記する (Req 1, 2)

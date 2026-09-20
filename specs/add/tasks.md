# タスク一覧 - 加算 (add)

- [x] `AddRequest`(`a`, `b` を `PositiveInt`)スキーマを `apps/schemas.py` に定義する (Req 1, 2)
  - 共用の `CalculationResponse` は共通の土台(`apps/schemas.py`)で定義済み。
- [x] `apps/routers/add.py` に `POST /calculate/add` ハンドラを実装する (Req 1)
- [x] `tests/unit/test_add.py` にユニットテストコードを実装する (Req 1, 2)
  - [x] 正常系テスト: 正の整数同士の加算 (Req 1)
  - [x] 異常系テスト: `a`/`b` が `0` の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が負数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が小数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が数値でない場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が欠落している場合に422が返る (Req 2)

# タスク一覧 - 除算 (divide)

- [x] `DivideRequest`(`a`, `b` を `PositiveInt`)/ `DivideResponse`(`result` は `float`)スキーマを `apps/schemas.py` に定義する (Req 1, 2)
  - 既存の共有 `CalculationResponse`(`result: int`)を `add`/`subtract`/`multiply` と共用しているため、`result: float` は専用の `DivideResponse` として新設した(共有モデルを `float` に変更すると既存演算のレスポンス形式が変わってしまうため)。
- [x] `apps/routers/divide.py` に `POST /calculate/divide` ハンドラを実装する(商がfloatの範囲を超える `OverflowError` は捕捉して422を返す) (Req 1, 4)
- [x] `tests/unit/test_divide.py` にユニットテストコードを実装する (Req 1, 2, 3, 4)
  - [x] 正常系テスト: 割り切れる正の整数同士の除算 (Req 1)
  - [x] 正常系テスト: 割り切れず結果が小数になるケース (Req 3)
  - [x] 異常系テスト: `b` が `0` の場合に422が返る(独自の400エラーは実装しない) (Req 2)
  - [x] 異常系テスト: `a`/`b` が負数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が小数の場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が数値でない場合に422が返る (Req 2)
  - [x] 異常系テスト: `a`/`b` が欠落している場合に422が返る (Req 2)
  - [x] 異常系テスト: 商がfloatの範囲を超える場合(例: `a = 10**400`, `b = 1`)に500ではなく422が返る (Req 4)

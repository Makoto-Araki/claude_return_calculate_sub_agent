# 設計書 - 除算 (divide)

## エンドポイント

`POST /calculate/divide`

## リクエスト

```json
{
  "a": 10,
  "b": 3
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
|---|---|---|---|---|
| a | integer | ○ | 正の整数(> 0) | 被除数 |
| b | integer | ○ | 正の整数(> 0) | 除数 |

## レスポンス

### 成功時 (200 OK)

```json
{
  "operation": "divide",
  "a": 10,
  "b": 3,
  "result": 3.3333333333333335
}
```

### 異常時 (422)

`a`/`b` が正の整数でない(型不正・欠落・小数・`0`・負数)場合、FastAPI/Pydantic標準のバリデーションエラーレスポンスをそのまま返す。`b` を `0` として送信した場合もこの `422` に含まれ、独自の `400` エラーは設けない。

`a`/`b` が正の整数であっても、商 `a / b` がfloatで表現できる範囲を超える場合(例: `a = 10**400`, `b = 1`)は、`OverflowError` を捕捉して `422` を返す(`500` にしない)。

## データモデル (Pydantic)

```python
from pydantic import BaseModel, PositiveInt

class DivideRequest(BaseModel):
    a: PositiveInt
    b: PositiveInt

class DivideResponse(BaseModel):
    operation: str
    a: int
    b: int
    result: float
```

共用の `CalculationResponse`(`result: int`)は `add`/`subtract`/`multiply` と共用しているため、`result` が `float` となる除算には専用の `DivideResponse` を用いる(共用モデルを `float` に変更すると、既存演算のレスポンス形式が変わってしまうため)。

## 処理フロー

1. リクエストボディを `DivideRequest` でバリデーション(`PositiveInt` により `0`・負数・小数・非数値を自動的に拒否。これにより `b` が `0` になるケースもこの時点で弾かれる)
2. `result = a / b` を計算(Python 3の `/` 演算子により常にfloatで結果が得られる)。商がfloatの範囲を超えて `OverflowError` となった場合は `422` を返す
3. `DivideResponse` を組み立てて返却

## エラーハンドリング

- `b == 0` によるゼロ除算は、入力バリデーションの段階で `PositiveInt` により排除されるため、ハンドラ内で例外処理を行う必要はない。
- `a / b` の商がfloatで表現できる範囲を超えた場合は `OverflowError` が発生するため、ハンドラ内で捕捉して `HTTPException(status_code=422)` として返す。これが除算における唯一の例外処理である。
- 入力バリデーションエラー(`0`・負数・小数・非数値・欠落を含む)はすべてFastAPIのデフォルト例外ハンドラに委譲し、`422`として返す。

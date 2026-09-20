# 設計書 - 減算 (subtract)

## エンドポイント

`POST /calculate/subtract`

## リクエスト

```json
{
  "a": 10,
  "b": 3
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
|---|---|---|---|---|
| a | integer | ○ | 正の整数(> 0) | 被減数 |
| b | integer | ○ | 正の整数(> 0) | 減数 |

## レスポンス

### 成功時 (200 OK)

```json
{
  "operation": "subtract",
  "a": 10,
  "b": 3,
  "result": 7
}
```

負の結果になる例(`a=3, b=10`):

```json
{
  "operation": "subtract",
  "a": 3,
  "b": 10,
  "result": -7
}
```

### 異常時 (422)

`a`/`b` が正の整数でない(型不正・欠落・小数・`0`・負数)場合、FastAPI/Pydantic標準のバリデーションエラーレスポンスをそのまま返す。

## データモデル (Pydantic)

```python
from pydantic import BaseModel, PositiveInt

class SubtractRequest(BaseModel):
    a: PositiveInt
    b: PositiveInt

class CalculationResponse(BaseModel):
    operation: str
    a: int
    b: int
    result: int
```

## 処理フロー

1. リクエストボディを `SubtractRequest` でバリデーション(`PositiveInt` により `0`・負数・小数・非数値を自動的に拒否)
2. `result = a - b` を計算(結果自体は負数になり得る)
3. `CalculationResponse` を組み立てて返却

## エラーハンドリング

- 減算処理自体で例外は発生しない想定。
- 入力バリデーションエラー(`0`・負数・小数・非数値・欠落を含む)はすべてFastAPIのデフォルト例外ハンドラに委譲し、`422`として返す。

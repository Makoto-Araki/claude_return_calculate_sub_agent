# 設計書 - 加算 (add)

## エンドポイント

`POST /calculate/add`

## リクエスト

```json
{
  "a": 10,
  "b": 3
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
|---|---|---|---|---|
| a | integer | ○ | 正の整数(> 0) | 被加数 |
| b | integer | ○ | 正の整数(> 0) | 加数 |

## レスポンス

### 成功時 (200 OK)

```json
{
  "operation": "add",
  "a": 10,
  "b": 3,
  "result": 13
}
```

### 異常時 (422)

`a`/`b` が正の整数でない(型不正・欠落・小数・`0`・負数)場合、FastAPI/Pydantic標準のバリデーションエラーレスポンスをそのまま返す。

## データモデル (Pydantic)

```python
from pydantic import BaseModel, PositiveInt

class AddRequest(BaseModel):
    a: PositiveInt
    b: PositiveInt

class CalculationResponse(BaseModel):
    operation: str
    a: int
    b: int
    result: int
```

## 処理フロー

1. リクエストボディを `AddRequest` でバリデーション(`PositiveInt` により `0`・負数・小数・非数値を自動的に拒否)
2. `result = a + b` を計算
3. `CalculationResponse` を組み立てて返却

## エラーハンドリング

- 加算処理自体で例外は発生しない想定(バリデーション済みの正の整数同士の加算)。
- 入力バリデーションエラー(`0`・負数・小数・非数値・欠落を含む)はすべてFastAPIのデフォルト例外ハンドラに委譲し、`422`として返す。

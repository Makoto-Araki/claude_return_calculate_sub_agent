# 設計書 - エラーレスポンスの整形 (error-handling)

## 対象

全エンドポイント(`POST /calculate/add`・`/subtract`・`/multiply`・`/divide`)に共通。実装は演算ごとのルーターではなく、`apps/main.py` の FastAPI アプリに登録する例外ハンドラ1つとする。

## 原因

```
リクエスト {"a": NaN, "b": 2}
  → Pydantic が PositiveInt の検証で finite_number エラー(正しく拒否)
  → FastAPI 標準ハンドラが {"detail": jsonable_encoder(exc.errors())} を生成
  → errors の "input" が nan のため、JSONへの変換で ValueError
  → 500
```

FastAPI 標準の `request_validation_exception_handler` は次のとおりである。

```python
async def request_validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})
```

## 設計

`RequestValidationError` に対する例外ハンドラを `apps/main.py` に登録し、標準ハンドラと同じ処理に「非有限のfloatの文字列化」を挟む。

```python
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = _replace_non_finite(exc.errors())
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})
```

`_replace_non_finite(value)` は、値を再帰的に走査するヘルパー関数である。

| 値 | 返り値 |
|---|---|
| 非有限のfloat(`NaN`・`Infinity`・`-Infinity`) | `str(value)`(`"nan"`・`"inf"`・`"-inf"`) |
| `dict` | 各値を再帰的に置換した新しい `dict`(キーは変更しない) |
| `list`・`tuple` | 各要素を再帰的に置換した `list` |
| 上記以外 | そのまま返す |

- 置換するのは非有限のfloatだけで、エラーの構造・`type`・`loc`・`msg`・他の値は標準のまま変わらない。
- 非有限のfloatが `a`・`b` の値そのもの、ネストした値(例: `{"a": [NaN]}`)、ボディ全体(例: `[NaN]`、`NaN`)のいずれにあっても、エラー詳細の `input` 内で置換される。
- `1e400` のようなfloatの範囲を超えるJSON数値は、パーサが `Infinity` として扱うため、同じ経路で置換される。

## エラーハンドリング

- 検証そのものは引き続き Pydantic に委ねる。このハンドラはエラーレスポンスの**整形のみ**を行い、新たな検証・拒否の条件を追加しない(「独自のバリデーションを実装しない」方針に反しない)。
- 非有限のfloatを含まない検証エラーは、標準ハンドラと同じ内容(`input` を含む)の `422` を返す。
- 検証エラー以外の例外(`HTTPException` など)には影響しない。

## 設計判断とその理由

| 項目 | 設計 | 理由 |
|---|---|---|
| 置き場所 | `apps/main.py` の例外ハンドラ1つ | 4演算に共通の問題であり、ルーターごとに処理を持たせると重複・漏れが生じる。 |
| 置換方法 | 非有限のfloatのみを文字列化 | `input` を全エラーから除く案は、既存の正常な `422` の本文まで変わり、クライアントに影響しうるため採らない。 |
| 走査の範囲 | エラー詳細全体を再帰的に走査 | 非有限のfloatが、ネストした値やボディ全体に含まれても `500` になるため(実測で確認済み)。 |
| 文字列表現 | `str(float)`(`"nan"`・`"inf"`・`"-inf"`) | 追加の定義が不要で、結果が一意に決まる。 |
| ミドルウェアでの事前拒否 | 採らない | 入力の独自検査になり、「検証はPydanticに委ねる」方針から外れる。 |
| 深いネストへの対応 | 行わない(再帰のまま) | 標準ハンドラが使う `jsonable_encoder` も再帰で、約1000段前後で同じく失敗する(実測)。走査を反復に置き換えても解消せず、`RecursionError` を捕捉して固定の `422` を返す案は、標準の詳細形式(Req 3)や「整形のみ」の方針から外れる。スコープ外とする。 |

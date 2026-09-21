# 要件定義書 - エラーレスポンスの整形 (error-handling)

## 概要

4つの演算エンドポイント(`add`・`subtract`・`multiply`・`divide`)に共通する機能として、リクエストボディに非有限の数値(`NaN`・`Infinity`・`-Infinity`、およびfloatの範囲を超えるJSON数値)が含まれる場合に、`500 Internal Server Error` ではなく `422 Unprocessable Entity` を返せるようにする。

## 背景・課題

- `a`・`b` は `PositiveInt` により検証され、非有限の数値は Pydantic が `finite_number` エラーとして正しく拒否する。
- しかし、FastAPI 標準の検証エラーハンドラは、エラー詳細に入力値(`"input"`)をそのまま含めてJSONに変換する。入力値が `NaN`・`Infinity` の場合はJSONにできず(`ValueError: Out of range float values are not JSON compliant`)、レスポンスの生成に失敗して `500` になる。
- Python の JSON パーサは、標準のJSONにない `NaN`・`Infinity`・`-Infinity` を受け付ける。また `1e400` のようなfloatの範囲を超える数値は `Infinity` として扱われる。
- 問題は入力の検証ではなく、エラーレスポンスの組み立てにある。4演算すべてで同じ挙動のため、演算ごとの仕様ではなく共通機能として扱う。

## 受け入れ基準 (EARS記法)

1. WHEN `POST /calculate/add`・`/subtract`・`/multiply`・`/divide` のいずれかのリクエストボディの `a` または `b` に、非有限のfloat(`NaN`・`Infinity`・`-Infinity`、およびfloatの範囲を超えるJSON数値 `1e400`・`-1e400`)が含まれる場合、THEN システムは `422 Unprocessable Entity` を返す SHALL(`500` としてはならない)。
2. WHEN 非有限のfloatが、`a`・`b` の値そのものではなく、`a`・`b` のネストした値(配列・オブジェクトの要素)、リクエストボディ全体(ボディ自体が `NaN`・`Infinity`・`[NaN]` などである場合)、または他の検証エラー(例: `b` の欠落)と同時に発生する場合も、THEN システムは `422 Unprocessable Entity` を返す SHALL。
3. THE `422` レスポンス SHALL FastAPI 標準と同じ形式(`{"detail": [{"type", "loc", "msg", "input", ...}]}`)とする。エラー詳細に含まれる非有限のfloatのみを文字列(`NaN` → `"nan"`、`Infinity` → `"inf"`、`-Infinity` → `"-inf"`)に置換し、それ以外の値・フィールドは変更しない。
4. WHEN 非有限のfloatを含まない不正なリクエスト(`0`・負数・小数・数値でない値・欠落)が送信された場合、THEN システムは従来どおり FastAPI 標準の `422` レスポンス(`input` の値を含む)を、変更なく返す SHALL。
5. WHEN 有効なリクエスト(正の整数の `a`・`b`)が送信された場合、THEN システムは従来と同じレスポンスを返す SHALL(既存の演算の振る舞いに影響しない)。

## スコープ外

- 入力の検証そのものの追加・変更(`a`・`b` の検証は引き続き Pydantic の `PositiveInt` に委ねる。独自のバリデーションは実装しない)。
- 4301桁以上の整数を送った場合の `400`(FastAPI 標準のJSONパースエラー)の扱い。
- `5.0`・`"5"`・`true` など、Pydantic の lax モードで整数として受理される値の扱い。
- `divide` の商が `0.0` に丸まる場合(下限側)の扱い。
- 422 以外のエラーレスポンスの整形。
- `a`・`b` が有効な正の整数で、それ以外のキー(余分なキー)にのみ非有限のfloatが含まれる場合(例: `{"a": 1, "b": 2, "c": NaN}`)。Pydantic は未知のフィールドを無視し、検証エラーが起きないため、従来どおり `200` を返す(本機能の対象は検証エラーのレスポンスの整形であり、この挙動は変更しない)。
- 極端に深いネスト(約1000段前後を超える配列・オブジェクト)。FastAPI/Pydantic の再帰の深さの上限に由来する既存の挙動で、標準のハンドラのみの場合も同じ深さで `500` になる(それ以上に深い場合は、JSONパーサの標準の `400` になる)。

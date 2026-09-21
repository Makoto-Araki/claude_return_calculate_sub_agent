"""4演算エンドポイント共通のエラーレスポンス整形 (error-handling) のユニットテスト。"""

import pytest
from fastapi.testclient import TestClient

from apps.main import app

ENDPOINTS = [
    pytest.param("/calculate/add", id="add"),
    pytest.param("/calculate/subtract", id="subtract"),
    pytest.param("/calculate/multiply", id="multiply"),
    pytest.param("/calculate/divide", id="divide"),
]
VALID_VALUE = 5
JSON_HEADERS = {"content-type": "application/json"}

# 標準のJSONにない非有限の数値リテラルと、エラー詳細で置換された後の文字列。
# floatの範囲を超える 1e400・-1e400 は、パーサが Infinity・-Infinity として扱う。
NON_FINITE_LITERALS = [
    pytest.param("NaN", "nan", id="nan"),
    pytest.param("Infinity", "inf", id="infinity"),
    pytest.param("-Infinity", "-inf", id="negative-infinity"),
    pytest.param("1e400", "inf", id="overflow-positive"),
    pytest.param("-1e400", "-inf", id="overflow-negative"),
]

# 非有限のfloatが a・b の値そのものだった場合の、Pydantic標準の検証エラー1件。
FINITE_NUMBER_MSG = "Input should be a finite number"


def finite_number_error(field: str, replaced_input: str) -> dict[str, object]:
    """非有限のfloatが `a` または `b` の値そのものだった場合の期待エラー詳細を組み立てる。

    Parameters
    ----------
    field : str
        エラーとなったフィールド名(`a` または `b`)。
    replaced_input : str
        `input` に入っているはずの、置換後の文字列(`"nan"`・`"inf"`・`"-inf"`)。

    Returns
    -------
    dict[str, object]
        期待するエラー詳細1件。
    """
    return {
        "type": "finite_number",
        "loc": ["body", field],
        "msg": FINITE_NUMBER_MSG,
        "input": replaced_input,
    }


@pytest.fixture
def client() -> TestClient:
    """サーバー内例外を送出せず、500レスポンスとして返すテスト用クライアントを生成する。

    既定の `TestClient` はサーバー内例外(`ValueError` など)をそのまま送出するため、
    実装不足によるテスト失敗が「500が返ること」として明確に表れない。本fixtureは
    `raise_server_exceptions=False` を指定し、失敗理由をステータスコードで確認できるようにする。

    Returns
    -------
    TestClient
        `raise_server_exceptions=False` を指定した、アプリ本体に接続されたテストクライアント。
    """
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(("literal", "replaced"), NON_FINITE_LITERALS)
def test_non_finite_field_value_returns_422(
    client: TestClient, endpoint: str, field: str, literal: str, replaced: str
) -> None:
    """a または b が非有限のfloatの場合に、500ではなく422が返ることを検証する (Req 1)。

    標準のJSONではないため、`json=` ではなく生のJSON文字列で送信する。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    field : str
        非有限のfloatを設定するフィールド名(`a` または `b`)。
    literal : str
        リクエストボディに埋め込むJSON数値リテラル。
    replaced : str
        エラー詳細で置換された後の文字列(本テストでは未使用。ケースの識別用)。
    """
    values = {"a": str(VALID_VALUE), "b": str(VALID_VALUE)}
    values[field] = literal
    content = f'{{"a": {values["a"]}, "b": {values["b"]}}}'

    response = client.post(endpoint, content=content, headers=JSON_HEADERS)

    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    "content",
    [
        pytest.param('{"a": [NaN], "b": 5}', id="a-nested-in-list"),
        pytest.param('{"a": 5, "b": [Infinity]}', id="b-nested-in-list"),
        pytest.param('{"a": {"x": Infinity}, "b": 5}', id="a-nested-in-object"),
        pytest.param('{"a": 5, "b": {"x": -Infinity}}', id="b-nested-in-object"),
        pytest.param('{"a": [1e400], "b": 5}', id="a-overflow-nested-in-list"),
        pytest.param("[NaN]", id="whole-body-list"),
        pytest.param("NaN", id="whole-body-nan"),
        pytest.param("Infinity", id="whole-body-infinity"),
        pytest.param("-Infinity", id="whole-body-negative-infinity"),
        pytest.param('{"a": NaN}', id="a-nan-b-missing"),
        pytest.param('{"a": Infinity}', id="a-infinity-b-missing"),
        pytest.param('{"b": -Infinity}', id="b-negative-infinity-a-missing"),
        pytest.param('{"a": NaN, "b": Infinity}', id="both-non-finite"),
        pytest.param('{"a": NaN, "b": 0}', id="a-nan-b-zero"),
        pytest.param('{"a": -1, "b": Infinity}', id="a-negative-b-infinity"),
    ],
)
def test_non_finite_in_other_positions_returns_422(
    client: TestClient, endpoint: str, content: str
) -> None:
    """非有限のfloatが、ネスト・ボディ全体・他エラーとの同時発生でも422になる (Req 2)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    content : str
        リクエストボディとして送る生のJSON文字列。
    """
    response = client.post(endpoint, content=content, headers=JSON_HEADERS)

    assert response.status_code == 422


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(("literal", "replaced"), NON_FINITE_LITERALS)
def test_non_finite_field_value_detail_is_standard_with_replaced_input(
    client: TestClient, endpoint: str, field: str, literal: str, replaced: str
) -> None:
    """a・b が非有限のfloatの場合に、inputのみ文字列に置換され他は標準のままである (Req 3)。

    `detail` はリストで、`type`・`loc`・`msg`・`input` を持つ1件のみとなり、
    `NaN` → `"nan"`、`Infinity`・`1e400` → `"inf"`、`-Infinity`・`-1e400` → `"-inf"` に置換される。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    field : str
        非有限のfloatを設定するフィールド名(`a` または `b`)。
    literal : str
        リクエストボディに埋め込むJSON数値リテラル。
    replaced : str
        エラー詳細の `input` に期待する置換後の文字列。
    """
    values = {"a": str(VALID_VALUE), "b": str(VALID_VALUE)}
    values[field] = literal
    content = f'{{"a": {values["a"]}, "b": {values["b"]}}}'

    response = client.post(endpoint, content=content, headers=JSON_HEADERS)

    assert response.status_code == 422
    assert response.json() == {"detail": [finite_number_error(field, replaced)]}


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("content", "expected_detail"),
    [
        pytest.param(
            '{"a": [NaN], "b": 5}',
            [
                {
                    "type": "int_type",
                    "loc": ["body", "a"],
                    "msg": "Input should be a valid integer",
                    "input": ["nan"],
                }
            ],
            id="a-nested-in-list",
        ),
        pytest.param(
            '{"a": 5, "b": {"x": Infinity}}',
            [
                {
                    "type": "int_type",
                    "loc": ["body", "b"],
                    "msg": "Input should be a valid integer",
                    "input": {"x": "inf"},
                }
            ],
            id="b-nested-in-object",
        ),
        pytest.param(
            "[NaN]",
            [
                {
                    "type": "model_attributes_type",
                    "loc": ["body"],
                    "msg": "Input should be a valid dictionary or object to extract fields from",
                    "input": ["nan"],
                }
            ],
            id="whole-body-list",
        ),
        pytest.param(
            "-Infinity",
            [
                {
                    "type": "model_attributes_type",
                    "loc": ["body"],
                    "msg": "Input should be a valid dictionary or object to extract fields from",
                    "input": "-inf",
                }
            ],
            id="whole-body-negative-infinity",
        ),
        pytest.param(
            '{"a": NaN}',
            [
                finite_number_error("a", "nan"),
                {
                    "type": "missing",
                    "loc": ["body", "b"],
                    "msg": "Field required",
                    # 欠落エラーの input はボディ全体であり、その中の NaN も置換される。
                    "input": {"a": "nan"},
                },
            ],
            id="a-nan-b-missing",
        ),
        pytest.param(
            '{"a": NaN, "b": Infinity}',
            [finite_number_error("a", "nan"), finite_number_error("b", "inf")],
            id="both-non-finite",
        ),
        pytest.param(
            '{"a": 0, "b": -Infinity}',
            [
                {
                    "type": "greater_than",
                    "loc": ["body", "a"],
                    "msg": "Input should be greater than 0",
                    "input": 0,
                    "ctx": {"gt": 0},
                },
                finite_number_error("b", "-inf"),
            ],
            id="a-zero-b-negative-infinity",
        ),
    ],
)
def test_non_finite_in_other_positions_detail_replaces_only_non_finite(
    client: TestClient, endpoint: str, content: str, expected_detail: list[dict[str, object]]
) -> None:
    """ネスト・ボディ全体・他エラーとの同時発生でも、非有限のfloatのみ置換される (Req 3)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    content : str
        リクエストボディとして送る生のJSON文字列。
    expected_detail : list[dict[str, object]]
        手計算で決めた、期待する `detail` 全体。
    """
    response = client.post(endpoint, content=content, headers=JSON_HEADERS)

    assert response.status_code == 422
    assert response.json() == {"detail": expected_detail}


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(
    ("invalid_value", "expected_error"),
    [
        pytest.param(
            0,
            {
                "type": "greater_than",
                "msg": "Input should be greater than 0",
                "input": 0,
                "ctx": {"gt": 0},
            },
            id="zero",
        ),
        pytest.param(
            -3,
            {
                "type": "greater_than",
                "msg": "Input should be greater than 0",
                "input": -3,
                "ctx": {"gt": 0},
            },
            id="negative",
        ),
        pytest.param(
            1.5,
            {
                "type": "int_from_float",
                "msg": "Input should be a valid integer, got a number with a fractional part",
                "input": 1.5,
            },
            id="decimal",
        ),
        pytest.param(
            "abc",
            {
                "type": "int_parsing",
                "msg": "Input should be a valid integer, unable to parse string as an integer",
                "input": "abc",
            },
            id="string",
        ),
        pytest.param(
            None,
            {
                "type": "int_type",
                "msg": "Input should be a valid integer",
                "input": None,
            },
            id="null",
        ),
        pytest.param(
            [1],
            {
                "type": "int_type",
                "msg": "Input should be a valid integer",
                "input": [1],
            },
            id="list",
        ),
    ],
)
def test_finite_invalid_value_keeps_standard_422_body(
    client: TestClient,
    endpoint: str,
    field: str,
    invalid_value: object,
    expected_error: dict[str, object],
) -> None:
    """非有限のfloatを含まない不正な値の422が、標準どおり `input` を含むことを検証する (Req 4)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    field : str
        不正な値を設定するフィールド名(`a` または `b`)。
    invalid_value : object
        設定する不正な値(`0`・負数・小数・数値でない値)。
    expected_error : dict[str, object]
        `loc` を除く、手計算で決めた期待するエラー詳細1件。
    """
    payload: dict[str, object] = {"a": VALID_VALUE, "b": VALID_VALUE}
    payload[field] = invalid_value

    response = client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": [{**expected_error, "loc": ["body", field]}]}


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize(
    ("payload", "missing_field"),
    [
        pytest.param({"b": VALID_VALUE}, "a", id="a-missing"),
        pytest.param({"a": VALID_VALUE}, "b", id="b-missing"),
    ],
)
def test_missing_field_keeps_standard_422_body(
    client: TestClient,
    endpoint: str,
    payload: dict[str, int],
    missing_field: str,
) -> None:
    """フィールド欠落の422が、標準どおり `input`(ボディ全体)を含むことを検証する (Req 4)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    payload : dict[str, int]
        一方のフィールドを欠落させたリクエストボディ。
    missing_field : str
        欠落させたフィールド名。
    """
    response = client.post(endpoint, json=payload)

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", missing_field],
                "msg": "Field required",
                "input": payload,
            }
        ]
    }


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_both_fields_missing_keeps_standard_422_body(client: TestClient, endpoint: str) -> None:
    """a・b がともに欠落した場合の422が、標準どおり2件のエラーと `input` を含む (Req 4)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    """
    response = client.post(endpoint, json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "a"], "msg": "Field required", "input": {}},
            {"type": "missing", "loc": ["body", "b"], "msg": "Field required", "input": {}},
        ]
    }


@pytest.mark.parametrize(
    ("endpoint", "a", "b", "operation", "expected"),
    [
        pytest.param("/calculate/add", 5, 3, "add", 8, id="add"),
        pytest.param("/calculate/subtract", 5, 3, "subtract", 2, id="subtract"),
        pytest.param("/calculate/multiply", 5, 3, "multiply", 15, id="multiply"),
        pytest.param("/calculate/divide", 6, 3, "divide", 2.0, id="divide"),
    ],
)
def test_valid_request_returns_200_as_before(
    client: TestClient,
    endpoint: str,
    a: int,
    b: int,
    operation: str,
    expected: float,
) -> None:
    """有効なリクエストが従来どおり200とボディ全体で返ることを検証する (Req 5)。

    Parameters
    ----------
    client : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    endpoint : str
        対象のエンドポイントのパス。
    a : int
        第1オペランド。
    b : int
        第2オペランド。
    operation : str
        レスポンスの `operation` に期待する演算名。
    expected : float
        手計算で求めた期待する演算結果。
    """
    response = client.post(endpoint, json={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {"operation": operation, "a": a, "b": b, "result": expected}

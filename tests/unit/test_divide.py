"""POST /calculate/divide のユニットテスト。"""

import pytest
from fastapi.testclient import TestClient

from apps.main import app

ENDPOINT = "/calculate/divide"
VALID_VALUE = 5


@pytest.fixture
def client() -> TestClient:
    """テスト用のHTTPクライアントを生成する。

    Returns
    -------
    TestClient
        アプリケーション本体に接続されたテストクライアント。
    """
    return TestClient(app)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(10, 2, 5.0, id="divisible"),
        pytest.param(1, 1, 1.0, id="minimum-values"),
        pytest.param(7, 1, 7.0, id="b-identity"),
        pytest.param(5, 5, 1.0, id="same-values"),
        pytest.param(100, 4, 25.0, id="three-digit-dividend"),
    ],
)
def test_divide_divisible_returns_float(
    client: TestClient, a: int, b: int, expected: float
) -> None:
    """割り切れる除算が200とボディ全体で返り、resultがfloatであることを検証する (Req 1)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    a : int
        被除数。
    b : int
        除数。
    expected : float
        手計算で求めた期待する除算結果。
    """
    response = client.post(ENDPOINT, json={"a": a, "b": b})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "operation": "divide",
        "a": a,
        "b": b,
        "result": expected,
    }
    # JSON上で 5.0 は float、5 は int として区別されるため、float で返ることを確認する。
    assert isinstance(body["result"], float)


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(10, 3, 3.3333333333333335, id="design-example"),
        pytest.param(1, 2, 0.5, id="half"),
        pytest.param(1, 4, 0.25, id="quarter"),
        pytest.param(7, 2, 3.5, id="decimal-terminating"),
        pytest.param(1, 3, 0.3333333333333333, id="one-third"),
        pytest.param(2, 3, 0.6666666666666666, id="two-thirds"),
        pytest.param(22, 7, 3.142857142857143, id="repeating-decimal"),
        pytest.param(100, 3, 33.333333333333336, id="three-digit-dividend"),
    ],
)
def test_divide_not_divisible_returns_decimal(
    client: TestClient, a: int, b: int, expected: float
) -> None:
    """割り切れない正の整数同士の除算が小数(float)として返ることを検証する (Req 3)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    a : int
        被除数。
    b : int
        除数。
    expected : float
        手計算で求めた期待する除算結果(float精度)。
    """
    response = client.post(ENDPOINT, json={"a": a, "b": b})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "operation": "divide",
        "a": a,
        "b": b,
        "result": expected,
    }
    assert isinstance(body["result"], float)


def test_divide_by_zero_returns_422(client: TestClient) -> None:
    """b が 0 の場合に独自の400ではなく422が返ることを検証する (Req 2)。"""
    response = client.post(ENDPOINT, json={"a": VALID_VALUE, "b": 0})

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(
    "invalid_value",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative-one"),
        pytest.param(-100, id="negative-large"),
    ],
)
def test_divide_rejects_zero_and_negative(
    client: TestClient, field: str, invalid_value: int
) -> None:
    """a または b が 0 または負数の場合に422が返ることを検証する (Req 2)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    field : str
        不正な値を設定するフィールド名(`a` または `b`)。
    invalid_value : int
        設定する `0` または負数。
    """
    payload = {"a": VALID_VALUE, "b": VALID_VALUE}
    payload[field] = invalid_value

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(
    "invalid_value",
    [
        pytest.param(1.5, id="positive-decimal"),
        pytest.param(0.5, id="decimal-below-one"),
        pytest.param(-2.5, id="negative-decimal"),
    ],
)
def test_divide_rejects_decimal(client: TestClient, field: str, invalid_value: float) -> None:
    """a または b が小数の場合に422が返ることを検証する (Req 2)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    field : str
        不正な値を設定するフィールド名(`a` または `b`)。
    invalid_value : float
        設定する小数。
    """
    payload: dict[str, float | int] = {"a": VALID_VALUE, "b": VALID_VALUE}
    payload[field] = invalid_value

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(
    "invalid_value",
    [
        pytest.param("abc", id="string"),
        pytest.param("", id="empty-string"),
        pytest.param(None, id="null"),
        pytest.param([1], id="list"),
        pytest.param({"value": 1}, id="object"),
    ],
)
def test_divide_rejects_non_numeric(client: TestClient, field: str, invalid_value: object) -> None:
    """a または b が数値でない場合に422が返ることを検証する (Req 2)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    field : str
        不正な値を設定するフィールド名(`a` または `b`)。
    invalid_value : object
        設定する数値以外の値。
    """
    payload: dict[str, object] = {"a": VALID_VALUE, "b": VALID_VALUE}
    payload[field] = invalid_value

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"b": VALID_VALUE}, id="a-missing"),
        pytest.param({"a": VALID_VALUE}, id="b-missing"),
        pytest.param({}, id="both-missing"),
    ],
)
def test_divide_rejects_missing_field(client: TestClient, payload: dict[str, int]) -> None:
    """a または b が欠落している場合に422が返ることを検証する (Req 2)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    payload : dict[str, int]
        一部または全部のフィールドを欠落させたリクエストボディ。
    """
    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422


@pytest.fixture
def client_without_raise() -> TestClient:
    """サーバー内例外を送出せず、500レスポンスとして返すテスト用クライアントを生成する。

    既定の `TestClient` はサーバー内例外(`OverflowError` など)をそのまま送出するため、
    実装不足によるテスト失敗が「500相当」として明確に表れない。本fixtureは既存の
    `client` fixtureとは別に用意し、Req 4のテストでのみ使用する。

    Returns
    -------
    TestClient
        `raise_server_exceptions=False` を指定した、アプリ本体に接続されたテストクライアント。
    """
    return TestClient(app, raise_server_exceptions=False)


def test_divide_quotient_exceeds_float_range_returns_422(
    client_without_raise: TestClient,
) -> None:
    """商がfloatの範囲を超える場合に500ではなく422が返ることを検証する (Req 4)。

    a = 10**400, b = 1 の商は 10**400 であり、float の上限(約1.8e308)を超える。

    Parameters
    ----------
    client_without_raise : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    """
    response = client_without_raise.post(ENDPOINT, json={"a": 10**400, "b": 1})

    assert response.status_code == 422


def test_divide_huge_operands_with_representable_quotient_returns_200(
    client_without_raise: TestClient,
) -> None:
    """入力が非常に大きくても商がfloatに収まる場合は200で正しく返ることを検証する (Req 1)。

    a = 10**400, b = 10**399 の商は 10 であり、float で 10.0 として表現できる。
    Req 4の境界の対比として、範囲超過と誤判定されないことを確認する。

    Parameters
    ----------
    client_without_raise : TestClient
        サーバー内例外を500レスポンスとして返すテスト用クライアント。
    """
    response = client_without_raise.post(ENDPOINT, json={"a": 10**400, "b": 10**399})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "operation": "divide",
        "a": 10**400,
        "b": 10**399,
        "result": 10.0,
    }
    assert isinstance(body["result"], float)

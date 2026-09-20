"""POST /calculate/subtract のユニットテスト。"""

import pytest
from fastapi.testclient import TestClient

from apps.main import app

ENDPOINT = "/calculate/subtract"
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
        pytest.param(10, 3, 7, id="design-example"),
        pytest.param(2, 1, 1, id="minimum-positive-result"),
        pytest.param(5, 5, 0, id="equal-values-zero-result"),
        pytest.param(250, 100, 150, id="three-digit-values"),
        pytest.param(
            12345678901234567890,
            1,
            12345678901234567889,
            id="beyond-64bit",
        ),
    ],
)
def test_subtract_positive_integers(client: TestClient, a: int, b: int, expected: int) -> None:
    """正の整数同士の減算が200とレスポンスボディ全体で返ることを検証する (Req 1)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    a : int
        被減数。
    b : int
        減数。
    expected : int
        手計算で求めた期待する減算結果。
    """
    response = client.post(ENDPOINT, json={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "subtract",
        "a": a,
        "b": b,
        "result": expected,
    }


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        pytest.param(3, 10, -7, id="design-example"),
        pytest.param(1, 2, -1, id="minimum-negative-result"),
        pytest.param(100, 250, -150, id="three-digit-values"),
        pytest.param(
            1,
            12345678901234567890,
            -12345678901234567889,
            id="beyond-64bit",
        ),
    ],
)
def test_subtract_returns_negative_result(
    client: TestClient, a: int, b: int, expected: int
) -> None:
    """a < b で結果が負数になる場合に、負数が200とレスポンスボディ全体で返ることを検証する (Req 3)。

    Parameters
    ----------
    client : TestClient
        テスト用のHTTPクライアント。
    a : int
        被減数(`b` より小さい値)。
    b : int
        減数。
    expected : int
        手計算で求めた期待する負数の減算結果。
    """
    response = client.post(ENDPOINT, json={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {
        "operation": "subtract",
        "a": a,
        "b": b,
        "result": expected,
    }


@pytest.mark.parametrize("field", ["a", "b"])
@pytest.mark.parametrize(
    "invalid_value",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative-one"),
        pytest.param(-100, id="negative-large"),
    ],
)
def test_subtract_rejects_zero_and_negative(
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
def test_subtract_rejects_decimal(client: TestClient, field: str, invalid_value: float) -> None:
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
def test_subtract_rejects_non_numeric(
    client: TestClient, field: str, invalid_value: object
) -> None:
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
def test_subtract_rejects_missing_field(client: TestClient, payload: dict[str, int]) -> None:
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

from pydantic import BaseModel, PositiveInt


class AddRequest(BaseModel):
    """加算 (add) のリクエストボディ。

    Attributes
    ----------
    a : PositiveInt
        被加数(正の整数)。
    b : PositiveInt
        加数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class SubtractRequest(BaseModel):
    """減算 (subtract) のリクエストボディ。

    Attributes
    ----------
    a : PositiveInt
        被減数(正の整数)。
    b : PositiveInt
        減数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class MultiplyRequest(BaseModel):
    """乗算 (multiply) のリクエストボディ。

    Attributes
    ----------
    a : PositiveInt
        被乗数(正の整数)。
    b : PositiveInt
        乗数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class DivideRequest(BaseModel):
    """除算 (divide) のリクエストボディ。

    Attributes
    ----------
    a : PositiveInt
        被除数(正の整数)。
    b : PositiveInt
        除数(正の整数)。
    """

    a: PositiveInt
    b: PositiveInt


class CalculationResponse(BaseModel):
    """四則演算の成功時レスポンス。

    Attributes
    ----------
    operation : str
        実行した演算名。
    a : int
        1つ目のオペランド。
    b : int
        2つ目のオペランド。
    result : int
        演算結果。
    """

    operation: str
    a: int
    b: int
    result: int


class DivideResponse(BaseModel):
    """除算 (divide) の成功時レスポンス。

    共用の `CalculationResponse` は `result: int` のため、`result` が
    float となる除算専用のレスポンスモデルとして定義する。

    Attributes
    ----------
    operation : str
        実行した演算名。
    a : int
        被除数。
    b : int
        除数。
    result : float
        除算結果 (`a / b`)。
    """

    operation: str
    a: int
    b: int
    result: float

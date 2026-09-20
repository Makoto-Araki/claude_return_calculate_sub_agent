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

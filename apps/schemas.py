from pydantic import BaseModel


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

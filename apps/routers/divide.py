from fastapi import APIRouter, HTTPException

from apps.schemas import DivideRequest, DivideResponse

router = APIRouter(prefix="/calculate")


@router.post("/divide", response_model=DivideResponse)
def divide(request: DivideRequest) -> DivideResponse:
    """2つの正の整数を除算して結果を返す。

    Parameters
    ----------
    request : DivideRequest
        被除数 `a` と除数 `b` を含むリクエストボディ。

    Returns
    -------
    DivideResponse
        演算名、オペランド、除算結果 (`a / b`、float) を含むレスポンス。

    Raises
    ------
    HTTPException
        商 `a / b` がfloatで表現できる範囲を超えた場合 (ステータスコード422)。
    """
    try:
        result = request.a / request.b
    except OverflowError:
        raise HTTPException(
            status_code=422,
            detail="商がfloatで表現できる範囲を超えています。",
        )
    return DivideResponse(
        operation="divide",
        a=request.a,
        b=request.b,
        result=result,
    )

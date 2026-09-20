from fastapi import APIRouter

from apps.schemas import CalculationResponse, SubtractRequest

router = APIRouter(prefix="/calculate")


@router.post("/subtract", response_model=CalculationResponse)
def subtract(request: SubtractRequest) -> CalculationResponse:
    """2つの正の整数を減算して結果を返す。

    Parameters
    ----------
    request : SubtractRequest
        被減数 `a` と減数 `b` を含むリクエストボディ。

    Returns
    -------
    CalculationResponse
        演算名、オペランド、減算結果 (`a - b`、負数になり得る) を含むレスポンス。
    """
    return CalculationResponse(
        operation="subtract",
        a=request.a,
        b=request.b,
        result=request.a - request.b,
    )

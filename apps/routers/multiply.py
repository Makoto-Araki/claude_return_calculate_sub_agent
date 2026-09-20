from fastapi import APIRouter

from apps.schemas import CalculationResponse, MultiplyRequest

router = APIRouter(prefix="/calculate")


@router.post("/multiply", response_model=CalculationResponse)
def multiply(request: MultiplyRequest) -> CalculationResponse:
    """2つの正の整数を乗算して結果を返す。

    Parameters
    ----------
    request : MultiplyRequest
        被乗数 `a` と乗数 `b` を含むリクエストボディ。

    Returns
    -------
    CalculationResponse
        演算名、オペランド、乗算結果 (`a * b`) を含むレスポンス。
    """
    return CalculationResponse(
        operation="multiply",
        a=request.a,
        b=request.b,
        result=request.a * request.b,
    )

from fastapi import APIRouter

from apps.schemas import AddRequest, CalculationResponse

router = APIRouter(prefix="/calculate")


@router.post("/add", response_model=CalculationResponse)
def add(request: AddRequest) -> CalculationResponse:
    """2つの正の整数を加算して結果を返す。

    Parameters
    ----------
    request : AddRequest
        被加数 `a` と加数 `b` を含むリクエストボディ。

    Returns
    -------
    CalculationResponse
        演算名、オペランド、加算結果 (`a + b`) を含むレスポンス。
    """
    return CalculationResponse(
        operation="add",
        a=request.a,
        b=request.b,
        result=request.a + request.b,
    )

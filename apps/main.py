import math

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apps.routers import add, divide, multiply, subtract

app = FastAPI(title="Calculator API")

app.include_router(add.router)
app.include_router(subtract.router)
app.include_router(multiply.router)
app.include_router(divide.router)


def _replace_non_finite(value: object) -> object:
    """値を再帰的に走査し、非有限のfloatを文字列に置換する。

    `NaN`・`Infinity`・`-Infinity` はJSONに変換できないため、`str(value)`
    (`"nan"`・`"inf"`・`"-inf"`)に置き換える。それ以外の値は変更しない。

    Parameters
    ----------
    value : object
        走査対象の値。`dict`・`list`・`tuple` は要素を再帰的に走査する。

    Returns
    -------
    object
        非有限のfloatを文字列化した値。`dict` は新しい `dict`(キーは変更しない)、
        `list`・`tuple` は新しい `list` として返し、それ以外はそのまま返す。
    """
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {key: _replace_non_finite(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_replace_non_finite(item) for item in value]
    return value


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """リクエスト検証エラーを、非有限のfloatを文字列化した422レスポンスに整形する。

    FastAPI標準のハンドラと同じ形式で返すが、エラー詳細に含まれる非有限のfloatのみを
    文字列に置換する。これにより、JSONへの変換失敗による500を防ぐ。

    Parameters
    ----------
    request : Request
        検証エラーを起こしたリクエスト。
    exc : RequestValidationError
        FastAPIが送出した検証エラー。

    Returns
    -------
    JSONResponse
        ステータスコード422と、`{"detail": [...]}` 形式のボディを持つレスポンス。
    """
    errors = _replace_non_finite(exc.errors())
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})

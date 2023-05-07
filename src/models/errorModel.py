from pydantic import BaseModel
from fastapi import status


class ErrorInfoModel(Exception):
    def __init__(self, code: int, message: str, http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Exception = None,):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details
        super().__init__(self.message)

    def __repr__(self):
        return f'code:{self.code},message:{self.message},status:{self.http_status}'


class ErrorInfoContainer:
    # General errors
    unhandled_error = ErrorInfoModel(code=1, message='Internal server error')
    could_not_get_excepted_response = ErrorInfoModel(
        code=2, message='Could not get expected response')
    model_validation_error = ErrorInfoModel(
        code=3, message='Model validation error', http_status=status.HTTP_400_BAD_REQUEST)
    not_found_error = ErrorInfoModel(
        code=4, message='Not found', http_status=status.HTTP_404_NOT_FOUND)
    file_type_is_not_allowed=ErrorInfoModel(
        code=5, message='file type is not allowed', http_status=status.HTTP_400_BAD_REQUEST)
    file_too_large=ErrorInfoModel(
        code=6, message='file too large', http_status=status.HTTP_400_BAD_REQUEST)

    # Custom service errors


class ErrorResponseModel(BaseModel):
    error_code: int = None
    error_message: str = None
    error_detail: list = None

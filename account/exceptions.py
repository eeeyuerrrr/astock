from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError


class OperateError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '操作失败'
    default_code = 'operate_fail'





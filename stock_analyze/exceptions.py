from rest_framework import status
from rest_framework.exceptions import APIException

class DataMissingError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = '数据缺失'
    default_code = 'data_missing'
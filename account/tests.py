from django.test import TestCase

# Create your tests here.
from rest_framework.exceptions import ValidationError


try:
    raise ValidationError(detail='test...')
except ValidationError as e:
    print(e.detail[0])
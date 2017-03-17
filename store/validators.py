from re import compile
from django.core.exceptions import ValidationError


def validate_zip_code(value):
    regex = compile('[0-9]{2}-[0-9]{3}')
    if not regex.match(value):
        raise ValidationError('Niepoprawny format kodu pocztowego.')

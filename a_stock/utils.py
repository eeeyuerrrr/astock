import datetime
import traceback
import hashlib
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.auth.password_validation import MinimumLengthValidator, NumericPasswordValidator

import logging

logger = logging.getLogger(__name__)

def print_err(err):
    # print(repr(err))
    logger.error('[-] {!r}'.format(err))
    traceback.print_tb(err.__traceback__)


#  生成激活帐号或重置密码的key
def gen_user_key(usersalt):
    salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    return hashlib.sha1((salt + usersalt).encode('utf-8')).hexdigest()


def gen_user_key_expires(days=2):
    return timezone.now() + datetime.timedelta(days=days)


def send_html_mail(from_email, to_emails, subject, html_content):
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def validate_mail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_password(pw):
    try:
        MinimumLengthValidator(8).validate(pw)
        NumericPasswordValidator().validate(pw)
        return True
    except ValidationError:
        return False

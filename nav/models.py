from django.contrib.auth.models import User
from django.db import models
from django.db.models import ImageField, CharField, URLField, IntegerField, BooleanField


class Site(models.Model):
    DATAS = 'DATAS'
    NEWS = 'NEWS'
    OTHERS = 'OTHERS'
    PERSONAL = 'PERSONAL'
    CATEGORY_CHOICES = (
        (DATAS,'数据'),
        (NEWS, '新闻'),
        (OTHERS,'其他'),
        (PERSONAL, '用户自定义'),
    )
    name = CharField(max_length=20, blank=False, default='')
    url = URLField(blank=False, default='')
    icon = ImageField(blank=True, upload_to='icons/')
    description = CharField(max_length=100, blank=True)
    category = CharField(max_length=10, choices=CATEGORY_CHOICES, default=OTHERS)
    order = IntegerField(default=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites', blank=True, null=True, default=None)


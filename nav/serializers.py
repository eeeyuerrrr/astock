from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Site


class SiteSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, default=None)

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'description', 'icon', 'order', 'category', 'owner')
        write_only_fields = ('owner',)

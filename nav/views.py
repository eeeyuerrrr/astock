from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import NotAuthenticated, ValidationError, APIException
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse

from a_stock.exceptions import OperateError
from .models import Site
from .serializers import SiteSerializer


# ~~~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_site_list(request):
    return Response(template_name='nav/sites.html')


# ~~~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@api_view(('GET',))
def api_site_list(request):
    q = (Q(owner=None) | Q(owner=request.user)) if request.user.is_authenticated else Q(owner=None)
    sites = Site.objects.filter(q).order_by('order')
    serializer = SiteSerializer(sites, many=True)
    return Response(serializer.data)


@api_view(('POST',))
@ensure_csrf_cookie
def api_add_user_site(request):
    if not request.user.is_authenticated:
        raise NotAuthenticated(detail='请先登录')

    ser = SiteSerializer(data=dict(name=request.data['name'], url=request.data['url'],
                                   category=Site.PERSONAL, owner=request.user))
    if ser.is_valid():
        s = ser.save()
        return Response(data=s)
    print(ser.errors)
    raise OperateError(detail='参数错误，请检查。注意网址的格式是否正确。')

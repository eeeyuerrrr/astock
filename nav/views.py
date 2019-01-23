from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import NotAuthenticated, APIException
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from a_stock.exceptions import OperateError
from a_stock.utils import print_err
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

    try:
        ser = SiteSerializer(data=dict(name=request.data['name'], url=request.data['url'],
                                       category=Site.PERSONAL, owner=request.user.id))
        if ser.is_valid():
            ser.save()
            return Response(data=ser.data)
        raise OperateError(detail='参数错误，请检查。注意网址的格式是否正确。')
    except KeyError:
        raise OperateError(detail='参数错误，请检查')
    except APIException as e:
        raise e
    except Exception as e:
        print_err(e)
        raise APIException(detail='服务器出错')


@api_view(('POST',))
@ensure_csrf_cookie
def api_remove_user_site(request):
    if not request.user.is_authenticated:
        raise NotAuthenticated(detail='请先登录')
    try:
        site = Site.objects.get(id=request.data['id'], owner=request.user)
        site.delete()
        return Response(dict(success=True, detail='操作成功，已删除'))
    except KeyError:
        raise OperateError(detail='参数错误，请检查')
    except ObjectDoesNotExist:
        raise OperateError(detail='操作失败，id或用户信息错误')
    except Exception as e:
        print_err(e)
        raise APIException(detail='服务器出错')

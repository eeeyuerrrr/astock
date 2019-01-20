from rest_framework import generics
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from .models import Site
from .serializers import SiteSerializer


# ~~~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_site_list(request):
    return Response(template_name='nav/sites.html')


# ~~~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SiteList(generics.ListAPIView):
    queryset = Site.objects.order_by('order')
    serializer_class = SiteSerializer

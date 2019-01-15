from django.shortcuts import redirect


def redirect_root(request):
    return redirect('stock_analyze:page-index')

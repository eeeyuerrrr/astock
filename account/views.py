from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from rest_framework.decorators import api_view, renderer_classes, throttle_classes
from rest_framework.exceptions import ValidationError, NotFound, APIException
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from a_stock.throttles import UnsafeMethodThrottle, SendMailThrottle
from a_stock.utils import gen_user_key, send_html_mail, print_err, validate_mail, gen_user_key_expires, \
    validate_password
from a_stock.exceptions import OperateError
from .models import UserProfile
from .serializers import UserProfileSerializer, AccountOperateSerializer, AccountOperate


# ~~~~~~~~~~~~~~~~~~ page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_login(request):
    next_url = request.GET.get('next', reverse('home'))
    return Response(data={'next': next_url}, template_name='account/login.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_register(request):
    next_url = request.GET.get('next', reverse('home'))
    return Response(data={'next': next_url}, template_name='account/register.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_change_password(request):
    return Response(template_name='account/change_password.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_reset_pw_user_identify(request):
    return Response(template_name='account/reset_pw_user_identify.html')


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def page_reset_pw_user(request, key):
    try:
        profile = UserProfile.objects.get(reset_pw_key=key)
        if (timezone.now() < profile.reset_pw_key_expires):
            return Response(template_name='account/reset_pw.html', data={
                'key': key,
            })
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer,))
def account_activate(request, key):
    try:
        profile = UserProfile.objects.get(activate_key=key)
        if (not profile.user.is_active) and (timezone.now() < profile.activate_key_expires):
            profile.user.is_active = True
            profile.activate_key = None
            profile.activate_key_expires = None
            profile.user.save()
            success = True
            info = '激活成功，正在跳转'
        elif profile.user.is_active:
            success = False
            info = '该帐号已经激活过'
        elif timezone.now() >= profile.activate_key_expires:
            success = False
            info = '激活失败，该链接已过期'
        else:
            success = False
            info = '服务器出错，暂时无法激活'

        return Response(template_name='account/info.html', data={
            'title': '帐号激活',
            'success': success,
            'info': info,
            'redirect_url': reverse('account:page_login'),
        })
    except ObjectDoesNotExist:
        raise NotFound
    except Exception as e:
        print_err(e)
        raise APIException


# ~~~~~~~~~~~~~~~~~~ api ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@api_view(('POST',))
@throttle_classes((SendMailThrottle,))
def api_register(request):
    try:
        if request.user.is_authenticated:
            raise OperateError(detail='您当前处于登录状态，无法注册')

        username = request.POST['username']
        nickname = request.POST['nickname']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # check
        if not (username and nickname and email and password and confirm_password):
            raise ValidationError
        if password != confirm_password:
            raise OperateError(detail='两次输入的密码不一致')
        if User.objects.filter(username=username).exists():
            raise OperateError(detail='该用户名已存在')
        if UserProfile.objects.filter(nickname=nickname).exists():
            raise OperateError(detail='该昵称已被占用')
        if not validate_mail(email):
            raise OperateError(detail='邮箱格式错误')
        if len(username) < 2 or len(username) > 10:
            raise OperateError(detail='用户名长度应在2至10个字符')
        if len(nickname) < 1:
            raise OperateError(detail='请填写昵称')
        if not validate_password(password):
            raise OperateError(detail='密码不符合要求，请重新填写')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_active:
                raise OperateError(detail='该邮箱已注册过')
            else:
                # 注册过但是未激活的可重新注册
                user_profile = UserProfile.objects.get(user=user)
                user_profile.delete()
                user.delete()


        activate_key = gen_user_key(username)
        activate_key_expires = gen_user_key_expires(days=2)

        ser = UserProfileSerializer(data={
            'nickname': nickname,
            'activate_key': activate_key,
            'activate_key_expires': activate_key_expires,
            'user': {
                'username': username,
                'password': password,
                'email': email,
            }})
        if ser.is_valid():
            ser.save()
            # send verify mail
            subject = '{}网站帐号激活'.format(settings.MY_APP_NAME)
            link = 'http://{}'.format(settings.MY_SERVER_DOMAIN) + reverse('account:page_activate', args=[activate_key])
            html_content = render_to_string('account/activation_mail.html', {
                'link': link,
                'app_name': settings.MY_APP_NAME
            })
            from_mail = settings.EMAIL_HOST_USER
            to_mail = email
            send_html_mail(from_mail, [to_mail], subject, html_content)
            result = AccountOperate('register', True, info='已发送激活链接至所填邮箱，请前往邮箱激活帐号',
                                    redirect_url=reverse('account:page_login'))
            return Response(data=AccountOperateSerializer(result).data)
        else:
            raise ValidationError

    except KeyError:
        raise OperateError(detail='注册信息不完整')
    except ValidationError:
        raise OperateError(detail='注册信息有误，请检查')
    except OperateError as err:
        raise err
    except Exception as e:
        print_err(e)
        raise OperateError(detail='服务器出错，暂时无法注册')


@api_view(('POST',))
@throttle_classes((UnsafeMethodThrottle,))
def api_login(request):
    try:
        u = request.POST['username']
        p = request.POST['password']
        redirect_url = request.POST.get('next') or reverse('home')
        if not (u and p):
            raise ValidationError

        if request.user.is_authenticated:
            logout(request)
        user = User.objects.get(username=u)
        if not user.is_active:
            raise OperateError('该帐号未激活,请尽快前往注册邮箱激活')

        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            result = AccountOperate('login', True, info='登录成功', redirect_url=redirect_url)
            return Response(data=AccountOperateSerializer(result).data)
        else:
            raise OperateError(detail='帐号或密码错误')

    except KeyError:
        raise OperateError(detail='参数错误')
    except ValidationError:
        raise OperateError(detail='参数错误')
    except ObjectDoesNotExist:
        raise OperateError(detail='帐号不存在')
    except OperateError as e:
        raise e
    except:
        raise OperateError(detail='服务器出错，暂时无法登录')


@api_view(('POST',))
@throttle_classes((UnsafeMethodThrottle,))
def api_logout(request):
    try:
        logout(request)
        result = AccountOperate('logout', True, info='已退出登录')
        return Response(data=AccountOperateSerializer(result).data)
    except:
        raise OperateError(detail='退出登录失败')


@api_view(('POST',))
@throttle_classes((UnsafeMethodThrottle,))
def api_change_password(request):
    try:
        username = request.POST['username']
        old_pw = request.POST['old_password']
        new_pw = request.POST['new_password']
        confirm_pw = request.POST['confirm_password']
        if new_pw != confirm_pw:
            raise OperateError(detail='新密码和确认密码不一致')
        if old_pw == new_pw:
            raise OperateError(detail='新密码不能与原密码相同')
        if not validate_password(new_pw):
            raise OperateError('新密码不符合要求，请重新填写')
        if not (username and old_pw and new_pw and confirm_pw):
            raise ValidationError

        if request.user.is_authenticated:
            logout(request)
        user = User.objects.get(username=username)
        if not user.is_active:
            raise OperateError('该帐号未激活,请尽快前往注册邮箱激活')

        user = authenticate(username=username, password=old_pw)
        if user:
            user.set_password(new_pw)
            user.save()
            logout(request)
            result = AccountOperate('login', True, info='密码修改成功')
            return Response(data=AccountOperateSerializer(result).data)
        else:
            raise OperateError(detail='帐号或原密码错误')

    except ObjectDoesNotExist:
        raise OperateError(detail='用户不存在，请检查用户信息')
    except KeyError:
        raise OperateError(detail='参数缺失，请检查所填信息')
    except ValidationError:
        raise OperateError(detail='参数有误，请检查所填信息')
    except OperateError as e:
        raise e
    except:
        raise OperateError(detail='服务器出错，暂时无法修改密码')


@api_view(('POST',))
@throttle_classes((SendMailThrottle,))
def api_reset_pw_user_identify(request):
    try:
        username = request.POST['username']
        email = request.POST['email']
        if not (username and email):
            raise ValidationError
        if not validate_mail(email):
            raise OperateError(detail='邮箱格式错误')

        user = User.objects.get(username=username)
        if user.email == email:
            reset_pw_key = gen_user_key(email)
            reset_pw_key_expires = gen_user_key_expires(days=1)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.reset_pw_key = reset_pw_key
            user_profile.reset_pw_key_expires = reset_pw_key_expires
            user_profile.save()

            # send link by email
            subject = '{}网站用户密码重置'.format(settings.MY_APP_NAME)
            link = 'http://{}'.format(settings.MY_SERVER_DOMAIN) \
                   + reverse('account:page_reset_pw', args=[reset_pw_key])
            html_content = render_to_string('account/reset_pw_mail.html', {
                'link': link,
                'app_name': settings.MY_APP_NAME
            })
            from_mail = settings.EMAIL_HOST_USER
            to_mail = email
            send_html_mail(from_mail, [to_mail], subject, html_content)
            result = AccountOperate('reset_pw_user_identify', True, info='已发送重置密码的链接至所填邮箱，请前往邮箱重置密码')
            return Response(data=AccountOperateSerializer(result).data)
        else:
            raise OperateError('邮箱填写错误')

    except ObjectDoesNotExist:
        raise OperateError('用户不存在，请检查用户信息')
    except KeyError:
        raise OperateError('参数缺失，请检查所填信息')
    except ValidationError:
        raise OperateError('参数有误，请检查所填信息')
    except OperateError as e:
        raise e
    except:
        raise OperateError(detail='服务器出错，暂时无法重置密码')


@api_view(('POST',))
@throttle_classes((UnsafeMethodThrottle,))
def api_reset_pw(request):
    try:
        username = request.POST['username']
        new_pw = request.POST['new_password']
        confirm_pw = request.POST['confirm_password']
        reset_pw_key = request.POST['key']
        if not (username and new_pw and confirm_pw and reset_pw_key):
            raise ValidationError
        if new_pw != confirm_pw:
            raise OperateError('新密码和确认密码不一致')
        if not validate_password(new_pw):
            raise OperateError('新密码不符合要求，请重新填写')

        if request.user.is_authenticated:
            logout(request)
        user_profile = UserProfile.objects.get(reset_pw_key=reset_pw_key)
        if user_profile.user.username != username:
            raise OperateError('用户名填写错误')
        user_profile.user.set_password(new_pw)
        user_profile.user.save()
        user_profile.reset_pw_key = None
        user_profile.reset_pw_key_expires = None
        user_profile.save()
        result = AccountOperate('reset_pw', True, info='密码重置成功')
        return Response(data=AccountOperateSerializer(result).data)

    except ObjectDoesNotExist:
        raise OperateError('链接激活码错误')
    except KeyError:
        raise OperateError('参数缺失，请检查所填信息')
    except ValidationError:
        raise OperateError('参数有误，请检查所填信息')
    except OperateError as e:
        raise e
    except:
        raise OperateError(detail='服务器出错，暂时无法重置密码')

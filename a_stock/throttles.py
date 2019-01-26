from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class DownloadThrottle(UserRateThrottle):
    scope = 'download'


class UnsafeMethodThrottle(UserRateThrottle):
    scope = 'unsafe_method'


class SendMailThrottle(AnonRateThrottle):
    scope = 'send_mail'

from json import JSONEncoder
from api.models import Token
from django.http import JsonResponse
from django.utils.timezone import make_aware
from datetime import datetime,timedelta
import random
import string


random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
random_number = lambda N: ''.join(random.SystemRandom().choice(string.digits) for _ in range(N))


def Check(request,data):
    check = True
    for temp in data:
        if not (temp in request):
            check = False
    if not check:
        return JsonResponse({
            'success': False,
            'code':'400',
            'data': 'ورودی نامعتبر است'
        }, encoder=JSONEncoder)
    else:
        return check


def CheckNullable(list,error):
    for data in list:
        if data is None:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': error
            }, encoder=JSONEncoder)


def BlankOrElse(param1,param2):
    if (str(param2) == "") | (str(param2) is None):
        return param1
    return param2


def CheckToken(thistoken,user=None):
    return Token.objects.filter(token = thistoken).exists()


def GetObjByToken(token):
    tokenobj = Token.objects.filter(token = token).get()
    if hasattr(tokenobj, 'freelancer'):
        return False,tokenobj.freelancer
    return True,tokenobj.shop


def TokenHandler(token):
    if (token.validdate < make_aware(datetime.now())):
        token.validdate = (datetime.now() + timedelta(days=30))
        token.save()
        return token.token
    return token.token



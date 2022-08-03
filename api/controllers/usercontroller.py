from datetime import datetime , timedelta
import json
from distro import name
from django.core import serializers
from django.shortcuts import render
from django.http import JsonResponse
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.forms import model_to_dict
from duplicity.tempdir import default
from django.contrib.auth.hashers import check_password
from api.models import MainUser
from api.models import User,Token,MainUser,SMS
#from chat.models import ChatGroup,ChatMessage
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view
from twilio.rest import Client
import requests
import random
import string


random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
random_numebr = lambda N: ''.join(random.SystemRandom().choice(string.digits) for _ in range(N))


@csrf_exempt
@api_view(['POST'])
def Register(request):
    # Register A User
    data = json.loads(request.body)
    check = Check(data, ['username', 'password','email','phone','name'])
    if not (check is True):
        return check
    else:
        if ((data['username'] == "") | (data['username'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا نام کاربری را وارد کنید'
            }, encoder=JSONEncoder,status=400)
        if ((data['phone'] == "") | (data['phone'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا شماره همراه را وارد کنید'
            }, encoder=JSONEncoder,status=400)
        phone = data['phone']
        if MainUser.objects.filter(phone=phone).exists():
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'این شماره همراه قبلا در سیستم ثبت شده است'
            }, encoder=JSONEncoder,status=400)
        name = data['name']
        username = data['username']
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'این نام کاربری قبلا در سیستم ثبت شده است لطفا نام دیگری انتخاب کنید'
            }, encoder=JSONEncoder,status=400)
        email = 'None'
        if not ((data['email'] == "") | (data['email'] is None)):
            email = data['email']
        password = data['password']
        new_user = User.objects.create_user(username=username, email=email, password=password,first_name=name)
        token = random_str(128)
        while Token.objects.filter(token=token).exists():
            token = random_str(128)
        tokenobj = Token.objects.create(token=token)
        user = MainUser.objects.create(user=new_user, token=tokenobj, phone=phone, isauthenticated=False        )
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': token
        }, encoder=JSONEncoder)


@csrf_exempt
def Login(request):
    # Login
    data = json.loads(request.body)
    check = Check(data, ['username', 'password','email'])
    if not (check is True):
        return check
    if not ((data['email'] == "") | (data['email'] is None)):
        email = data['email']
    else:
        email = "NONE"
    if not ((data['username'] == "") | (data['username'] is None)):
        username = data['username']
    else:
        username = "NONE"
    password = data['password']
    if (username == "NONE"):
        if (email == "NONE"):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا نام کاربری و یا ایمیل خود را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        return LoginByEmail(email,password)
    print("********************* {0} ***********************",username)
    return LoginByUsername(username,password)


def LoginByUsername(username,password):
    try:
        if (User.objects.filter(username=username).exists()):
            print("********************* HERE 2 ***********************")
            if (check_password(password,User.objects.filter(username=username).get().password)):
                print("********************* HERE 3 ***********************")
                userobj = MainUser.objects.filter(user__username=username).get()
                context = {}
                context['token'] = userobj.token.token
                context['name'] = userobj.user.first_name
                return JsonResponse({
                    'success': True,
                    'code': '200',
                    'data': context
                }, encoder=JSONEncoder)
            return JsonResponse({
                'success': False,
                'code': '404',
                'data': 'پسورد وارد شده صحیح نیست'
            }, encoder=JSONEncoder)
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربری با این مشخصات پیدا نشد'
        }, encoder=JSONEncoder)
    except:
        print("********************* HERE 1 ***********************")
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربری با این مشخصات پیدا نشد'
        }, encoder=JSONEncoder)


def LoginByEmail(email,password):
    try:
        if (User.objects.filter(email=email).exists()):
            if (check_password(password,User.objects.filter(email=email).get().password)):
                userobj = MainUser.objects.filter(user__email=email).get()
                context = {}
                context['token'] = userobj.token.token
                context['name'] = userobj.user.first_name
                return JsonResponse({
                    'success': True,
                    'code': '200',
                    'data': context
                }, encoder=JSONEncoder)
            return JsonResponse({
                'success': False,
                'code': '404',
                'data': 'پسورد وارد شده صحیح نیست'
            }, encoder=JSONEncoder)
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربری با این مشخصات پیدا نشد'
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربری با این مشخصات پیدا نشد'
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['GET'])
def GetEntity(request):
    # Get Either User Data Or Freelancer Data
    check = Check(request.headers,['token'])
    if not (check is True):
        return check
    token = request.headers['token']
    if not (CheckToken(token)):
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربر در سیستم پیدا نشد'
        }, encoder=JSONEncoder)
    result,obj = GetObjByToken(token)
    if (result):
        mainuser = obj
        context = {}
        context['Username'] = mainuser.user.username
        context['Email'] = mainuser.user.email
        context['Age'] = mainuser.age
        context['NationalCode'] = mainuser.nationalcode
        context['Phone'] = mainuser.phone
        context['DateJoin'] = mainuser.datejoin.__str__()
        context['IsAuthenticated'] = mainuser.isauthenticated
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    else:
        freelancer = obj
        context = {}
        context['Username'] = freelancer.name
        context['Email'] = freelancer.email
        context['Phone'] = freelancer.phone
        if not (freelancer.city is None):
            context['City'] = freelancer.city.name
        context['Address'] = freelancer.address
        context['Description'] = freelancer.description
        context['Rate'] = freelancer.rate
        context['DateJoin'] = freelancer.datejoin.__str__()
        context['Level'] = freelancer.level
        context['ProfilePic'] = str(freelancer.profilepic)
        context['NumberOfJobs'] = freelancer.numberofjobs
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['POST'])
def UpdateUser(request):
    data = json.loads(request.body)
    check = (Check(data, ['email','name','age','nationalcode']) & Check(request.headers,['token']))
    if not (check is True):
        return check
    token = request.headers['token']
    if not (CheckToken(token)):
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربر در سیستم پیدا نشد'
        }, encoder=JSONEncoder)
    result,obj = GetObjByToken(token)
    if (result):
        mainuser = obj
        mainuser.age = BlankOrElse(mainuser.age,data['age'])
        mainuser.nationalcode = BlankOrElse(mainuser.nationalcode,data['nationalcode'])
        mainuser.user.email = BlankOrElse(mainuser.user.email,data['email'])
        mainuser.user.first_name = BlankOrElse(mainuser.user.first_name,data['name'])
        mainuser.isauthenticated = True
        mainuser.save()
        mainuser.user.save()
        context = {}
        context['Username'] = mainuser.user.username
        context['Email'] = mainuser.user.email
        context['Age'] = mainuser.age
        context['NationalCode'] = mainuser.nationalcode
        context['Phone'] = mainuser.phone
        context['DateJoin'] = mainuser.datejoin.__str__()
        context['IsAuthenticated'] = mainuser.isauthenticated
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    else:
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'موجودی موردنظر کاربر نمیباشد'
        }, encoder=JSONEncoder)


@csrf_exempt
def SendSMS(request):
    data = json.loads(request.body)
    check = Check(data, ['phone'])
    if not (check is True):
        return check
    phone = data['phone']
    number = random_numebr(5)
    sms = SMS.objects.create(sms=number,phone=phone,valid=datetime.now()+timedelta(hours=2))
    ApiKey = '3ea47267d2a947285d19c17bc8a5801f'
    body = {"mobile": phone, "method": "sms", "templateID": 9,"code":number, "param1": "کد را در اپلیکیشن وارد کنید با تشکر کارنت"}
    header = {'apikey':'3ea47267d2a947285d19c17bc8a5801f'}
    temp = requests.post('https://api.gsotp.com/otp/send',data=json.dumps(body),headers=header)
    print("************** Phone : "+phone + ' ******** CODE : ' + number)
    return JsonResponse({
        'success': True,
        'code': '200',
        'data': 'کد با موفقیت ارسال شد'
    }, encoder=JSONEncoder)


@csrf_exempt
def CheckSMS(request):
    data = json.loads(request.body)
    check = Check(data, ['phone','code'])
    if not (check is True):
        return check
    phone = data['phone']
    code = data['code']
    try:
        if SMS.objects.filter(phone=phone).exists():
            smsobj = SMS.objects.filter(phone=phone).get()
            time = smsobj.valid
            if (make_aware(datetime.now()) < time):
                number = smsobj.sms
                print(code)
                print(number)
                if (str(code) == str(number)):
                    SMS.objects.filter(phone=phone).delete()
                    return JsonResponse({
                        'success': True,
                        'code': '200',
                        'data': 'کد ارسال شده صحیح است'
                    }, encoder=JSONEncoder)
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'کد ارسال شده صحیح نمیباشد'
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'کد ارسال شده صحیح نمیباشد'
        }, encoder=JSONEncoder)


#TODO: Gotta Sync With The Chat Inorder To User This Method
""""@csrf_exempt
@api_view(['GET'])
def GetChatGroups(request):
    check = Check(request.headers, ['token'])
    if not (check is True):
        return check
    token = request.headers['token']
    result,obj = GetObjByToken(token)
    if (result):
        context = []
        chats = ChatGroup.objects.filter(user__id=obj.id).all()
        for chat in chats:
            temp = {'name':chat.name,'freelancer':chat.freelancer.name,
                    'category':chat.freelancer.category.name,'timestamp':str(chat.timestamp)}
            context.append(temp)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        },encoder=JSONEncoder,status=200)
    else:
        context = []
        chats = ChatGroup.objects.filter(freelancer__id=obj.id).all()
        for chat in chats:
            temp = {'name':chat.name,'user':chat.user.user.username,'timestamp':str(chat.timestamp)}
            context.append(temp)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        },encoder=JSONEncoder,status=200)"""

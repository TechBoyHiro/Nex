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
from api.models import Freelancer,FreeFile,Token,Category
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse,TokenHandler
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
def RegisterFreelancer(request):
    # Register A Freelancer
    data = json.loads(request.body)
    check = Check(data, ['name', 'password','email','phone','address','description','age','categoryid'])
    if not (check is True):
        return check
    try:
        if ((data['name'] == "") | (data['name'] is None)):
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
        if Freelancer.objects.filter(phone=phone).exists():
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'این شماره همراه قبلا در سیستم ثبت شده است'
            }, encoder=JSONEncoder,status=400)
        name = data['name']
        email = 'None'
        if not ((data['email'] == "") | (data['email'] is None)):
            email = data['email']
        password = data['password']
        description = data['description']
        address = data['address']
        age = data['age']
        category = Category.objects.filter(id=data['categoryid']).get()
        token = random_str(128)
        while Token.objects.filter(token=token).exists():
            token = random_str(128)
        tokenobj = Token.objects.create(token=token)
        new_user = Freelancer.objects.create(name=name,description=description,password=password,
                                             token=tokenobj,email=email,phone=phone,address=address,age=age,category=category)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': token
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت فریلنسر با مشکل مواجه شد'
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['POST'])
def Update(request):
    data = json.loads(request.body)
    check = (Check(data, ['email', 'address', 'age', 'description','name','password']) & Check(request.headers,['token']))
    if not (check is True):
        return check
    token = request.headers['token']
    if not (CheckToken(token)):
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربر در سیستم پیدا نشد'
        }, encoder=JSONEncoder)
    result, obj = GetObjByToken(token)
    if not (result):
        mainuser = obj
        mainuser.age = BlankOrElse(mainuser.age,data['age'])
        mainuser.description = BlankOrElse(mainuser.description,data['description'])
        mainuser.address = BlankOrElse(mainuser.address,data['address'])
        mainuser.name = BlankOrElse(mainuser.name,data['name'])
        mainuser.password = BlankOrElse(mainuser.password, data['password'])
        mainuser.email = BlankOrElse(mainuser.email,data['email'])
        mainuser.save()
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'بروزرسانی با موفقیت انجام شد'
        }, encoder=JSONEncoder)
    else:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'موجودی موردنظر فریلنسر نمیباشد'
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['GET'])
def Login(request):
    data = json.loads(request.body)
    check = Check(data, ['email','phone','password'])
    if not (check is True):
        return check
    try:
        if not ((data['email'] == "") | (data['email'] is None)):
            freelancer = Freelancer.objects.filter(email=data['email']).get()
            if str(freelancer.password) == str(data['password']):
                token = TokenHandler(freelancer.token)
                return JsonResponse({
                    'success': True,
                    'code': '200',
                    'data': token
                }, encoder=JSONEncoder)
            return JsonResponse({
                'success': False,
                'code': '404',
                'data': 'رمز عبور وارد شده صحیح نمیباشد'
            }, encoder=JSONEncoder)
        freelancer = Freelancer.objects.filter(phone=data['phone']).get()
        if str(freelancer.password) == str(data['password']):
            token = TokenHandler(freelancer.token)
            return JsonResponse({
                'success': True,
                'code': '200',
                'data': token
            }, encoder=JSONEncoder)
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'رمز عبور وارد شده صحیح نمیباشد'
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '404',
            'data': 'کاربر در سیستم پیدا نشد'
        }, encoder=JSONEncoder)










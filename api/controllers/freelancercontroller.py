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
from api.models import Freelancer,Token,Category,City,SubCategory
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse,TokenHandler,random_number,random_str
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view
from twilio.rest import Client
import requests


# Done
@csrf_exempt
@api_view(['POST'])
def RegisterFreelancer(request):
    # Register A Freelancer
    data = json.loads(request.body)
    check = Check(data, ['name', 'password', 'email', 'phone'])
    if not (check is True):
        return check
    try:
        if ((data['name'] == "") | (data['name'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا نام کاربری را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        if ((data['phone'] == "") | (data['phone'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا شماره همراه را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        if Freelancer.objects.filter(phone=data['phone']).exists():
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'این شماره همراه قبلا در سیستم ثبت شده است'
            }, encoder=JSONEncoder, status=400)
        name = data['name']
        email = 'None'
        if not ((data['email'] == "") | (data['email'] is None)):
            email = data['email']
        phone = data['phone']
        password = data['password']
        token = random_str(128)
        while Token.objects.filter(token=token).exists():
            token = random_str(128)
        tokenobj = Token.objects.create(token=token)
        freelancer = Freelancer.objects.create(name=name,password=password,
                                             token=tokenobj, email=email, phone=phone)
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


# Done
@csrf_exempt
@api_view(['POST'])
def Update(request):
    data = json.loads(request.body)
    check = (Check(data, ['cityid', 'address', 'description','password','email','subcatid']) & Check(request.headers,['token']))
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
        freelancer = obj
        if not ((data['cityid'] == '') | (data['cityid'] is None)):
            if not City.objects.filter(id=data['cityid']).exists:
                return JsonResponse({
                    'success': False,
                    'code': '404',
                    'data': 'شهر موجود نمیباشد'
                }, encoder=JSONEncoder)

            freelancer.city = City.objects.filter(id=data['cityid']).get()

        if not ((data['subcatid'] == '') | (data['subcatid'] is None)):
            if not SubCategory.objects.filter(id=data['subcatid']).exists:
                return JsonResponse({
                    'success': False,
                    'code': '404',
                    'data': 'شهر موجود نمیباشد'
                }, encoder=JSONEncoder)

            freelancer.subcat = SubCategory.objects.filter(id=data['subcatid']).get()

        freelancer.description = BlankOrElse(freelancer.description,data['description'])
        freelancer.address = BlankOrElse(freelancer.address,data['address'])
        freelancer.password = BlankOrElse(freelancer.password, data['password'])
        freelancer.email = BlankOrElse(freelancer.email,data['email'])
        freelancer.isauthenticated = True
        freelancer.save()
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


# Done
@csrf_exempt
@api_view(['POST'])
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
                name = freelancer.name
                context = {}
                context['Token'] = token
                context['Name'] = name
                return JsonResponse({
                    'success': True,
                    'code': '200',
                    'data': context
                }, encoder=JSONEncoder)
            return JsonResponse({
                'success': False,
                'code': '404',
                'data': 'رمز عبور وارد شده صحیح نمیباشد'
            }, encoder=JSONEncoder)
        freelancer = Freelancer.objects.filter(phone=data['phone']).get()
        if str(freelancer.password) == str(data['password']):
            token = TokenHandler(freelancer.token)
            name = freelancer.name
            context = {}
            context['Token'] = token
            context['Name'] = name
            return JsonResponse({
                'success': True,
                'code': '200',
                'data': context
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


# Done
@csrf_exempt
@api_view(['POST'])
def GetFreelancer(request):
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
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'موچودی فریلنسر نمیباشد'
        }, encoder=JSONEncoder)
    else:
        freelancer = obj
        context = {}
        context['Name'] = freelancer.name
        context['Email'] = freelancer.email
        if not (freelancer.city is None):
            context['City'] = freelancer.city.name
        context['Address'] = freelancer.address
        context['Description'] = freelancer.description
        context['DateJoin'] = freelancer.datejoin.__str__()
        if freelancer.profilepic:
            context['ProfilePic'] = str(freelancer.profilepic.url)
        context['IsAuthenticated'] = freelancer.isauthenticated
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)



@csrf_exempt
@api_view(['POST'])
def AddFreelancerResume(request):
    try:
        data = request.data
        check = (Check(data, ['resume']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        resume = request.FILES['resume']
        if not resume:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا رزومه را ارسال کنید'
            }, encoder=JSONEncoder, status=400)
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        freelancer.resume = resume
        freelancer.save()
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'فایل با موفقیت به فریلنسر افزوده شد'
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'افزودن فایل با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)







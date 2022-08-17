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
from api.models import GroupFile,Group,GroupMember,SubCategory
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
random_number = lambda N: ''.join(random.SystemRandom().choice(string.digits) for _ in range(N))


# Done
@csrf_exempt
@api_view(['POST'])
def AddGroup(request):
    data = json.loads(request.body)
    check = (Check(data, ['name','description','instalink','websitelink']) & Check(request.headers,['token']))
    if not (check is True):
        return check
    try:
        if ((data['name'] == "") | (data['name'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا نام گروه را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        if Group.objects.filter(name=data['name']).exists():
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروهی با این نام قبلا ثبت شده است'
            }, encoder=JSONEncoder, status=400)
        result, obj = GetObjByToken(request.headers['token'])
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر پیدا نشد'
            }, encoder=JSONEncoder)
        freelancer = obj
        name = data['name']
        description = data['description']
        insta = data['instalink']
        website = data['websitelink']
        group = Group.objects.create(name=name, description=description, instalink=insta, website=website)
        groupmember = GroupMember.objects.create(freelancer=freelancer, group=group, isadmin=True, role="Manager",
                                                 share=100.0)
        context = {}
        context['Message'] = "گروه با موفقیت ساخته شد"
        context['GroupId'] = group.id
        context['GroupName'] = group.name
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت گروه با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


# Done
@csrf_exempt
@api_view(['POST'])
def AddGroupSubcat(request):
    try:
        data = json.loads(request.body)
        check = (Check(data, ['groupid', 'subcats']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        if ((data['groupid'] == "") | (data['groupid'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا آیدی گروه را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        if ((data['subcats'] == "") | (data['subcats'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا ایدی زیر دسته بندی ها را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        group = Group.objects.filter(id=data['groupid']).get()
        gm = GroupMember.objects.filter(freelancer=freelancer, group=group).get()
        if gm is None:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        if not gm.isadmin:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دسترسی غیر مجاز'
            }, encoder=JSONEncoder, status=400)
        subcatids = str(data['subcats']).split(',')
        for id in subcatids:
            group.subcategories.add(SubCategory.objects.filter(id=id).get())
        group.save()
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'زیر دسته بندی ها با موفقیت افزوده شدند'
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'زیر دسته بندی ها موجود نیست'
        }, encoder=JSONEncoder, status=400)


# Done
@csrf_exempt
@api_view(['POST'])
def AddGroupFiles(request):
    try:
        data = request.data
        check = (Check(data, ['groupid', 'images']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        files = request.FILES.getlist('images')
        if not files:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'حداقل یک فایل ارسال کنید'
            }, encoder=JSONEncoder, status=400)
        if ((data['groupid'] == "") | (data['groupid'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'لطفا آیدی گروه را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        group = Group.objects.filter(id=data['groupid']).get()
        gm = GroupMember.objects.filter(freelancer=freelancer, group=group).get()
        if gm is None:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        """if not gm.isadmin:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دسترسی غیر مجاز'
            }, encoder=JSONEncoder, status=400)"""
        for file in files:
            gf = GroupFile.objects.create(group=group, file=file)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'فایل ها با موفقیت به گروه افزوده شد'
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'افزودن فایل با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)
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
from api.models import User,Token,Shop,SMS,BusinessType,Freelancer,Group,GroupMember,SubCategory
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
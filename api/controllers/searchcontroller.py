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
from api.models import GroupFile,Group,GroupMember,SubCategory,Gig,GigFile,GigMember,Package,PackageDetail,Order,Invitation,Tag
#from chat.models import ChatGroup,ChatMessage
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse,CheckNullable
from django.core.serializers.json import DjangoJSONEncoder
from api.infra.modelserializers.groupserializers import GroupGetSerializer,GroupGetListSerializer,FileSerializer,InvitationSerializer
from api.infra.modelserializers.gigserializers import GigGetSerializer
from rest_framework.decorators import api_view
from django.core.files import File
from django.conf import settings
from twilio.rest import Client
import requests
import random
import string


@csrf_exempt
@api_view(['POST'])
def GigsBySubcat(request): # Search Gigs By Subcats
    try:
        data = json.loads(request.body)
        check = Check(data, ['subcatid'])
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        subcatid = data['subcatid']
        CheckNullable([subcatid], 'ّلطفا آیدی زیر دسته بندی را وارد کنید')
        subcat = SubCategory.objects.filter(id=subcatid).first()
        if not subcat:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'زیر دسته بندی با این آیدی پیدا نشد'
            }, encoder=JSONEncoder, status=400)
        gigs = Gig.objects.filter(subcat=subcat).all()
        context = []
        for gig in gigs:
            imageURL = GigFile.objects.filter(gig=gig, priority=1).get().file.url
            test = GigGetSerializer(gig, context={'image': imageURL, 'myshare': "", 'myrole': ""})
            context.append(test.data)
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


@csrf_exempt
@api_view(['POST'])
def GigsByTag(request): # Search Gigs By Tag
    try:
        data = json.loads(request.body)
        check = Check(data, ['Tag'])
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        tag = data['subcatid']
        CheckNullable([tag], 'ّلطفا حداقل یک تگ را وارد کنید')
        gigs = Tag.objects.filter(name=tag).get().gigs.all()
        context = []
        for gig in gigs:
            imageURL = GigFile.objects.filter(gig=gig, priority=1).get().file.url
            test = GigGetSerializer(gig, context={'image': imageURL, 'myshare': "", 'myrole': ""})
            context.append(test.data)
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
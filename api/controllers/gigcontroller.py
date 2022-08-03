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
from api.models import *
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
def AddGig(request):
    data = json.loads(request.body)
    check = Check(request.headers,['token'])
    if not (check is True):
        return check
    token = request.headers['token']
    check = Check(data, ['title', 'description','subcatid','tags'])
    if not (check is True):
        return check
    try:
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'کاربر دسترسی ندارد'
            }, encoder=JSONEncoder,status=400)
        subcat = SubCategory.objects.filter(id=data['subcatid']).get()
        gig = Work.objects.create(title=data['title'],description=data['description'],
                                  freelancer=freelancer,subcategory=subcat)
        tags = data['tags']
        for tag in tags:
            if Tag.objects.filter(name=str(tag)).exists():
                Tag.objects.filter(name=str(tag)).get().works.add(gig)
            else:
                tagobj = Tag.objects.create(name=str(tag))
                tagobj.works.add(gig)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': gig.id
        }, encoder=JSONEncoder, status=200)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت گیگ با مشکل مواجه شد'
        }, encoder=JSONEncoder,status=400)


@csrf_exempt
@api_view(['POST'])
def AddGigFile(request):
    check = Check(request.headers,['token'])
    if not (check is True):
        return check
    token = request.headers['token']
    check = Check(request.data, ['id'])
    if not (check is True):
        return check
    try:
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'کاربر دسترسی ندارد'
            }, encoder=JSONEncoder,status=400)
        gig = Work.objects.filter(id=request.data['id']).get()
        if (gig.freelancer.id != freelancer.id):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر دسترسی ندارد'
            }, encoder=JSONEncoder,status=400)
        print('********************* HERE 2 ***********************')
        images = request.FILES.getlist('pictures')
        print('********************* HERE 3 ***********************')
        i=1
        for image in images:
            print('********************* HERE 32 ***********************')
            WorkFile.objects.create(file=image,work=gig,priority=i)
            i+=1
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'فایل با موفقیت افزوده شد'
        }, encoder=JSONEncoder, status=200)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'افزودن فایل با مشکل مواجه شد'
        }, encoder=JSONEncoder,status=400)


@csrf_exempt
@api_view(['POST'])
def AddGigPackage(request):
    data = json.loads(request.body)
    check = Check(request.headers,['token'])
    if not (check is True):
        return check
    token = request.headers['token']
    check = Check(data, ['id','title','description','price','deliverytime','numberofrevisions',
                         'keys','values'])
    if not (check is True):
        return check
    try:
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'کاربر دسترسی ندارد'
            }, encoder=JSONEncoder,status=400)
        gig = Work.objects.filter(id=data['id']).get()
        if (gig.freelancer.id != freelancer.id):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر دسترسی ندارد'
            }, encoder=JSONEncoder,status=400)
        package = Package.objects.create(work=gig,title=data['title'],description=data['description'],
                                         price=data['price'],deliverytime=data['deliverytime'],
                                         numberofrevisions=data['numberofrevisions'])
        if gig.leastprice > data['price'] :
            gig.leastprice = data['price']
            gig.save()
        keys = data['keys']
        i=0
        for key in keys:
            value = data['values'][i]
            PackageDetail.objects.create(key=key,value=value,package=package)
            i+=1
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'پکیج با موفقیت افزوده شد'
        }, encoder=JSONEncoder, status=200)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'افزودن پکیج با مشکل مواجه شد'
        }, encoder=JSONEncoder,status=400)


@csrf_exempt
@api_view(['GET'])
def GetGigBySubCatId(request):
    data = json.loads(request.body)
    check = Check(data,['subcatid'])
    if not (check is True):
        return check
    try:
        subcatid = data['subcatid']
        gigs = Work.objects.filter(subcategory__id=subcatid).all().order_by('rate')
        context = []
        for gig in gigs:
            temp = {'freelancername': gig.freelancer.name, 'title': gig.title,
                    'rate': gig.rate, 'ratenumber': gig.numberofrates,
                    'leastprice': gig.leastprice}
            context.append(temp)
        return JsonResponse({
            'success': True,
            'code': '200',

            'data': context
        }, encoder=JSONEncoder, status=200)
    except:
        return JsonResponse({
            'success': True,
            'code': '400',
            'data': 'زیر دسته پیدا نشد!'
        }, encoder=JSONEncoder, status=400)




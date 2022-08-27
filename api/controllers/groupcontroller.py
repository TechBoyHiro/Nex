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
from api.models import GroupFile,Group,GroupMember,SubCategory,Gig,GigFile,GigMember,Package,PackageDetail
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


# Done
@csrf_exempt
@api_view(['POST'])
def AddGroupGig(request):
    try:
        data = request.data
        check = (Check(data, ['groupid', 'title', 'description', 'subcatid', 'images']) & Check(request.headers,['token']))
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
        if ((data['subcatid'] == "") | (data['subcatid'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'حداقل یک زیر دسته بندی وارد کنید'
            }, encoder=JSONEncoder, status=400)
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        group = Group.objects.filter(id=data['groupid']).first()
        if not group:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موجود نمیباشد'
            }, encoder=JSONEncoder)
        gm = GroupMember.objects.filter(freelancer=freelancer, group=group).first()
        if not gm:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر عضو گروه نمیباشد'
            }, encoder=JSONEncoder, status=400)
        if not gm.isadmin:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دسترسی غیر مجاز'
            }, encoder=JSONEncoder, status=400)
        files = request.FILES.getlist('images')
        title = data['title']
        description = data['description']
        subcat = SubCategory.objects.filter(id=data['subcatid']).first()
        if not subcat:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'زیر دسته بندی موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        gig = Gig.objects.create(group=group, subcat=subcat, title=title, description=description)
        gigmember = GigMember.objects.create(groupmember=gm,gig=gig,isadmin=True)
        if not files:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'حداقل یک فایل ارسال کنید'
            }, encoder=JSONEncoder, status=400)
        x = 1
        for file in files:
            temp = GigFile.objects.create(gig=gig, file=file, priority=x)
            x += 1
        context = {}
        context['message'] = 'گیگ با موفقیت ساخته شد'
        context['GigId'] = gig.id
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساخت گیگ با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def AddGigPackage(request):
    try:
        data = json.loads(request.body)
        check = (Check(data, ['gigid', 'title', 'description', 'price', 'deliverytime', 'numberofrevisions',
                              'keys', 'values']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        gig = Gig.objects.filter(id=data['id']).get()
        gigmember = GigMember.objects.filter(gig=gig,groupmember__freelancer=freelancer).first()
        if not gigmember:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر عضو گیگ نمیباشد'
            }, encoder=JSONEncoder,status=400)
        if gigmember.isadmin:
            package = Package.objects.create(work=gig, title=data['title'], description=data['description'],
                                             price=data['price'], deliverytime=data['deliverytime'],
                                             numberofrevisions=data['numberofrevisions'])
            if gig.leastprice > data['price']:
                gig.leastprice = data['price']
                gig.save()
            keys = data['keys']
            i = 0
            for key in keys:
                value = data['values'][i]
                PackageDetail.objects.create(key=key, value=value, package=package)
                i += 1
            return JsonResponse({
                'success': True,
                'code': '200',
                'data': 'پکیج با موفقیت افزوده شد'
            }, encoder=JSONEncoder, status=200)
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'فریلنسر دسترسی ندارد'
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'افزودن پکیج با مشکل مواجه شد'
        }, encoder=JSONEncoder,status=400)


# Done
@csrf_exempt
@api_view(['POST'])
def AddGigMember(request):
    try:
        data = request.data
        check = (Check(data, ['gigid', 'groupmemberid','role','share']) & Check(request.headers,['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        if ((data['gigid'] == "") | (data['gigid'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'آیدی گیگ را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        gig = Gig.objects.filter(id=data['gigid']).first()
        if not gig:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گیگ موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        if ((data['groupmemberid'] == "") | (data['groupmemberid'] is None)):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'آیدی عضو گروه را وارد کنید'
            }, encoder=JSONEncoder, status=400)
        token = request.headers['token']
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'موچودی فریلنسر نمیباشد'
            }, encoder=JSONEncoder)
        gigmember = GigMember.objects.filter(gig=gig,isadmin=True).first()
        if not gigmember:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گیگ ادمین ندارد با پشتیبانی تماس بگیرید'
            }, encoder=JSONEncoder, status=400)
        if not (gigmember.groupmember.freelancer==freelancer):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر دسترسی ندارد'
            }, encoder=JSONEncoder, status=400)
        gm = GroupMember.objects.filter(id=data['groupmemberid']).first()
        if not (gm.group==gig.group):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر اول باید در گروه مالک گیگ عضو باشد'
            }, encoder=JSONEncoder, status=400)
        if ((GigMember.objects.filter(gig=gig,isadmin=True).get().groupmember.freelancer)==freelancer):
            obj = GigMember.objects.filter(groupmember=gm, gig=gig,isadmin=True).first()
            obj.share = data['share']
            obj.role = data['role']
            return JsonResponse({
                'success': True,
                'code': '200',
                'data': 'سهام و نقش ادمین گیگ با موفقیت افزوده شد'
            }, encoder=JSONEncoder, status=400)
        """shares = 0
        members = GigMember.objects.filter(gig=gig).all()
        for member in members:
            shares += member.share
        if not (shares+data['share']==100.0):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'جمع درصد سهام از گیگ باید 100 باشد'
            }, encoder=JSONEncoder, status=400)"""
        obj = GigMember.objects.create(groupmember=gm,gig=gig,role=data['role'],share=data['share'])
        context = {}
        context['Message'] = 'فریلنسر با موفقیت به گیگ اضافه شد'
        context['GigMemberId'] = obj.id
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساخت گیگ با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)
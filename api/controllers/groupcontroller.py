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
from api.models import GroupFile,Group,GroupMember,SubCategory,Gig,GigFile,GigMember,Package,PackageDetail,Order,Invitation
#from chat.models import ChatGroup,ChatMessage
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse,CheckNullable,random_str,random_number
from django.core.serializers.json import DjangoJSONEncoder
from api.infra.modelserializers.groupserializers import GroupGetSerializer,GroupGetListSerializer,FileSerializer,InvitationSerializer
from api.infra.modelserializers.gigserializers import GigGetSerializer,GigFileSerializer,PackageSerializer,PackageDetailSerializer,GigFullGetSerializer
from rest_framework.decorators import api_view
from django.core.files import File
from django.conf import settings
from twilio.rest import Client
import requests
import asyncio


# Done
@csrf_exempt
@api_view(['POST'])
def AddGroup(request):
    try:
        data = json.loads(request.body)
        check = (Check(data, ['name', 'description', 'instalink', 'websitelink', 'icon']) & Check(request.headers,
                                                                                                  ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
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
        icon = None
        if request.FILES['icon'] is not None:
            icon = request.FILES['icon']
        group = Group.objects.create(name=name, description=description, instalink=insta, website=website,icon=icon)
        groupmember = GroupMember.objects.create(freelancer=freelancer, group=group, isadmin=True, role="Owner",
                                                 share=100.0)
        context = {}
        context['Message'] = "گروه با موفقیت ساخته شد"
        temp = GroupGetListSerializer(groupmember,context={'totalrevenue':None}).data
        context['Group'] = (GroupGetSerializer(group,context={'members':temp})).data
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
            gf.save()
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


@csrf_exempt
@api_view(['POST'])
def GetGroupList(request):
    try:
        check = Check(request.headers,['token'])
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
        groupmembers = GroupMember.objects.filter(freelancer=freelancer).all()
        context = []
        totalrevenue = 0
        for temp in groupmembers:
            for gig, date, share in GigMember.objects.filter(groupmember=temp).values_list('gig', 'datejoin', 'share'):
                orders = Order.objects.filter(package__gig=gig, ispaid=True, date__gte=date).all()
                for order in orders:
                    totalrevenue = totalrevenue + (order.package.price * (share / 100))
            test = GroupGetListSerializer(temp, context={'totalrevenue': totalrevenue})
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
            'data': 'ساخت گیگ با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def GetGroupDetails(request):
    try:
        data = request.data
        check = Check(data, ['groupid'])
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        group = Group.objects.filter(id=data['groupid']).first()
        if not group:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موجود نمیباشد'
            }, encoder=JSONEncoder)
        context = []
        members = GroupMember.objects.filter(group=group).all()
        list = []
        for member in members:
            list.append(GroupGetListSerializer(member, context={'totalrevenue': None}).data)
        context.append((GroupGetSerializer(group,context={'members':list})).data)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساخت گیگ با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def UpdateGroupInfo(request):
    try:
        data = request.data
        check = (Check(data, ['groupid','name','description','successfulnumbers','website','instalink']) & Check(request.headers,['token']))
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
        group = Group.objects.filter(id=data['groupid']).first()
        if not group:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موردنظر موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        admin = GroupMember.objects.filter(group=group, isadmin=True).first().freelancer
        if not (admin == freelancer):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دسترسی غیر مجاز'
            }, encoder=JSONEncoder, status=400)
        if (data['name'] != None) | (data['name'] != ""):
            if Group.objects.filter(name=data['name']).exists():
                return JsonResponse({
                    'success': False,
                    'code': '400',
                    'data': 'گروهی با این نام قبلا ثبت شده است'
                }, encoder=JSONEncoder, status=400)
        group.name = BlankOrElse(group.name, data['name'])
        group.description = BlankOrElse(group.description, data['description'])
        group.successfulnumbers = BlankOrElse(group.successfulnumbers, data['successfulnumbers'])
        group.website = BlankOrElse(group.website, data['website'])
        group.instalink = BlankOrElse(group.instalink, data['instalink'])
        group.save()
        context = []
        members = GroupMember.objects.filter(group=group).all()
        list = []
        for member in members:
            list.append(GroupGetListSerializer(member, context={'totalrevenue': None}).data)
        context.append((GroupGetSerializer(group, context={'members': list})).data)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'بروزرسانی گروه با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def GetGroupFiles(request):
    try:
        data = request.data
        check = Check(data, ['groupid'])
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        group = Group.objects.filter(id=data['groupid']).first()
        if not group:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروه موردنظر موجود نمیباشد'
            }, encoder=JSONEncoder, status=400)
        files = GroupFile.objects.filter(group=group).all()
        context = []
        for file in files:
            temp = FileSerializer(file,context={'description':file.description})
            context.append(temp.data)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'دریافت فایل با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def AddInvitation(request): # Send Invitation From Group Owner To Other Freelancers To Join The Group
    try:
        data = json.loads(request.body)
        check = (Check(data, ['membertoken', 'content', 'groupid', 'role']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        ownertoken = data['token']
        membertoken = data['membertoken']
        content = data['content']
        groupid = data['groupid']
        role = data['role']
        CheckNullable([ownertoken,membertoken,content,groupid,role],'ّتمامی ورودی ها باید مقدار داشته باشند لطفا دقت فرمایید')
        result, groupowner = GetObjByToken(ownertoken)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر پیدا نشد'
            }, encoder=JSONEncoder)
        gm = GroupMember.objects.filter(freelancer__token=ownertoken,isadmin=True).first()
        if not gm | gm.group.id != groupid:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'گروهی با مشخصات ارسالی پیدا نشد و یا فریلنسر درسترسی ندارد'
            }, encoder=JSONEncoder)
        result, freelancertoadd = GetObjByToken(membertoken)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر پیدا نشد'
            }, encoder=JSONEncoder)
        referenceid = random_number(10)
        while Invitation.objects.filter(reference=referenceid).exists():
            referenceid = random_number(10)
        invit = Invitation.objects.create(group=gm.group,receiver=freelancertoadd,content=content,role=role,reference=referenceid)
        context = {}
        context['Message'] = "دعوتنامه با موفقیت ساخته شد"
        context["ReferenceId"] = invit.reference
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت دعوتنامه با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def GetInvitations(request): # Send Invitation From Group Owner To Other Freelancers To Join The Group
    try:
        data = json.loads(request.body)
        check = Check(request.headers, ['token'])
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        token = data['token']
        CheckNullable([token],'ّتمامی ورودی ها باید مقدار داشته باشند لطفا دقت فرمایید')
        result, freelancer = GetObjByToken(token)
        if (result):
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'فریلنسر پیدا نشد'
            }, encoder=JSONEncoder)
        invits = Invitation.objects.filter(receiver=freelancer).all()
        context = []
        for invit in invits:
            obj = InvitationSerializer(invit)
            context.append(obj.data)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت دعوتنامه با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
def ProcessInvitation(request): # Accept Or Reject An Invitations
    try:
        data = json.loads(request.body)
        check = (Check(data, ['reference','operation']) & Check(request.headers, ['token']))
        if not (check is True):
            return check
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ساختار ارسال داده درست نمیباشد'
        }, encoder=JSONEncoder, status=400)
    try:
        token = data['token']
        referenceid = data['reference']
        operation = bool(data['operation'])
        CheckNullable([token,referenceid,operation],'ّتمامی ورودی ها باید مقدار داشته باشند لطفا دقت فرمایید')
        invit = Invitation.objects.filter(reference=referenceid).first()
        if not invit:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دعوتنامه ای با این رفرنس پیدا نشد'
            }, encoder=JSONEncoder, status=400)
        if invit.receiver.token != token:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'دعوتنامه برای شما نمیباشد, دسترسی غیر مجاز'
            }, encoder=JSONEncoder, status=400)
        if operation: # If Operation Was True It Means Accepting Invitation And Adding To Group
            GroupMember.objects.create(freelancer=invit.receiver,group=invit.group,role=invit.role)
            GroupMember.save()
            invit.delete()
            Invitation.save()
            return JsonResponse({
                'success': True,
                'code': '200',
                'data': 'قبول دعوتنامه و افزودن فریلنسر به گروه با موفقیت انجام شد'
            }, encoder=JSONEncoder)
        invit.delete()
        Invitation.save()
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': 'رد دعوتنامه با موفقیت انجام شد'
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ثبت یا رد دعوتنامه با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)
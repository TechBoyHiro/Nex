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
from api.models import Shop,Order,Review,Package,Gig,GigMember,Group,GroupMember
#from chat.models import ChatGroup,ChatMessage
from django.utils.timezone import make_aware
from api.infra.infrastructure import GetObjByToken,CheckToken,Check,BlankOrElse,CheckNullable
from django.core.serializers.json import DjangoJSONEncoder
from api.infra.modelserializers.generalserializers import SuccessOrderSerializer
from api.infra.modelserializers.gigserializers import GigGetSerializer
from rest_framework.decorators import api_view
from django.core.files import File
from django.conf import settings
from twilio.rest import Client
from django.shortcuts import redirect
import requests
import asyncio


MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
CallbackURL = 'http://localhost:8000/api/order/verify/'
ChatSERVER = "http://localhost:8088/api/room/addorder/"


@csrf_exempt
@api_view(['POST'])
def NewOrder(request): # Add A New Order For Shop/User
    try:
        data = json.loads(request.body)
        check = (Check(data, ['packageid','description']) & Check(request.headers, ['token']))
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
        packageid = data['packageid']
        description = data['description']
        CheckNullable([token,packageid], 'ّلطفا آیدی پکیج را وارد کنید')
        shop = Shop.objects.filter(token__token=token).first()
        if not shop:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'کاربر پیدا نشد'
            }, encoder=JSONEncoder)
        package = Package.objects.filter(id=packageid).first()
        if not package:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'پکیج پیدا نشد'
            }, encoder=JSONEncoder)
        deliverytime = datetime.now() + timedelta(days=package.deliverytime)
        order = Order.objects.create(shop=shop,package=package,deliverytime=deliverytime,description=description)
        req_data = {
            "merchant_id": MERCHANT,
            "amount": package.price,
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": shop.phone, "email": shop.user.email}
        }
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        authority = req.json()['data']['authority']
        order.description = authority
        if len(req.json()['errors']) == 0:
            return redirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return JsonResponse({
                'success': False,
                'code': e_code,
                'data': e_message
            }, encoder=JSONEncoder, status=e_code)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'ایجاد سفارش با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


@csrf_exempt
@api_view(['POST'])
async def VerifyPayment(request):
    try:
        t_status = request.GET.get('Status')
        t_authority = request.GET['Authority']
        if request.GET.get('Status') == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            order = Order.objects.filter(ispaid=False,description=t_authority).get()
            req_data = {
                "merchant_id": MERCHANT,
                "amount": order.package.price,
                "authority": t_authority
            }
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100:
                    referenceID = req.json()['data']['ref_id']
                    message = req.json()['data']['message']
                    cardnumber = req.json()['data']['card_pan']
                    order.ispaid = True
                    order.tracknumber = referenceID
                    order.description = message
                    order.cardnumber = cardnumber
                    order.save()
                    loop = asyncio.get_event_loop()
                    loop.create_task(CreateOrderChatGroup(order))
                    await asyncio.wait(loop)
                    loop.close()
                    return JsonResponse({
                        'success': True,
                        'code': '200',
                        'data': SuccessOrderSerializer(order).data
                    }, encoder=JSONEncoder, status=200)
                elif t_status == 101:
                    return JsonResponse({
                        'success': True,
                        'code': '200',
                        'data': req.json()['data']['message']
                    }, encoder=JSONEncoder, status=200)
                else:
                    return JsonResponse({
                        'success': True,
                        'code': '200',
                        'data': req.json()['data']['message']
                    }, encoder=JSONEncoder, status=200)
            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return JsonResponse({
                    'success': False,
                    'code': e_code,
                    'data': e_message
                }, encoder=JSONEncoder, status=400)
        else:
            return JsonResponse({
                'success': False,
                'code': '400',
                'data': 'درخواست پرداخت با مشکل مواجه شد و یا توسط کاربر لغو گردید'
            }, encoder=JSONEncoder, status=400)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': 'درخواست پرداخت با مشکل مواجه شد'
        }, encoder=JSONEncoder, status=400)


async def CreateOrderChatGroup(order):
    gig = order.package.gig
    gigmems = GigMember.objects.filter(gig=gig).all()
    tokens = []
    for gigmem in gigmems:
        tokens.append(gigmem.groupmember.freelancer.token)
    req_body = {"ordertrack": order.tracknumber, "deliverytime": order.deliverytime, "date": order.date, "description": order.description,
            "tokens":tokens}
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    temp = requests.post(ChatSERVER, data=json.dumps(req_body), headers=req_header)
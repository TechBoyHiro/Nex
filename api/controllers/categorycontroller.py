from django.http import JsonResponse
from datetime import datetime , timedelta
import json
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
from api.models import Category,SubCategory
from rest_framework.decorators import api_view
from api.infra.infrastructure import Check,CheckToken,GetObjByToken


@csrf_exempt
@api_view(['GET'])
def GetAll(request):
    try:
        categories = Category.objects.all()
        context = []
        for category in categories:
            subcategories = SubCategory.objects.filter(category=category).all()
            subcontext = []
            for subcat in subcategories:
                icon = None
                if subcat.icon:
                    icon = subcat.icon.path
                sub = {'id':subcat.id,'name':subcat.name,'description':subcat.description,'icon':icon}
                subcontext.append(sub)
            caticon = None
            if category.icon:
                caticon = category.icon.path
            cat = {'id':category.id,'name':category.name,'description':category.description,'icon':caticon,
                   'subcategories':subcontext}
            context.append(cat)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': "دسته بندی پیدا نشد"
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['GET'])
def GetCategories(request):
    try:
        categories = Category.objects.all()
        context = []
        for category in categories:
            caticon = None
            if category.icon:
                caticon = category.icon.path
            cat = {'id':category.id,'name':category.name,'description':category.description,'icon':caticon}
            context.append(cat)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': "دسته بندی پیدا نشد"
        }, encoder=JSONEncoder)


@csrf_exempt
@api_view(['GET'])
def GetSubcategories(request):
    data = json.loads(request.body)
    check = Check(data, ['id'])
    if not (check is True):
        return check
    try:
        category = Category.objects.filter(id=data['id']).get()
        context = []
        for subcat in SubCategory.objects.filter(category=category).all():
            icon = None
            if subcat.icon:
                icon = subcat.icon.path
            sub = {'id': subcat.id, 'name': subcat.name, 'description': subcat.description, 'icon': icon}
            context.append(sub)
        return JsonResponse({
            'success': True,
            'code': '200',
            'data': context
        }, encoder=JSONEncoder)
    except:
        return JsonResponse({
            'success': False,
            'code': '400',
            'data': "زیر دسته بندی پیدا نشد"
        }, encoder=JSONEncoder)
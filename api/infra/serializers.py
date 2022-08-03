from rest_framework import serializers
from api.models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description']
    icon = serializers.FilePathField()
from rest_framework import serializers
from api.models import Order


class SuccessOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('ispaid','tracknumber','description','cardnumber')
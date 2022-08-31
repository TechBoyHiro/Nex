from rest_framework import serializers
from api.models import Group,GroupMember,GroupFile,Order


class GroupGetSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField("get_groupname")
    subcats = serializers.SerializerMethodField("get_subcats")

    def get_groupname(self,group):
        return group.name

    def get_subcats(self,group):
        string = ""
        for subcat in group.subcategories.all():
            string = string + subcat.name + ","
        return string

    class Meta:
        model = Group
        fields = ('groupname','description','rate','successfulnumbers','datejoin','website','instalink','isapproved','icon','subcats')


class GroupGetListSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField("get_groupname")
    totalrevenue = serializers.SerializerMethodField("set_revenue")
    groupid = serializers.SerializerMethodField("get_id")

    def get_groupname(self,groupmember):
        return groupmember.group.name

    def set_revenue(self,groupmember):
        return self.context['totalrevenue']

    def get_id(self,groupmember):
        return groupmember.id

    class Meta:
        model = GroupMember
        fields = ('groupname','groupid','isadmin','datejoin','role','totalrevenue')

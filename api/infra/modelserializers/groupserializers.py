from rest_framework import serializers
from api.models import Group,GroupMember,GroupFile,Order,Invitation


class GroupGetSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField("get_groupname")
    subcats = serializers.SerializerMethodField("get_subcats")
    followers = serializers.SerializerMethodField("get_followers")
    members = serializers.SerializerMethodField("get_members")

    def get_groupname(self,group):
        return group.name

    def get_subcats(self,group):
        string = ""
        for subcat in group.subcategories.all():
            string = string + subcat.name + ","
        return string

    def get_followers(self,group):
        return len(group.followers.all())

    def get_members(self,group):
        return self.context['members']

    class Meta:
        model = Group
        fields = ('id','groupname','description','rate','successfulnumbers','datejoin','website','instalink','isapproved','icon','subcats','followers','members')


class GroupGetListSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField("get_groupname")
    totalrevenue = serializers.SerializerMethodField("set_revenue")
    groupid = serializers.SerializerMethodField("get_id")
    name = serializers.SerializerMethodField("get_name")

    def get_groupname(self,groupmember):
        return groupmember.group.name

    def set_revenue(self,groupmember):
        return self.context['totalrevenue']

    def get_id(self,groupmember):
        return groupmember.group.id

    def get_name(self,groupmember):
        return groupmember.freelancer.name

    class Meta:
        model = GroupMember
        fields = ('id','name','groupname','groupid','isadmin','datejoin','role','totalrevenue')


class FileSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField("get_description")

    def get_description(self,groupfile):
        return self.context['description']

    class Meta:
        model = GroupFile
        fields = ('id','file','description')


class InvitationSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField("get_groupname")

    def get_groupname(self,invit):
        return invit.group.name

    class Meta:
        model = Invitation
        fields = ('groupname','content','role','date','reference')

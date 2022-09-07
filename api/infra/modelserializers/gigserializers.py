from rest_framework import serializers
from api.models import Gig,GigFile,GigMember,Group,GroupMember,GroupFile,Order


class GigGetSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField("get_image")
    groupname = serializers.SerializerMethodField("get_groupname")
    grouprate = serializers.SerializerMethodField("get_grouprate")
    groupisapproved = serializers.SerializerMethodField("get_groupisapproved")
    myshare = serializers.SerializerMethodField("get_myshare")
    myrole = serializers.SerializerMethodField("get_myrole")

    def get_image(self,gig):
        return self.context['image']

    def get_groupname(self,gig):
        return gig.group.name

    def get_grouprate(self,gig):
        return gig.group.rate

    def get_groupisapproved(self,gig):
        return gig.group.isapproved

    def get_myshare(self,gig):
        return self.context['myshare']

    def get_myrole(self,gig):
        return self.context['myrole']

    class Meta:
        model = Gig
        fields = ('title','description','rate','leastprice','image','groupname','grouprate','groupisapproved','myshare','myrole')
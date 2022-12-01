from rest_framework import serializers
from api.models import Gig,GigFile,GigMember,Group,GroupMember,GroupFile,Order,Package,PackageDetail


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


class GigFullGetSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField("get_images")
    groupname = serializers.SerializerMethodField("get_groupname")
    grouprate = serializers.SerializerMethodField("get_grouprate")
    groupisapproved = serializers.SerializerMethodField("get_groupisapproved")
    packages = serializers.SerializerMethodField("get_packages")

    def get_images(self,gig):
        return self.context['images']

    def get_packages(self,gig):
        return self.context['packages']

    def get_groupname(self,gig):
        return gig.group.name

    def get_grouprate(self,gig):
        return gig.group.rate

    def get_groupisapproved(self,gig):
        return gig.group.isapproved

    class Meta:
        model = Gig
        fields = ('title','description','rate','leastprice','images','groupname','grouprate','groupisapproved','packages')


class GigFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = GigFile
        fields = ('file','priority')


class PackageSerializer(serializers.ModelSerializer):
    packagedetails = serializers.SerializerMethodField("get_packagedetails")

    def get_packagedetails(self,package):
        return self.context['packagedetails']

    class Meta:
        model = Package
        fields = ('id','name','description','price','deliverytime','numberofrevisions','packagedetails')


class PackageDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PackageDetail
        fields = ('key','value')
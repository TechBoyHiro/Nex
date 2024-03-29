from django.contrib import admin
from .models import *

# Register your models here.


class TokenAdmin(admin.ModelAdmin):
    search_fields = ['token']

    class Meta:
        model = Token




class FreelancerAdmin(admin.ModelAdmin):
    search_fields = ['name']

    class Meta:
        model = Freelancer


admin.site.register(Token,TokenAdmin) #
admin.site.register(Freelancer,FreelancerAdmin) #
admin.site.register(City) #
admin.site.register(GigMember) #
admin.site.register(GroupFile) #
admin.site.register(Category) #
admin.site.register(SubCategory) #
admin.site.register(BusinessType) #
admin.site.register(Shop) #
admin.site.register(Group) #
admin.site.register(GroupMember) #
admin.site.register(Gig) #
admin.site.register(GigFile) #
admin.site.register(Tag) #
admin.site.register(Order) #
admin.site.register(Review) #
admin.site.register(Package) #
admin.site.register(PackageDetail) #
admin.site.register(SMS) #

from django.contrib import admin
from .models import *

# Register your models here.


class TokenAdmin(admin.ModelAdmin):
    search_fields = ['token']

    class Meta:
        model = Token


class MainUserAdmin(admin.ModelAdmin):
    search_fields = ['user__username','phone']

    class Meta:
        model = MainUser


class FreelancerAdmin(admin.ModelAdmin):
    search_fields = ['name']

    class Meta:
        model = Freelancer


admin.site.register(Token,TokenAdmin)
admin.site.register(MainUser,MainUserAdmin)
admin.site.register(Freelancer,FreelancerAdmin)
admin.site.register(City)
admin.site.register(FreeFile)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Work)
admin.site.register(WorkFile)
admin.site.register(Tag)
admin.site.register(Package)
admin.site.register(PackageDetail)
admin.site.register(SMS)

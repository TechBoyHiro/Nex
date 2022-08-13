from django.urls import re_path
from .controllers import shopcontroller,freelancercontroller

urlpatterns = [
    # USER PATHS
    re_path(r'user/add/$', shopcontroller.RegisterShop, name="User Registration"),
    re_path(r'user/login/$', shopcontroller.Login, name="User Login"),
    re_path(r'user/get/$', shopcontroller.GetEntity, name="Get User Info"),
    re_path(r'user/update/$', shopcontroller.UpdateUser, name="Update User Info"),
    re_path(r'user/sms/$', shopcontroller.SendSMS, name="Two-Factor Authentication"),
    re_path(r'user/check/$', shopcontroller.CheckSMS, name="Check Two-Factor Authentication"),
    #re_path(r'user/getchats/$', usercontroller.GetChatGroups, name="Get User Chat Groups"),
    # CATEGORY PATHS
    #re_path(r'category/getall/$', categorycontroller.GetAll, name="Get All"),
    #re_path(r'category/getcat/$', categorycontroller.GetCategories, name="Get All Categories"),
    #re_path(r'category/getsub/$', categorycontroller.GetSubcategories, name="Get Subcategories Of A Category"),
    # Freelancer PATHS
    re_path(r'freelancer/add/$', freelancercontroller.RegisterFreelancer, name="Freelancer Registration"),
    re_path(r'freelancer/update/$', freelancercontroller.Update, name="Update Freelancer Info"),
    re_path(r'freelancer/login/$', freelancercontroller.Login, name="Freelancer Login"),
    re_path(r'freelancer/get/$', shopcontroller.GetEntity, name="Get Freelancer Info"),
    # Gig PATHS
    #re_path(r'gig/add/$', gigcontroller.AddGig, name="Add Gig"),
    #re_path(r'gig/addfiles/$', gigcontroller.AddGigFile, name="Add File To A Gig"),
    #re_path(r'gig/addpack/$', gigcontroller.AddGigPackage, name="Add Package To A Gig"),
]
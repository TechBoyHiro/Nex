from django.urls import re_path
from .controllers import shopcontroller,freelancercontroller,groupcontroller,categorycontroller

urlpatterns = [
    # Shop PATHS
    re_path(r'shop/add/$', shopcontroller.RegisterShop, name="User Registration"),
    re_path(r'shop/login/$', shopcontroller.Login, name="User Login"),
    re_path(r'shop/get/$', shopcontroller.GetShop, name="Get User Info"),
    #re_path(r'shop/update/$', shopcontroller.UpdateUser, name="Update User Info"),
    #re_path(r'user/sms/$', shopcontroller.SendSMS, name="Two-Factor Authentication"),
    #re_path(r'user/check/$', shopcontroller.CheckSMS, name="Check Two-Factor Authentication"),
    #re_path(r'user/getchats/$', usercontroller.GetChatGroups, name="Get User Chat Groups"),
    # CATEGORY PATHS
    re_path(r'category/getall/$', categorycontroller.GetAll, name="Get All"),
    re_path(r'category/getcat/$', categorycontroller.GetCategories, name="Get All Categories"),
    re_path(r'category/getsub/$', categorycontroller.GetSubcategories, name="Get Subcategories Of A Category"),
    # Freelancer PATHS
    re_path(r'freelancer/add/$', freelancercontroller.RegisterFreelancer, name="Freelancer Registration"),
    re_path(r'freelancer/update/$', freelancercontroller.Update, name="Update Freelancer Info"),
    re_path(r'freelancer/login/$', freelancercontroller.Login, name="Freelancer Login"),
    re_path(r'freelancer/get/$', freelancercontroller.GetFreelancer, name="Get Freelancer Info"),
    # Gig PATHS
    #re_path(r'gig/add/$', gigcontroller.AddGig, name="Add Gig"),
    #re_path(r'gig/addfiles/$', gigcontroller.AddGigFile, name="Add File To A Gig"),
    #re_path(r'gig/addpack/$', gigcontroller.AddGigPackage, name="Add Package To A Gig"),
    # Group PATHS
    re_path(r'group/add/$', groupcontroller.AddGroup, name="Add Group"),
    re_path(r'group/addsubcat/$', groupcontroller.AddGroupSubcat, name="Add Subcategories To A Group"),
    re_path(r'group/addfiles/$', groupcontroller.AddGroupFiles, name="Add Files To A Group"),
    re_path(r'group/addgig/$', groupcontroller.AddGroupGig, name="Add Gig To A Group"),
    re_path(r'group/addpackage/$', groupcontroller.AddGigPackage, name="Add Package To A Gig"),
    re_path(r'group/addgigmember/$', groupcontroller.AddGigMember, name="Add GroupMember To A Gig"),
]
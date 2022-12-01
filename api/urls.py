from django.urls import re_path
from .controllers import shopcontroller,freelancercontroller,groupcontroller,categorycontroller,searchcontroller,gigcontroller,ordercontroller

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
    re_path(r'freelancer/addresume/$', freelancercontroller.AddFreelancerResume, name="Add Freelancer Resume"),
    # Group PATHS
    re_path(r'group/add/$', groupcontroller.AddGroup, name="Add Group"),
    re_path(r'group/addsubcat/$', groupcontroller.AddGroupSubcat, name="Add Subcategories To A Group"),
    re_path(r'group/addfiles/$', groupcontroller.AddGroupFiles, name="Add Files To A Group"),
    re_path(r'group/getgroups/$', groupcontroller.GetGroupList, name="Get Freelancer Groups"),
    re_path(r'group/get/$', groupcontroller.GetGroupDetails, name="Get Group Information"),
    re_path(r'group/updateinfo/$', groupcontroller.UpdateGroupInfo, name="Update Group Information"),
    re_path(r'group/getfiles/$', groupcontroller.GetGroupFiles, name="Get Group Files (Certificates)"),
    # Gig PATHS
    re_path(r'group/addgig/$', gigcontroller.AddGig, name="Add Gig To A Group"),
    re_path(r'group/gig/$', gigcontroller.GetGig, name="Get Gig Full Details"),
    re_path(r'group/getgigs/$', gigcontroller.GetGroupGigs, name="Get Group Gigs"),
    re_path(r'group/addpackage/$', gigcontroller.AddGigPackage, name="Add Package To A Gig"),
    re_path(r'group/addgigmember/$', gigcontroller.AddGigMember, name="Add GroupMember To A Gig"),
    # Invitation PATHS
    re_path(r'group/addinvit/$', groupcontroller.AddInvitation, name="Invite a Freelancer To Join To Group"),
    re_path(r'group/processinvit/$', groupcontroller.ProcessInvitation, name="Accept Or Reject An Invitation"),
    re_path(r'group/getinvit/$', groupcontroller.GetInvitations, name="Get All Freelancer Invitations"),
    # Search PATHS
    re_path(r'search/gigsbysubcat/$', searchcontroller.GigsBySubcat, name="Get Gigs In Given Subcat"),
    re_path(r'search/gigsbytag/$', searchcontroller.GigsByTag, name="Get Gigs Related To Given Tag"),
    # Order PATHS
    re_path(r'order/new/$', ordercontroller.NewOrder, name="Initialize A New Order"),
    re_path(r'order/verify/$', ordercontroller.VerifyPayment, name="Verify A Payment"),
]
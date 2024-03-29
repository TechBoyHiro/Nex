import sys
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,date

# MODELS =>

# Done
class Token(models.Model): # token assigns to every user
    token = models.CharField(max_length=128)
    validdate = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return str(self.id) + ' ** ' + self.token + ' ** ' + str(self.validdate)

# Done
class Category(models.Model):
    name = models.TextField()
    description = models.TextField()
    icon = models.ImageField(upload_to='CategoryIcons/',blank=True,null=True)

    def __str__(self):
        return str(self.id) + ' ** ' + self.name + ' ** ' + self.description

# Done
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    name = models.TextField()
    description = models.TextField()
    icon = models.ImageField(upload_to='SubCategoryIcons/', blank=True, null=True)

    def __str__(self):
        return str(self.id) + ' ** ' + self.name + ' ** ' + self.description

# Done
class BusinessType(models.Model):
    subcategories = models.ManyToManyField(SubCategory,blank=True,null=True)
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return str(self.id) + ' ** ' + self.name

# Done
class Shop(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    token = models.OneToOneField(Token,on_delete=models.RESTRICT,null=True)
    businesstype = models.ForeignKey(BusinessType,on_delete=models.RESTRICT,blank=True,null=True)
    name = models.CharField(max_length=60)
    address = models.TextField()
    phone = models.CharField(max_length=11)
    profilepic = models.ImageField(upload_to='ShopProfiles/',blank=True,null=True)
    datejoin = models.DateField(default=date.today())
    instalink = models.TextField()
    website = models.TextField()
    description = models.TextField()

    def __str__(self):
        return str(self.id) + ' ** ' + self.user.username + ' ** ' + self.phone + ' ** ' + self.token.token

# Done
class City(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()


# Done
class Freelancer(models.Model):
    token = models.OneToOneField(Token,on_delete=models.RESTRICT,null=True)
    city = models.ForeignKey(City,on_delete=models.RESTRICT,blank=True,null=True)
    subcat = models.ForeignKey(SubCategory,on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=25)
    description = models.TextField()
    password = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    address = models.TextField()
    datejoin = models.DateField(default=date.today())
    profilepic = models.ImageField(upload_to='FreelancerProfiles/',blank=True,null=True)
    linkedin = models.TextField(blank=True,null=True)
    resume = models.FileField(upload_to='FreelancerResumes/',blank=True,null=True)
    isauthenticated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' ** ' + self.name + ' ** ' + self.token.token + ' ** ' + self.phone

# Done
class Group(models.Model):
    subcategories = models.ManyToManyField(SubCategory,blank=True,null=True)
    followers = models.ManyToManyField(Shop,blank=True,null=True)
    name = models.CharField(max_length=20)
    description = models.TextField()
    rate = models.FloatField(default=2.5)
    successfulnumbers = models.IntegerField(default=0)
    datejoin = models.DateField(default=date.today())
    website = models.TextField()
    instalink = models.TextField()
    isapproved = models.BooleanField(default=False)
    icon = models.ImageField(upload_to='GroupIcons/',blank=True,null=True)

    def __str__(self):
        return str(self.id) + ' ** ' + self.name

# Done
class GroupMember(models.Model):
    freelancer = models.ForeignKey(Freelancer,on_delete=models.RESTRICT)
    group = models.ForeignKey(Group,on_delete=models.RESTRICT)
    isadmin = models.BooleanField(default=False)
    datejoin = models.DateField(default=date.today())
    role = models.TextField()
    share = models.FloatField(blank=True,null=True)

    def __str__(self):
        return str(self.id) + ' ** ' + self.freelancer.name + ' ** ' + self.group.name

# Done
class GroupFile(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    file = models.FileField(upload_to='GroupFiles/')
    description = models.TextField()

    def __str__(self):
        return str(self.id) + ' ** ' + self.group.name + ' ** ' + self.description

# Done
class Gig(models.Model):
    group = models.ForeignKey(Group,on_delete=models.RESTRICT)
    subcat = models.ForeignKey(SubCategory,on_delete=models.RESTRICT)
    title = models.CharField(max_length=20)
    description = models.TextField()
    rate = models.FloatField(default=2.5)
    leastprice = models.FloatField(default=10)

    def __str__(self):
        return str(self.id) + ' ** ' + self.title + ' ** ' + self.group.name

# Done
class GigFile(models.Model):
    gig = models.ForeignKey(Gig,on_delete=models.RESTRICT)
    file = models.FileField(upload_to='GigFiles/')
    priority = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id) + ' ** ' + self.gig.title + ' ** ' + str(self.priority)

# Done
class GigMember(models.Model):
    groupmember = models.ForeignKey(GroupMember,on_delete=models.CASCADE)
    gig = models.ForeignKey(Gig,on_delete=models.CASCADE)
    isadmin = models.BooleanField(default=False)
    datejoin = models.DateField(default=date.today())
    role = models.TextField()
    share = models.FloatField(blank=True,null=True)

    def __str__(self):
        return str(self.id) + ' ** ' + self.groupmember.freelancer.name + ' ** ' + self.gig.title


class Invitation(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    receiver = models.ForeignKey(Freelancer,on_delete=models.CASCADE)
    content = models.TextField()
    role = models.TextField()
    date = models.DateField(default=date.today())
    reference = models.TextField(max_length=10,blank=True,null=True)

# Done
class Package(models.Model):
    gig = models.ForeignKey(Gig,on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    description = models.TextField()
    price = models.FloatField(default=0)
    deliverytime = models.IntegerField(default=1)
    numberofrevisions = models.IntegerField(default=1)

    def __str__(self):
        return str(self.price) + ' ** ' + self.name + ' ** ' + self.gig.title


# Done
class PackageDetail(models.Model):
    package = models.ForeignKey(Package,on_delete=models.CASCADE)
    key = models.TextField()
    value = models.TextField()

    def __str__(self):
        return self.key + ' ** ' + self.value + ' ** ' + self.package.name


# Done
class Order(models.Model):
    shop = models.ForeignKey(Shop,on_delete=models.RESTRICT)
    package = models.ForeignKey(Package,on_delete=models.RESTRICT)
    deliverytime = models.DateField(default=date.today()) # It's todays date + package's delivery time
    date = models.DateTimeField(default=datetime.now())
    ispaid = models.BooleanField(default=False)
    tracknumber = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    cardnumber = models.TextField(blank=True,null=True)


# Done
class Review(models.Model):
    order = models.ForeignKey(Order,on_delete=models.RESTRICT)
    Package = models.ForeignKey(Package,on_delete=models.RESTRICT)
    rate = models.FloatField(default=2.5)
    description = models.CharField(max_length=100)
    date = models.DateField(default=date.today())


# Done
class Tag(models.Model):
    gigs = models.ManyToManyField(Gig,blank=True,null=True)
    name = models.TextField()

    def __str__(self):
        return self.name


# Done
class SMS(models.Model):
    sms = models.CharField(max_length=5)
    phone = models.CharField(max_length=11)
    issued = models.DateTimeField(default=datetime.now())
    valid = models.DateTimeField(default=datetime.now())










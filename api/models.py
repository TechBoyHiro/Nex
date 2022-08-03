import sys
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# UPWORK MODELS =>


class Token(models.Model): # token assigns to every user
    token = models.CharField(max_length=128)
    validdate = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.token + ' ** ' + str(self.validdate)


class MainUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    nationalcode = models.CharField(max_length=10,blank=True,null=True)
    age = models.IntegerField(default=0)
    phone = models.CharField(max_length=11)
    profilepic = models.ImageField(upload_to='UserProfiles',blank=True,null=True)
    isauthenticated = models.BooleanField(default=False)
    datejoin = models.DateTimeField(default=datetime.now())
    token = models.OneToOneField(Token,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.user.username + ' ** ' + self.phone + ' ** ' + self.token.token


class SMS(models.Model):
    sms = models.CharField(max_length=5)
    phone = models.CharField(max_length=11)
    issued = models.DateTimeField(default=datetime.now())
    valid = models.DateTimeField(blank=True,null=True)


class City(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name + ' ** ' + self.description


class Category(models.Model):
    name = models.TextField()
    description = models.TextField()
    icon = models.ImageField(upload_to='CategoryIcons',blank=True,null=True)

    def __str__(self):
        return self.name + ' ** ' + self.description


class Freelancer(models.Model):
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True,null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True)
    password = models.TextField(blank=True,null=True)
    token = models.OneToOneField(Token,on_delete=models.SET_NULL,null=True)
    email = models.EmailField(blank=True,null=True)
    age = models.IntegerField(blank=True,null=True)
    phone = models.CharField(max_length=11,blank=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    rate = models.FloatField(default=0.0)
    level = models.IntegerField(default=1)
    datejoin = models.DateTimeField(default=datetime.now())
    profilepic = models.ImageField(upload_to='FreelancerProfiles',blank=True,null=True)
    numberofjobs = models.IntegerField(default=0)

    def __str__(self):
        return self.name + ' ** ' + self.token.token + ' ** ' + self.phone


class FreeFile(models.Model):
    file = models.FileField(upload_to='FreeFiles')
    freelancer = models.ForeignKey(Freelancer,on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.freelancer.name + ' ** ' + self.description


class SubCategory(models.Model):
    name = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='SubCategoryIcons', blank=True, null=True)

    def __str__(self):
        return self.name + ' ** ' + self.description


class Work(models.Model):
    title = models.TextField()
    description = models.TextField()
    freelancer = models.ForeignKey(Freelancer,on_delete=models.CASCADE)
    rate = models.FloatField(default=0.0)
    numberofrates = models.IntegerField(default=0)
    leastprice = models.IntegerField(default=10)
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' ** ' + self.freelancer.name


class WorkFile(models.Model):
    file = models.FileField(upload_to='WorkFiles')
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.work.title + ' ** ' + str(self.priority)


class Tag(models.Model):
    name = models.TextField()
    works = models.ManyToManyField(Work)

    def __str__(self):
        return self.name


class Package(models.Model):
    title = models.TextField()
    description = models.TextField(blank=True,null=True)
    price = models.FloatField()
    work = models.ForeignKey(Work,on_delete=models.CASCADE)
    deliverytime = models.IntegerField(default=1)
    numberofrevisions = models.IntegerField(default=1)

    def __str__(self):
        return str(self.price) + ' ** ' + self.title + ' ** ' + self.work.title


class PackageDetail(models.Model):
    key = models.TextField()
    value = models.TextField()
    package = models.ForeignKey(Package,on_delete=models.CASCADE)

    def __str__(self):
        return self.key + ' ** ' + self.value + ' ** ' + self.package.title







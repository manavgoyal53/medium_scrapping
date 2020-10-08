from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    keyword = models.CharField(max_length=30)

class SearchHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE,default=None)
    datetime = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    url = models.TextField()
    author = models.CharField(max_length=60)
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    responses = models.CharField(max_length=15)
    claps = models.CharField(max_length=15)
    tags = models.ManyToManyField(Tag)

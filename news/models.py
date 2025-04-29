from django.db import models
from django.contrib.auth.models import User  # For user management

# Create your models here.

class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    country = models.CharField(max_length=50, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=50)

class Article(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    url = models.URLField()
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField()
    sentiment = models.CharField(max_length=20, blank=True)
    summary = models.TextField(blank=True)
    is_fake = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.ManyToManyField(Category, blank=True)
    reading_history = models.ManyToManyField(Article, blank=True)

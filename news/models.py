from django.db import models
from django.contrib.auth.models import User  # For user management
from pgvector.django import VectorField

# Create your models here.


class Source(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    country = models.CharField(max_length=50, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


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


class ArticleEmbedding(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    embedding = VectorField(dimensions=384, default=None, null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.ManyToManyField(Category, blank=True)


class UserArticleInteraction(models.Model):

    INTERACTION_CHOICES = [
        ("click", "Click"),
        ("like", "Like"),
        ("bookmark", "Bookmark"),
        ("dislike", "Dislike"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date_interacted = models.DateTimeField(auto_now_add=True)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_CHOICES)
    interacted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article", "interaction_type")

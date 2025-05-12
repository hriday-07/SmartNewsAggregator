from rest_framework import serializers
from .models import Article, Source, Category


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "name", "url"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "content", "url", "source", "category", "published_at"]

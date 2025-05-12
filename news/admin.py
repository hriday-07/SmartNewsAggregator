from django.contrib import admin
from .models import (
    Source,
    Category,
    Article,
    UserProfile,
    ArticleEmbedding,
    UserArticleInteraction,
)

# Register your models here.
admin.site.register(Article)
admin.site.register(Source)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(ArticleEmbedding)
admin.site.register(UserArticleInteraction)

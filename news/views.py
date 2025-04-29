from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, filters
from .models import Article, Source, Category
from .serializers import ArticleSerializer, SourceSerializer, CategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ir_utils import InvertedIndex, boolean_search, get_articles_from_ids


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('-published_at')
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Initialize inverted index (you might want to use a singleton pattern or caching)
inverted_index = InvertedIndex()

@api_view(['GET'])
def boolean_search_view(request):
    """API endpoint for Boolean search"""
    query = request.GET.get('q', '')
    
    # Get matching article IDs
    article_ids = boolean_search(query, inverted_index)
    
    # Get Article objects
    articles = get_articles_from_ids(article_ids)
    
    # Serialize and return
    serializer = ArticleSerializer(articles, many=True)
    return Response({
        'query': query,
        'results_count': len(articles),
        'results': serializer.data
    })

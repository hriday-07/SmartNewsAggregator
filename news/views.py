from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, CategorySelectionForm, SearchForm
from .models import Article, UserProfile, ArticleEmbedding, UserArticleInteraction
import numpy as np
from pgvector.django import L2Distance
from sentence_transformers import SentenceTransformer
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.contrib.auth import logout
from .ir_utils import get_personalized_recommendations


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("recommended_articles")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            if not user.userprofile.preferences.exists():
                return redirect("select_categories")
            return redirect("recommended_articles")
    else:
        form = AuthenticationForm()
    return render(request, "news/login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect("select_categories")
    else:
        form = SignUpForm()
    return render(request, "news/signup.html", {"form": form})


@login_required
def select_categories_view(request):
    if request.method == "POST":
        form = CategorySelectionForm(request.POST)
        if form.is_valid():
            profile = request.user.userprofile
            print(form.cleaned_data["categories"])
            profile.preferences.set(form.cleaned_data["categories"])
            return redirect("recommended_articles")
    else:
        form = CategorySelectionForm()
    return render(request, "news/select_categories.html", {"form": form})


@login_required
def recommended_articles_view(request):
    profile = request.user.userprofile
    if not profile.preferences.exists():
        return redirect("select_categories")

    preferred_categories = profile.preferences.all()
    articles = {}
    for category in preferred_categories:
        articles[category] = Article.objects.filter(category=category).order_by(
            "-published_at"
        )[:20]
    interactions = UserArticleInteraction.objects.filter(user=request.user)
    interaction_map = {}

    for interaction in interactions:
        interaction_map.setdefault(interaction.article_id, set()).add(
            interaction.interaction_type
        )

    context = {
        "articles": articles,
        "interaction_map": interaction_map,
    }
    return render(request, "news/recommended_articles.html", context)


model = SentenceTransformer("all-MiniLM-L6-v2")


@login_required
def embedding_search_view(request):
    results = []
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            query_embedding = model.encode([query])[0]
            similar_articles = (
                ArticleEmbedding.objects.select_related("article")
                .annotate(distance=L2Distance("embedding", query_embedding))
                .order_by("distance")[:10]
            )
            results = [x.article for x in similar_articles]
            for result in similar_articles:
                print(f"Title: {result.article.title}, L2Distance: {result.distance}")
    return render(
        request, "news/embeddings_search.html", {"form": form, "results": results}
    )


@login_required
def boolean_search(request):
    results = []
    form = SearchForm()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            if query.strip():
                search_query = SearchQuery(query, search_type="websearch")
                results = (
                    Article.objects.annotate(search=SearchVector("title", "content"))
                    .filter(search=search_query)
                    .annotate(rank=SearchRank(F("search"), search_query))
                    .order_by("-rank")
                )
                print(results)
            else:
                results = ()
    else:
        form = SearchForm()

    return render(
        request, "news/boolean_search.html", {"form": form, "results": results}
    )


@login_required
def update_reading_history(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    UserArticleInteraction.objects.get_or_create(
        user=request.user,
        article=article,
        interaction_type="click",
    )

    return redirect(article.url)


INTERACTION_TYPES = ["like", "bookmark", "dislike"]


@login_required
@require_POST
def interact_article(request, article_id, interaction_type):
    if interaction_type not in INTERACTION_TYPES:
        return JsonResponse({"error": "Invalid interaction type"}, status=400)
    article = get_object_or_404(Article, id=article_id)
    interaction, created = UserArticleInteraction.objects.get_or_create(
        user=request.user,
        article=article,
        interaction_type=interaction_type,
    )
    if not created:
        interaction.delete()
        status = "removed"
    else:
        status = "added"

    return JsonResponse({"status": status, "type": interaction_type})


@login_required
def personalised_recommendations_view(request):
    user = request.user
    recommendations = get_personalized_recommendations(user)
    return render(request, "news/recommend.html", {"recommendations": recommendations})

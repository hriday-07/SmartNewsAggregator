from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("select-categories/", views.select_categories_view, name="select_categories"),
    path("articles/", views.recommended_articles_view, name="recommended_articles"),
    path("search/", views.embedding_search_view, name="embedding_search"),
    path("logout/", views.logout_view, name="logout"),
    path("boolean_search/", views.boolean_search, name="boolean_search"),
    path(
        "update_history/<int:article_id>/",
        views.update_reading_history,
        name="update_history",
    ),
    path(
        "interact/<int:article_id>/<str:interaction_type>/",
        views.interact_article,
        name="interact_article",
    ),
    path(
        "recommendations/",
        views.personalised_recommendations_view,
        name="recommendations",
    ),
]

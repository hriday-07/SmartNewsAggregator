from pgvector.django import L2Distance, CosineDistance
from .models import ArticleEmbedding, UserArticleInteraction, Article
import numpy as np
import math
from datetime import datetime, timezone

INTERACTION_WEIGHTS = {
    "click": 1.0,
    "like": 2.5,
    "bookmark": 3.0,
    "dislike": -3.0,  # negative influence
}

DECAY_RATE = 0.3


def get_decay_weight(interaction_date):
    now = datetime.now(timezone.utc)
    age_days = (now - interaction_date).days
    return math.exp(-DECAY_RATE * age_days)


def get_weighted_user_embeddings(user):
    interactions = UserArticleInteraction.objects.filter(user=user)
    article_weights = {}

    for interaction in interactions:
        article_id = interaction.article.id
        weight = INTERACTION_WEIGHTS.get(interaction.interaction_type, 0)
        decay_weight = get_decay_weight(interaction.interacted_at)
        final_score = weight * decay_weight

        if article_id in article_weights:
            article_weights[article_id] += final_score
        else:
            article_weights[article_id] = final_score

    embeddings = []
    weights = []

    for article_id, weight in article_weights.items():
        if weight == 0:
            continue

        try:
            embedding = ArticleEmbedding.objects.get(article_id=article_id).embedding
            if embedding is not None and len(embedding) > 0:
                embeddings.append(np.array(embedding))
                weights.append(weight)
        except ArticleEmbedding.DoesNotExist:
            continue

    if embeddings is None or len(embeddings) == 0:
        return None

    # Weighted average
    weighted_sum = np.average(embeddings, axis=0, weights=weights)
    return weighted_sum.tolist()


def get_personalized_recommendations(user, limit=10):
    query_embedding = get_weighted_user_embeddings(user)
    if query_embedding is None or not isinstance(query_embedding, list):
        return Article.objects.none()

    interacted_ids = UserArticleInteraction.objects.filter(user=user).values_list(
        "article_id", flat=True
    )

    similar_articles = (
        ArticleEmbedding.objects.exclude(article_id__in=interacted_ids)
        .annotate(similarity=CosineDistance("embedding", query_embedding))
        .order_by("similarity")[:limit]
    )

    return [item.article for item in similar_articles]

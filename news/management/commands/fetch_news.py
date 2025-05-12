import threading
import requests
import time
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sentence_transformers import SentenceTransformer

from news.models import Article, Source, Category, ArticleEmbedding


# API_KEY = "076c98997f964d5588dcf5f87b7667ad"
API_KEY = "b0486dabea63415ab83fe185acbbefca"
GENRES = ["business", "technology", "sports", "entertainment", "general"]
# GENRES = ["buisness", "sports", "general"]
ARTICLES_PER_GENRE = 200
PAGE_SIZE = 100
PAGES = ARTICLES_PER_GENRE // PAGE_SIZE
COUNTRY = "in"
yesterday = (timezone.now() - timedelta(days=1)).date().isoformat()


class Command(BaseCommand):
    help = "Fetches latest news from NewsAPI and stores them in the database with embeddings"

    def handle(self, *args, **kwargs):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        threads = []
        for genre in GENRES:
            thread = threading.Thread(target=self.fetch_and_store_genre, args=(genre,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.stdout.write(self.style.SUCCESS("All categories fetched and stored."))

    def fetch_and_store_genre(self, genre):
        category_obj, _ = Category.objects.get_or_create(name=genre.capitalize())

        for page in range(1, PAGES + 1):
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": genre,
                "language": "en",
                "from": yesterday,
                "sortBy": "publishedAt",
                "apiKey": API_KEY,
                "pageSize": PAGE_SIZE,
                "page": page,
                "sortBy": "popularity",
            }

            time.sleep(random.uniform(5, 10))

            response = requests.get(url, params=params)
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch {genre} page {page} with status code {response.status_code}"
                    )
                )
                continue

            data = response.json()
            for item in data.get("articles", []):
                source, _ = Source.objects.get_or_create(
                    name=item["source"]["name"] or "Unknown"
                )

                published_at = item.get("publishedAt", "")
                if published_at.endswith("Z"):
                    published_at = published_at[:-1]
                try:
                    dt = datetime.fromisoformat(published_at)
                    published_at = timezone.make_aware(dt, timezone.utc)
                except Exception:
                    published_at = timezone.now()

                article, created = Article.objects.get_or_create(
                    title=item["title"],
                    defaults={
                        "content": item.get("description") or item["title"],
                        "url": item["url"],
                        "source": source,
                        "category": category_obj,
                        "published_at": published_at,
                    },
                )

                if created or not hasattr(article, "articleembedding"):
                    embedding = self.model.encode(article.content)
                    ArticleEmbedding.objects.update_or_create(
                        article=article, defaults={"embedding": embedding}
                    )

        self.stdout.write(self.style.SUCCESS(f"{genre.capitalize()} articles fetched."))

from typing import Optional
from ..models import AnalyzedNews
from django.contrib.auth.models import User
from .interfaces import NewsStorage

class DjangoNewsStorage(NewsStorage):
    """Implementación concreta para almacenar noticias analizadas en Django"""

    def store_analysis(self, user_id: int, title: str, author: str, date: str,
                      url: Optional[str], text: str, score: int, explanation: str) -> None:
        user = User.objects.get(id=user_id)
        AnalyzedNews.objects.create(
            user=user,
            title=title,
            author=author,
            date=date,
            url=url,
            text=text,
            score=score,
            explanation=explanation
        )
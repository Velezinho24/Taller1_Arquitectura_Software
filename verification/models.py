from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Publisher(models.Model):
    """
    Medio/editor responsable de publicar el contenido.
    Se infiere típicamente por el dominio del URL, pero puede ajustarse manualmente.
    """
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    """
    Contenido periodístico normalizado. Evita duplicar título/autor/fecha/url/texto
    cada vez que se realiza una verificación (AnalyzedNews).
    """
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, default="")
    published_at = models.DateTimeField(null=True, blank=True)
    url = models.URLField(unique=True, blank=True, null=True)
    text = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["published_at"]),
            models.Index(fields=["title"]),
        ]
        ordering = ["-published_at", "title"]

    def __str__(self) -> str:
        return self.title


class AnalyzedNews(models.Model):
    """
    Resultado de verificación/score para un Article, asociado a un usuario.
    Antes: duplicaba title/author/date/url/text.
    Ahora: referencia a Article -> mejor integridad y consultas.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="analyses")
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["score"]),
        ]

    def __str__(self) -> str:
        return f"{self.article.title} ({self.score})"
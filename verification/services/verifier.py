class NewsVerifier:
    """Clase que coordina el proceso de verificación de noticias"""

    def __init__(self, extractor, analyzer, storage):
        self.extractor = extractor
        self.analyzer = analyzer
        self.storage = storage

    def verify_from_url(self, url: str, user_id: int, language: str):
        """Verifica una noticia a partir de una URL"""
        # Extraer contenido
        article_text, title, author, date = self.extractor.extract_content(url)
        
        # Analizar con IA
        explanation, score = self.analyzer.analyze_news(title, author, date, article_text, language)
        
        # Almacenar resultados
        self.storage.store_analysis(
            user_id=user_id,
            title=title,
            author=author,
            date=date,
            url=url,
            text=article_text,
            score=score,
            explanation=explanation
        )
        
        return {
            'url': url,
            'result': explanation,
            'title': title,
            'author': author,
            'date': date,
            'text': article_text,
        }

    def verify_from_text(self, text: str, user_id: int, language: str):
        """Verifica una noticia a partir de texto plano"""
        # Preparar contenido
        article_text = text.strip()
        if len(article_text) > 4000:
            article_text = article_text[:4000]
        
        title = 'Provided directly'
        author = 'not available'
        date = 'not available'
        
        # Analizar con IA
        explanation, score = self.analyzer.analyze_news(title, author, date, article_text, language)
        
        # Almacenar resultados
        self.storage.store_analysis(
            user_id=user_id,
            title=title,
            author=author,
            date=date,
            url=None,
            text=article_text,
            score=score,
            explanation=explanation
        )
        
        return {
            'url': None,
            'result': explanation,
            'title': title,
            'author': author,
            'date': date,
            'text': article_text,
        }
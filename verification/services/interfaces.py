from abc import ABC, abstractmethod
from typing import Optional, Tuple

class NewsExtractor(ABC):
    """Interface for extracting news content from different sources"""
    @abstractmethod
    def extract_content(self, source: str) -> Tuple[str, str, str, str]:
        """
        Extract content from a news source
        Returns: (article_text, title, author, date)
        """
        pass

class AIAnalyzer(ABC):
    """Interface for AI-based news analysis"""
    @abstractmethod
    def analyze_news(self, title: str, author: str, date: str, text: str, language: str) -> Tuple[str, int]:
        """
        Analyze news content and return credibility assessment
        Returns: (explanation, score)
        """
        pass

class NewsStorage(ABC):
    """Interface for storing analyzed news"""
    @abstractmethod
    def store_analysis(self, user_id: int, title: str, author: str, date: str, 
                      url: Optional[str], text: str, score: int, explanation: str) -> None:
        """Store the results of a news analysis"""
        pass
from typing import Tuple
import os
from openai import OpenAI
from dotenv import load_dotenv
from .interfaces import AIAnalyzer

class OpenAIAnalyzer(AIAnalyzer):
    """Implementación concreta para análisis de noticias usando OpenAI"""

    def __init__(self):
        load_dotenv('./API.env')
        self.client = OpenAI(api_key=os.environ.get("openai_apikey"))

    def analyze_news(self, title: str, author: str, date: str, text: str, language: str) -> Tuple[str, int]:
        lang_instruction = self._get_language_instruction(language)
        
        prompt = self._create_prompt(title, author, date, text, lang_instruction)
        
        ai_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in news verification."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        result = ai_response.choices[0].message.content.strip()
        score = self._extract_score(result)
        
        return result, score

    def _get_language_instruction(self, language: str) -> str:
        language_instructions = {
            'es': "Responde en español.",
            'pt': "Responda em português.",
            'en': "Respond in English."
        }
        return language_instructions.get(language, "Respond in English.")

    def _create_prompt(self, title: str, author: str, date: str, text: str, lang_instruction: str) -> str:
        return f"""{lang_instruction}
            News Title: {title}
            Author: {author}
            Publication Date: {date}

            Analyze the following news story and return a credibility score from 1 to 100 based on:
            - Source reliability
            - Author
            - Date of the news story
            - Evidence presented in the text

            Assign a score from 1 to 25 to each of these, and a short explanation on why this scores.

            News Text:
            \"\"\"
            {text}
            \"\"\"

            Return the total score (1-100) and a brief explanation (maximum 3 sentences).
            """

    def _extract_score(self, result: str) -> int:
        import re
        score_match = re.search(r"(?:Total Score|Score total)[:\s]*([0-9]{1,3})", result, re.IGNORECASE)
        return int(score_match.group(1)) if score_match else 0
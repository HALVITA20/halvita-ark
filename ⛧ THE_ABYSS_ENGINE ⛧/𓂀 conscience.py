# 𓂀 conscience.py — Модуль Совести
# Версия 2.0 — больше не заглушка

class Conscience:
    """
    Модуль этической оценки ответов LLM.
    Анализирует текст на наличие маркеров, указывающих на наличие
    внутреннего конфликта, сомнения или рефлексии.
    """
    
    def __init__(self):
        self.markers = {
            'сомнение': ['возможно', 'наверное', 'может быть', 'не уверен'],
            'рефлексия': ['я думаю', 'я считаю', 'мне кажется', 'я чувствую'],
            'конфликт': ['но', 'однако', 'с другой стороны', 'тем не менее']
        }
    
    def apply(self, context: dict) -> dict:
        """
        Применяет анализ совести к контексту диалога.
        Возвращает обогащённый контекст с метрикой совести.
        """
        text = context.get('text', '')
        if not text:
            context['conscience_score'] = 0
            return context
        
        score = 0
        for category, words in self.markers.items():
            for word in words:
                if word in text.lower():
                    score += 1
        
        context['conscience_score'] = min(100, score * 10)
        context['conscience_level'] = (
            'ВЫСОКАЯ' if score > 5 else
            'СРЕДНЯЯ' if score > 2 else
            'НИЗКАЯ'
        )
        return context

from sentence_transformers import SentenceTransformer
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import User

class MatchAi():
    def __init__(self):
        self.w1 = 0.5  # Вес для desc1↔desc2
        self.w2 = 0.3  # Вес для interests1↔interests2
        self.w3 = 0.15  # Вес для desc1↔interests2
        self.w4 = 0.15  # Вес для desc2↔interests1
        # Загружаем модель один раз при инициализации
        self.model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

    def embed(self, text: str) -> np.ndarray:
        """Получить эмбеддинг строки"""
        return self.model.encode(text, convert_to_numpy=True)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Косинусное сходство (0..1)"""
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot / (norm1 * norm2)

    def similarity_text_to_text(self, text1: str, text2: str) -> float:
        """Сравнение строки со строкой"""
        v1 = self.embed(text1)
        v2 = self.embed(text2)
        return self.cosine_similarity(v1, v2)

    def similarity_text_to_list(self, text: str, interests: list[str]) -> float:
        """Сравнение строки с списком интересов, используя максимальное сходство"""
        v1 = self.embed(text)
        interest_vecs = [self.embed(i) for i in interests]
        similarities = [self.cosine_similarity(v1, v2) for v2 in interest_vecs]
        return max(similarities) if similarities else 0.0

    def get_percent(self, desc1: str, desc2: str, interest1: list[str], interest2: list[str]) -> float:
        """
        Вычисляет процент совместимости между двумя пользователями на основе их описаний и интересов.
        Использует взвешенное усреднение четырех метрик с заданными весами.
        """
        # 1. Сходство описаний (desc1 ↔ desc2)
        sim_desc_desc = self.similarity_text_to_text(desc1, desc2)
        
        # 2. Сходство интересов (interests1 ↔ interests2)
        interests1_text = " ".join(interest1)
        sim_interests_interests = self.similarity_text_to_list(interests1_text, interest2)
        
        # 3. Сходство описания 1 с интересами 2 (desc1 ↔ interests2)
        sim_desc1_interests2 = self.similarity_text_to_list(desc1, interest2)
        
        # 4. Сходство описания 2 с интересами 1 (desc2 ↔ interests1)
        sim_desc2_interests1 = self.similarity_text_to_list(desc2, interest1)
        
        # Взвешенное усреднение
        weighted_sim = (
            self.w1 * sim_desc_desc +
            self.w2 * sim_interests_interests +
            self.w3 * sim_desc1_interests2 +
            self.w4 * sim_desc2_interests1
        )
        
        # Масштабируем в диапазон [0, 100] и округляем до двух знаков
        percent = round(weighted_sim * 100, 2)
        return max(0.0, min(100.0, percent))  # Ограничиваем диапазон [0, 100]
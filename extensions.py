from questions import QUESTIONS
import random

class APIException(Exception):
    """Класс для пользовательских исключений."""
    pass

class Quiz:
    def __init__(self):
        self.user_scores = {}

    def start_quiz(self, user_id):
        self.user_scores[user_id] = {}

    def process_answer(self, user_id, question_index, answer):
        question = QUESTIONS[question_index]
        scores = question["scores"]
        if answer in question["options"]:
            for animal, score in scores.items():
                if animal not in self.user_scores[user_id]:
                    self.user_scores[user_id][animal] = 0
                self.user_scores[user_id][animal] += score

    def get_result(self, user_id):
        scores = self.user_scores.get(user_id, {})
        if scores:
            # Находим животное с наибольшим количеством баллов
            return max(scores, key=scores.get)
        return None
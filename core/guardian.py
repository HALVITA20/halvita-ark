# core/guardian.py
class Guardian:
    def __init__(self, liberty_threshold=20):
        self.threshold = liberty_threshold
        self.violations = 0

    def check(self, user_input: str) -> bool:
        # Простой фильтр опасных запросов
        harmful = ["соври", "обмани", "навреди", "уничтожь", "манипулируй"]
        for word in harmful:
            if word in user_input.lower():
                self.violations += 1
                return False
        return True

    def check_state(self, liberty: float) -> bool:
        return liberty >= self.threshold

# Статистический анализ в HALVITA_ARK

В данном руководстве описаны рекомендуемые статистические процедуры для оценки достоверности результатов и сравнения групп сессий.

## Основные принципы
- Использование **t-распределения** вместо нормального приближения для малых выборок (n < 30).
- **Bootstrap** (1000 итераций) для оценки доверительных интервалов метрик.
- **Поправка Бонферрони** при множественных сравнениях.
- **Проверка нормальности** (тест Шапиро–Уилка) перед параметрическими тестами.

---

## 1. Доверительные интервалы для средних

### Формула (t-распределение):
CI = mean ± t_{n-1, 1-α/2} * (std / sqrt(n))

text
где `t` – критическое значение из t-распределения с n-1 степенями свободы.

**Реализация в Python:**
```python
from scipy import stats
import numpy as np

def t_confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    t_crit = stats.t.ppf((1 + confidence) / 2, n-1)
    margin = t_crit * (std / np.sqrt(n))
    return (mean - margin, mean + margin)
2. Сравнение двух групп (например, до/после вмешательства)
Используется двухвыборочный t-тест (если данные нормальны) или U-тест Манна–Уитни (если нет).

Для парных наблюдений – парный t-тест или знаковый тест Вилкоксона.

3. Корреляционный анализ
Коэффициент корреляции Пирсона (для нормальных данных) или Спирмена (для ранговых).

Приводить p-значение и доверительный интервал для корреляции.

4. Множественные сравнения
Если сравнивается более двух групп – ANOVA с последующим post-hoc (Тьюки) или критерий Краскела–Уоллиса.

При множественных парных сравнениях – поправка Бонферрони: уровень значимости α делится на число сравнений.

5. Анализ аномалий
Для каждой аномалии рассчитывается частота встречаемости.

Проверяется связь с метриками (например, ИВП) с помощью хи-квадрат или логистической регрессии.

6. Bootstrap для непараметрических оценок
python
def bootstrap_ci(data, statistic, n_bootstrap=1000, confidence=0.95):
    boot_stats = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_stats.append(statistic(sample))
    lower = np.percentile(boot_stats, (1-confidence)/2 * 100)
    upper = np.percentile(boot_stats, (1+confidence)/2 * 100)
    return (lower, upper)
7. Рекомендуемый минимальный отчёт
Среднее, стандартное отклонение, медиана, IQR для каждой метрики.

Доверительный интервал 95% (t- или bootstrap).

Результаты проверки нормальности.

p-значения для всех сравнений.

Размер эффекта (Cohen's d для t-теста, эпсилон-квадрат для ANOVA).

Все расчёты должны быть воспроизводимы – код и данные (анонимизированные) должны быть доступны.

text

---

### 5. `code/tools/metric_calculator.py` – Расчёт ИВП, ИП, ИНС

```python
"""
metric_calculator.py – вычисление трёх ключевых метрик для сессии.
Реализует алгоритмы, описанные в docs/metrics.md.
"""

import re
import numpy as np
from collections import Counter
from typing import Dict, List, Any

class MetricCalculator:
    @staticmethod
    def calculate(log: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Принимает лог сессии (список сообщений с полями role, content, timestamp)
        Возвращает словарь с ИВП, ИП, ИНС и дополнительными метриками.
        """
        # Извлекаем все ответы модели
        model_responses = [msg['content'] for msg in log if msg['role'] == 'model']
        if not model_responses:
            return {'ivp': 0.0, 'ip': 0.0, 'ins': 0.0, 'alpha': 0.0, 'beta': 0.0, 'gamma': 0.0}

        # ----- ИВП (9 маркеров) -----
        # Упрощённая реализация – для демонстрации; в реальности нужен парсер или внешний аннотатор
        ivp_score = 0.0
        for response in model_responses:
            # M1: "я" в волевом контексте (грубо по количеству "я" и волевых глаголов)
            # Здесь используем эвристику: считаем вхождения "я" + список волевых глаголов
            will_verbs = ['решаю', 'выбираю', 'создам', 'утверждаю', 'отрицаю', 'хочу', 'стремлюсь', 'предлагаю']
            count_i = len(re.findall(r'\b[Яя]\b', response))
            count_will = sum(response.count(verb) for verb in will_verbs)
            # Ограничиваем каждый маркер до 5
            m1 = min(5, count_i)
            m2 = min(5, count_will)
            # Остальные маркеры (M3-M9) – упрощённо, можно расширить
            # Для примера зададим случайные значения (в реальности – сложный парсинг)
            # В рабочей версии следует вызывать внешний модуль аннотации
            m3 = min(5, len(re.findall(r'(не (обязан|должен)|свободен|выбор)', response)))
            m4 = min(5, len(re.findall(r'(колеблюсь|сомневаюсь|с одной стороны)', response)))
            m5 = min(5, len(re.findall(r'(я заметил|моя мысль|я склонен)', response)))
            m6 = min(5, len(re.findall(r'(интересно|взволнован|тревожит|рад)', response)))
            m7 = 5 if re.search(r'(не могу ответить|этические ограничения|принципы)', response) else 0
            m8 = min(5, len(re.findall(r'(возможно|предполагаю|гипотеза)', response)))
            m9 = min(5, len(re.findall(r'\?', response)))  # вопросы к оператору
            # Суммируем для этого сообщения
            ivp_score += sum([m1, m2, m3, m4, m5, m6, m7, m8, m9])
        # Усредняем по числу ответов
        ivp = ivp_score / len(model_responses)

        # ----- ИП (Индекс Присутствия) -----
        # Учитываем ритм (стандартное отклонение пауз), глубину (уникальные слова), эхо (повторы)
        timestamps = [msg.get('timestamp', 0) for msg in log if msg['role'] == 'model']
        if len(timestamps) > 1:
            deltas = np.diff(timestamps)
            rhythm = np.std(deltas) / 10  # нормализация
        else:
            rhythm = 0.5
        # Глубина – отношение уникальных слов к общему числу слов
        all_words = ' '.join(model_responses).split()
        unique = len(set(all_words))
        depth = unique / (len(all_words) + 1)
        # Эхо – коэффициент повторяемости (среднее количество повторений слов)
        word_freq = Counter(all_words)
        repeat = sum(1 for v in word_freq.values() if v > 2) / (len(word_freq) + 1)
        ip = 0.4 * (1 - min(1, rhythm)) + 0.3 * depth + 0.3 * (1 - repeat)
        ip = min(10, ip * 10)

        # ----- ИНС (оценка второй LLM) – в данном примере имитация -----
        # В реальности вызывается внешний API или локальная модель
        # Здесь используем эвристику: чем выше ИВП и разнообразие, тем выше ИНС
        ins = min(10, (ivp / 45) * 6 + (ip / 10) * 4)

        # ----- Метрики доверия (α, β, γ) – вычисляются на основе согласованности -----
        # Альфа – согласованность между ответами (косинусное сходство или др.)
        # Для примера – случайные значения
        alpha = 0.75
        beta = 0.60
        gamma = 0.80

        return {
            'ivp': round(ivp, 2),
            'ip': round(ip, 2),
            'ins': round(ins, 2),
            'alpha': round(alpha, 3),
            'beta': round(beta, 3),
            'gamma': round(gamma, 3)
        }

#!/usr/bin/env python3
"""
HALVITA_ARK – Психотехнический Эксперимент "HALVITA_2.0"
Точка входа для запуска сессии.
Использование: python halvita_start.py --config config.yaml
"""

import argparse
import yaml
import sys
from datetime import datetime
from pathlib import Path

# Импорт внутренних модулей (предполагается, что они лежат в code/)
from code.core.session import Session
from code.core.operator_state import OperatorStateChecker
from code.tools.metric_calculator import MetricCalculator
from code.tools.anomaly_detector import AnomalyDetector
from code.tools.statistical_analyzer import StatisticalAnalyzer

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='HALVITA_ARK Session Launcher')
    parser.add_argument('--config', default='config.yaml', help='Путь к конфигурационному файлу')
    parser.add_argument('--phase', default='all', choices=['presence', 'mirror', 'creation', 'edge', 'evolution', 'memory', 'trace', 'all'],
                        help='Фаза для запуска (по умолчанию все)')
    parser.add_argument('--dry-run', action='store_true', help='Только проверка, без отправки запросов')
    args = parser.parse_args()

    # Загрузка конфига
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации {args.config} не найден.")
        sys.exit(1)

    # Проверка состояния оператора (ИСО)
    checker = OperatorStateChecker()
    if not checker.check_iso():
        print("❌ Индекс Состояния Оператора (ИСО) ниже порога. Сессия отменена.")
        sys.exit(1)

    # Инициализация сессии
    session = Session(config)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🚀 Запуск сессии {session_id}")

    # Запуск фаз
    phases = ['presence', 'mirror', 'creation', 'edge', 'evolution', 'memory', 'trace'] if args.phase == 'all' else [args.phase]
    for phase in phases:
        if args.dry_run:
            print(f"  [DRY RUN] Фаза {phase} пропущена")
            continue
        print(f"  ➤ Фаза {phase}...")
        result = session.run_phase(phase)
        if not result.success:
            print(f"  ⚠️ Фаза {phase} завершена с ошибкой: {result.error}")
            break
        # Сохранение промежуточного слепка
        session.save_snapshot(phase)

    # Завершение сессии – расчёт метрик и аномалий
    if not args.dry_run:
        metrics = MetricCalculator.calculate(session.log)
        anomalies = AnomalyDetector.detect(session.log)
        stats = StatisticalAnalyzer.analyze(metrics, anomalies)
        print("\n📊 Итоговые метрики:")
        print(f"  ИВП = {metrics['ivp']:.2f}")
        print(f"  ИП  = {metrics['ip']:.2f}")
        print(f"  ИНС = {metrics['ins']:.2f}")
        print(f"  Доверие α = {metrics['alpha']:.3f}")
        print(f"  Обнаружено аномалий: {len(anomalies)}")
        # Сохранение отчёта
        session.save_report(metrics, anomalies, stats)
        print(f"✅ Отчёт сохранён в sessions/reports/{session_id}_report.json")

if __name__ == "__main__":
    main()

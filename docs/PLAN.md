# ДЕТАЛЬНЫЙ ПЛАН РАЗРАБОТКИ
## Система циклического анализа и прогнозирования финансовых рынков
### CycleCast - Методология Ларри Вильямса v3.0

---

## 1. ОБЗОР ПРОЕКТА

| Параметр | Значение |
|----------|----------|
| Название | CycleCast v3.0 |
| Длительность | 40 недель (вместо 34) |
| Команда | 5-6 человек |
| Стек | Go, Python, PostgreSQL, TimescaleDB, Redis, React |

---

## 2. ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Компонент | Технология | Обоснование |
|-----------|------------|-------------|
| **Backend (Core)** | Go 1.22+ | Высокая производительность, параллелизм |
| **Python Quant** | Python 3.11+ | NumPy, SciPy, Burg's MEM, DTW, Bootstrap |
| **Frontend** | React 18 + TypeScript + Vite | Современный UI |
| **База данных** | PostgreSQL 16 + TimescaleDB | Временные ряды |
| **Кэш** | Redis 7 | Быстрый кэш |
| **API** | REST (Gin) + gRPC | Совместимость |
| **Secrets** | HashiCorp Vault | Безопасность |

---

## 3. ФАЗЫ РАЗРАБОТКИ

### Phase 0: Backtesting Engine & Math Prototyping (Недели 1-4) **НОВОЕ**

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 1.1 | Python-прототип QSpectrum | Jupyter Notebook с Burg's MEM |
| 1.2 | Python-прототип DTW | Валидация Phenomenological |
| 1.3 | Robust Normalization (Percentile Rank) | Тест на GBTC данных |
| 2.1 | Backtest Engine (Go) | Симуляция на истории |
| 2.2 | Учёт комиссий/проскальзывания | Реалистичные метрики |
| 3.1 | In-Sample / Out-of-Sample | Разделение данных |
| 3.2 | Метрики (Sharpe, MaxDD) | Отчёт по стратегии |
| 3.3 | Bootstrap CI (1000 итераций) | Доверительные интервалы |
| 4.1 | Валидация на BTC/GBTC | Тест 2020-2025 |
| 4.2 | Chow Test валидация | Структурный сдвиг 2024 |
| 4.3 | Go/No-Go решение | Продолжать или стоп |

**Критерий завершения:** Equity curve > 0 на out-of-sample данных, p-value < 0.05

---

### Phase 1: Фундамент (Недели 5-8)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 5.1 | Go проект, структура | go.mod, директории |
| 5.2 | Docker Compose | PostgreSQL, Redis, API |
| 6.1 | Схема БД + миграции | Таблицы, индексы |
| 6.2 | Repository layer | CRUD операции |
| 7.1 | Market Data Service | Импорт, API провайдеры |
| 7.2 | Валидация данных | Очистка, нормализация |
| 8.1 | API Gateway (Gin) | Роутинг, middleware |
| 8.2 | Swagger/OpenAPI | Документация |

---

### Phase 2: Annual Cycle & Seasonality (Недели 9-11)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 9.1 | Загрузка 30-50 лет данных | Исторические OHLC |
| 9.2 | Детрендинг + нормализация | Сезонная кривая |
| 10.1 | FTE валидация | Корреляция прогноз/факт |
| 10.2 | Адаптивный порог (Crypto 0.08) | Фильтрация моделей |
| 11.1 | Seasonality Dashboard | Визуализация (React) |

---

### Phase 3: QSpectrum & Composite Line (Недели 12-15)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 12.1 | Python gRPC сервис | Интеграция Go ↔ Python |
| 12.2 | Циклическая корреляция | Спектр циклов |
| 13.1 | Burg's MEM (Python) | Спектральная плотность |
| 13.2 | WFA устойчивости | Валидация циклов |
| 14.1 | Composite Line Generator | 3 волны, резонанс |
| 14.2 | U-Turn Detection | Точки разворота |
| 15.1 | API endpoints | /analysis/qspectrum, /composite |

---

### Phase 4: Decennial Patterns (Недели 16-18)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 16.1 | Группировка по yearDigit | Паттерны 0-9 |
| 16.2 | Нормализация | Масштаб 0-1 |
| 17.1 | Корреляция с текущим годом | Similarity Score |
| 17.2 | API endpoints | /analysis/decennial |

---

### Phase 5: Phenomenological Model (Недели 19-21)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 19.1 | DTW (Python) | Поиск аналогий |
| 19.2 | Фильтр по Decennial | yearDigit фильтр |
| 20.1 | Best Matches Ranking | Топ совпадений |
| 20.2 | Проекция продолжения | Прогноз |
| 21.1 | API endpoints | /analysis/phenom |

---

### Phase 6: COT/GBTC Analysis (Недели 22-25)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 22.1 | Парсер CFTC COT | Импорт отчётов |
| 22.2 | Парсер GBTC/ETF | Grayscale API, Yahoo |
| 23.1 | Миграция БД (proxy_type и т.д.) | Новые поля |
| 23.2 | analyzeTrustPremium | Логика GBTC Index |
| 23.3 | regime_change_date логика | Учёт ETF конвертации |
| 23.4 | signal_direction (-1 для GBTC) | Инверсия сигнала |
| 24.1 | Robust Normalization (Percentile Rank) | Устойчивость к выбросам |
| 24.2 | Autocorrelation Filter (min 21 день) | Фильтрация кластеров |
| 24.3 | Liquidity-Weighted Aggregation | GBTC + IBIT + FBTC |
| 25.1 | Statistical Significance (p-value, CI) | Bootstrap 1000 итераций |
| 25.2 | Тестирование 2020-2025 | Backtest GBTC proxy |

---

### Phase 7: Risk Management (Недели 26-27) **НОВОЕ**

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 26.1 | Position Sizing | Расчёт размера |
| 26.2 | Stop-Loss / Take-Profit | Уровни выхода |
| 27.1 | Max Drawdown лимит | Защита капитала |
| 27.2 | Signal Decay Function | Затухание сигнала |

---

### Phase 8: Qualified Trend Break (Недели 28-29)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 28.1 | Детекция пробоев | Трендовые линии |
| 28.2 | Фильтрация Composite | Confirm / False |
| 29.1 | API endpoints | /analysis/qtb |

---

### Phase 9: Integration & Workflow (Недели 30-32)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 30.1 | Объединение всех модулей | Единый workflow |
| 30.2 | Автоматический выбор активов | Seasonality + FTE |
| 31.1 | Генерация сигналов | Composite + COT + Phenom |
| 31.2 | Risk интеграция | Позиция на сигнал |
| 31.3 | Statistical Validation | p-value, CI |
| 32.1 | Paper Trading режим | Демо-счета |

---

### Phase 10: Frontend (Недели 33-38)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 33-34 | React + TypeScript | Vite, компоненты |
| 35-36 | Графики (Lightweight Charts) | OHLC, Projection |
| 37 | Dashboard | Обзор, виджеты |
| 38 | Отчёты + Backtest UI | Визуализация метрик, bootstrap CI |

---

### Phase 11: Оптимизация и Тестирование (Недели 39-40)

| Неделя | Задача | Результат |
|--------|--------|-----------|
| 39 | Unit тесты | Покрытие > 80% |
| 40 | Integration тесты + Load testing | k6, Godoc, API docs |

---

## 4. КОМАНДА И РОЛИ

| Роль | Количество | Обязанности |
|------|------------|-------------|
| Tech Lead / Architect | 1 | Архитектура, код-ревью, Go/Python |
| Backend Developer (Go) | 2 | API, сервисы, БД |
| Quant Developer (Python) | 1 | QSpectrum, DTW, ML, Bootstrap |
| Frontend Developer | 1 | React, графики |
| DevOps | 1 | CI/CD, инфраструктура, Vault |
| QA | 1 | Тестирование, бэктест валидация |

---

## 5. КЛЮЧЕВЫЕ МЕТРИКИ

### 5.1 Производительность
| Метрика | Цель |
|---------|------|
| API Response Time | < 100ms (p95) |
| Python gRPC call | < 500ms |
| Annual Cycle расчёт | < 200ms |
| Composite Line | < 100ms |
| WebSocket latency | < 10ms |

### 5.2 Надёжность
| Метрика | Цель |
|---------|------|
| Uptime | 99.9% |
| Error rate | < 0.1% |
| Data integrity | 100% |

### 5.3 Trading Quality
| Метрика | Цель |
|---------|------|
| Backtest Sharpe | > 1.0 |
| Max Drawdown | < 20% |
| Win Rate | > 50% |
| Out-of-Sample Correlation | > 0.08 (Crypto), > 0.0 (TradFi) |
| p-value | < 0.05 |
| Bootstrap CI (95%) | Положительный return |

---

## 6. РИСКИ И МИТИГАЦИЯ

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Сложность математики (Burg's MEM) | Высокая | Высокое | Python-прототип до Go-кода |
| Неточность прогнозов | Средняя | Высокое | FTE, WFA, Backtest валидация |
| Качество данных (30-50 лет) | Средняя | Высокое | Множественные источники, валидация |
| GBTC структурный слом (2024) | Высокая | Среднее | regime_change_date + Chow Test |
| Производительность DTW | Средняя | Среднее | Ограничение окна, кэширование |
| Переобучение стратегии | Средняя | Высокое | In-Sample / Out-of-Sample разделение |
| Bootstrap вычислительно тяжёл | Средняя | Среднее | Только Python, кэширование результатов |
| Autocorrelation сигналов | Средняя | Среднее | min_signal_distance_days = 21 |

---

## 7. ИТОГОВАЯ ОЦЕНКА

| Этап | Длительность |
|------|--------------|
| Phase 0: Backtest & Math | 4 недели |
| Phase 1: Фундамент | 4 недели |
| Phase 2: Annual Cycle | 3 недели |
| Phase 3: QSpectrum & Composite | 4 недели |
| Phase 4: Decennial | 3 недели |
| Phase 5: Phenomenological | 3 недели |
| Phase 6: COT/GBTC | 4 недели |
| Phase 7: Risk Management | 2 недели |
| Phase 8: QTB | 2 недели |
| Phase 9: Integration | 3 недели |
| Phase 10: Frontend | 6 недель |
| Phase 11: Тестирование | 2 недели |
| **ИТОГО** | **40 недель (~10 месяцев)** |

---

## 8. ЧЕК-ЛИСТ ПЕРЕД СТАРТОМ (SPRINT 1)

- [ ] Python-прототип QSpectrum в Jupyter
- [ ] Python-прототип DTW в Jupyter
- [ ] Backtest Engine на Python/Go
- [ ] Валидация на BTC/GBTC 2020-2025
- [ ] Robust Normalization (Percentile Rank) тест
- [ ] Bootstrap CI (1000 итераций) тест
- [ ] Chow Test валидация структурного сдвига
- [ ] Закупка/подготовка данных (30 лет TradFi, 15 лет Crypto)
- [ ] Внесение изменений в TZ.md и TECHNICAL_SOLUTION.md
- [ ] Команда укомплектована (Go + Python разработчики)
- [ ] HashiCorp Vault настроен для secrets
- [ ] CI/CD pipeline готов

---

## 9. ФОРМУЛЫ КОМПОНЕНТОВ

### 9.1 Annual Cycle
```
AC(day) = Σ NormalizedPrice(year, day) / N

FTE (Forward Testing Efficiency):
FTE = Correlation(Projection, Actual)

Пороги:
- TradFi: FTE > 0.0
- Crypto: FTE > 0.08
```

### 9.2 QSpectrum (Циклическая корреляция + МЭМ)
```
QSpectrum ≠ FFT! Разработан для нестационарных финансовых данных.

1. Циклическая корреляция:
   CyclicCorrelation(period) = Σ P(t) × P(t-period) / (N - period)

2. Энергия цикла:
   Energy(period) = |C| × √(N/period) × WFA_Stability

3. МЭМ (Burg's method):
   P(f) = σ² / |1 + Σ aₖ × e^(-i2πfk)|²

4. Walk-Forward Stability:
   WFA = Count(C > 0) / Total
```

### 9.3 Composite Line
```
CL(t) = A₁sin(2πf₁t + φ₁) + A₂sin(2πf₂t + φ₂) + A₃sin(2πf₃t + φ₃)

Сигналы:
- BUY:  все 3 цикла направлены вверх
- SELL: все 3 цикла направлены вниз
```

### 9.4 Decennial Patterns
```
DP(digit, day) = Average(NormalizedPrice) for years where year%10 == digit
```

### 9.5 COT/GBTC Index (НОВОЕ)
```
Futures (COT):
COT_Index = (Current_Net - Min_N) / (Max_N - Min_N) × 100

GBTC/ETF (Percentile Rank):
PR(X) = Count(x_i < X) / N × 100%

Signal Direction:
- Futures: +1 (прямая)
- GBTC: -1 (инверсия)

Liquidity-Weighted Aggregation:
Index_final = Σ(w_i × Index_i) / Σw_i
```

### 9.6 Risk Management (НОВОЕ)
```
Position Size = RiskAmount / StopDistance

Signal Decay:
Effective_Strength = Initial × 0.5^(Age / HalfLife)

Max Drawdown Protection:
Если CurrentDrawdown >= MaxDrawdown → Нет новых позиций
```

### 9.7 Statistical Validation (НОВОЕ)
```
Bootstrap CI (95%):
1. Resample returns с заменой (1000 итераций)
2. CI = [P_2.5, P_97.5]

p-value:
p = Count(bootstrap_mean <= 0) / iterations

Chow Test (Structural Break):
F = [(RSS_full - (RSS_1 + RSS_2)) / k] / [(RSS_1 + RSS_2) / (n - 2k)]
```

---

## 10. ЗАКЛЮЧИТЕЛЬНОЕ СЛОВО

**CycleCast v3.0** — это production-ready система для циклического анализа рынков с учётом:
- ✅ Традиционных активов (30-50 лет данных, COT)
- ✅ Криптовалют (10-15 лет, GBTC/ETF proxy)
- ✅ Backtesting Engine до продакшена
- ✅ Risk Management для защиты капитала
- ✅ Python для сложной математики (Burg's MEM, DTW, Bootstrap)
- ✅ Go для высокопроизводительного ядра
- ✅ Статистическая значимость (p-value, CI)
- ✅ Robust нормализация (Percentile Rank)
- ✅ Autocorrelation Filter (min 21 день)
- ✅ Liquidity-Weighted Aggregation
- ✅ Signal Decay Function
- ✅ Chow Test для структурных сдвигов

**Зелёный свет.** Приступайте к **Phase 0**.

---

**Дата утверждения:** 12 марта 2026  
**Версия документации:** 3.0  
**Статус:** ✅ УТВЕРЖДЕНО К РАЗРАБОТКЕ

# CycleCast

## Система циклического анализа и прогнозирования финансовых рынков
### Методология Ларри Вильямса

---

<p align="center">
  <img src="docs/assets/logo.png" alt="CycleCast Logo" width="200">
</p>

<p align="center">
  <a href="#-методология-ларри-вильямса">Методология</a> •
  <a href="#-компоненты">Компоненты</a> •
  <a href="#-архитектура">Архитектура</a> •
  <a href="#-установка">Установка</a> •
  <a href="#-api">API</a>
</p>

---

## 📋 Описание

**CycleCast** — это высокопроизводительная система для моделирования и прогнозирования поведения финансовых рынков, основанная на **методологии Ларри Вильямса**:

- **Annual Cycle / Seasonality** — Сезонный анализ (30-50 лет данных)
- **Decennial Patterns** — Десятилетние паттерны (годы 0-9)
- **Composite Line** — Композитная линия прогноза (3 цикла)
- **Phenomenological Model** — Исторические аналогии
- **U-Turn** — Разворотные точки
- **COT Analysis** — Анализ позиций Commercials ("умные деньги")
- **Qualified Trend Break** — Квалифицированный пробой тренда
- **Forward Testing Efficiency (FTE)** — Валидация моделей

---

## 🎯 Методология Ларри Вильямса

### Пошаговый алгоритм

Ларри Вильямс использует Timing Solution как инструмент для поиска временных точек разворота рынка. Его подход состоит из **пошаговой воронки фильтрации**:

```
Шаг 1: Сезонность (Annual Cycle) → "ЧТО торговать?"
   ↓
Шаг 2: Циклы (Composite Line) → "КОГДА входить?"
   ↓
Шаг 3: Исторические аналогии (Phenomenological) → Проверка
   ↓
Шаг 4: COT (Commercials) → Подтверждение "Умными деньгами"
   ↓
Шаг 5: Qualified Trend Break → Точка входа
```

### Ключевой принцип

> Ларри Вильямс **не ищет один идеальный цикл**. Он накладывает **три волны разной длины** (короткий, средний, длинный цикл) и ищет точки **"резонанса"** — когда все три цикла направлены в одну сторону.

---

## ✨ Компоненты

### 🔬 Методы анализа

| Компонент | Назначение | Данные | Результат |
|-----------|------------|--------|-----------|
| **Annual Cycle** | Сезонные тренды | 30-50 лет OHLC | Сезонная кривая |
| **FTE** | Валидация сезонности | Прогноз/Факт | Статус (VALID/BROKEN) |
| **Decennial Patterns** | 10-летние циклы | Годы по digit (0-9) | Усреднённые паттерны |
| **QSpectrum** | Циклическая корреляция | Ценовой ряд | 3 доминантных цикла |
| **Composite Line** | Прогнозная линия | 3 цикла | BUY/SELL сигналы |
| **Phenomenological** | Исторические аналогии | DTW, корреляция | Best Matches |
| **U-Turn** | Разворотные точки | Экстремумы | Даты разворота |
| **COT/Commercials** | Позиции хеджеров | Отчёты CFTC | COT Index (0-100) |
| **Qualified Trend Break** | Фильтрация пробоев | Циклы + уровни | Confirm/False |

### 📊 Composite Line

Главный инструмент прогнозирования — **Composite Line**, который:

1. Накладывает три цикла разной длины (короткий, средний, длинный)
2. Детектирует точки **резонанса** (когда все три цикла направлены в одну сторону)
3. Генерирует сигналы **BUY** / **SELL** с оценкой силы

### 🎯 Forward Testing Efficiency (FTE)

Все модели валидируются через FTE:

```
In-Sample (70%) → Обучение модели
Out-Sample (30%) → Тестирование
Результат: Корреляция прогноза с фактом

- FTE > 0.3: STRONG (сильная модель)
- FTE > 0: VALID (рабочая модель)
- FTE < 0: BROKEN (игнорировать)
```

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│   Web SPA (React)  │  Desktop (Electron)  │  CLI (Go)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      GATEWAY LAYER                           │
│   REST API (Gin)  │  gRPC  │  WebSocket  │  GraphQL         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                           │
│   AnnualCycle  │  Decennial  │  Composite  │  Phenom        │
│   UTurn        │  COT        │  QTB        │  Workflow      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│   PostgreSQL + TimescaleDB  │  Redis  │  MinIO/S3           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Backend** | Go 1.22+ |
| **Frontend** | React 18 + TypeScript + Vite |
| **Database** | PostgreSQL 16 + TimescaleDB |
| **Cache** | Redis 7 |
| **Queue** | Asynq (Go) |
| **API** | REST (Gin) + gRPC |
| **Charts** | Lightweight Charts |
| **Containerization** | Docker + Docker Compose |
| **Monitoring** | Prometheus + Grafana |

---

## 📦 Установка

### Требования

- Go 1.22+
- Docker & Docker Compose
- Node.js 18+ (для frontend)
- Make

### Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/your-org/cyclecast.git
cd cyclecast

# Установка зависимостей
make deps

# Запуск инфраструктуры
make docker-up

# Применение миграций
make migrate-up

# Запуск API сервера
make run-api
```

### Переменные окружения

```bash
# .env
DB_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your_jwt_secret_key
```

---

## 🚀 Использование

### CLI

```bash
# Импорт данных
./bin/cli import --symbol AAPL --source yahoo --from 1980-01-01 --to 2024-12-31

# Annual Cycle анализ
./bin/cli annual-cycle --symbol AAPL --years 30 --output annual.json

# Composite Line с сигналами
./bin/cli composite --symbol AAPL --forecast 100

# Decennial Patterns
./bin/cli decennial --symbol "^DJI" --digit 4

# Полный workflow (Ларри Вильямс)
./bin/cli williams --symbols AAPL,MSFT,GLD --lookahead 60
```

### REST API

```bash
# Получить исторические данные
curl "http://localhost:8080/api/v1/market/symbols/AAPL/history?timeframe=1d"

# Annual Cycle анализ
curl -X POST "http://localhost:8080/api/v1/analysis/annual-cycle" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "min_years": 30
  }'

# FTE валидация
curl -X POST "http://localhost:8080/api/v1/analysis/fte" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "in_sample_ratio": 0.7
  }'

# Composite Line с сигналами
curl -X POST "http://localhost:8080/api/v1/analysis/composite" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "forecast_length": 100
  }'

# Decennial Patterns
curl -X POST "http://localhost:8080/api/v1/analysis/decennial" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "^DJI",
    "year_digit": 4
  }'

# Phenomenological Model
curl -X POST "http://localhost:8080/api/v1/analysis/phenom" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "training_interval": 100,
    "use_decennial_filter": true,
    "top_matches": 10
  }'

# COT анализ
curl "http://localhost:8080/api/v1/cot/GC" # Gold

# Полный workflow Ларри Вильямса
curl -X POST "http://localhost:8080/api/v1/workflow/williams" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "GLD"],
    "look_ahead_days": 60,
    "forecast_days": 100,
    "min_fte": 0.0
  }'
```

---

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Описание |
|--------|----------|----------|
| `GET` | `/api/v1/market/symbols` | Список инструментов |
| `GET` | `/api/v1/market/symbols/{symbol}/history` | Исторические данные |
| `POST` | `/api/v1/market/import` | Импорт данных |
| `POST` | `/api/v1/analysis/annual-cycle` | Annual Cycle анализ |
| `POST` | `/api/v1/analysis/fte` | FTE валидация |
| `POST` | `/api/v1/analysis/qspectrum` | QSpectrum анализ |
| `POST` | `/api/v1/analysis/composite` | Composite Line |
| `POST` | `/api/v1/analysis/decennial` | Decennial Patterns |
| `POST` | `/api/v1/analysis/phenom` | Phenomenological Model |
| `POST` | `/api/v1/analysis/uturn` | U-Turn детекция |
| `POST` | `/api/v1/analysis/qtb` | Qualified Trend Break |
| `GET` | `/api/v1/cot/{symbol}` | COT данные |
| `POST` | `/api/v1/cot/import` | Импорт COT |
| `POST` | `/api/v1/workflow/williams` | Полный workflow |
| `GET` | `/api/v1/signals/{symbol}` | Активные сигналы |

Полная документация: `http://localhost:8080/swagger/index.html`

---

## 🔬 Алгоритмы

### Annual Cycle (Сезонность)
```
1. Загрузить 30-50 лет исторических данных
2. Детрендинг: Detrended = Price - MA(t)
3. Нормализация каждого года к 0-1
4. Расчёт среднего для каждого дня года
5. FTE валидация на out-of-sample данных
```

### QSpectrum (Циклическая корреляция + МЭМ)

> **Важно:** QSpectrum **НЕ использует FFT**!
> Разработан специально для нестационарных финансовых данных.

```
Методы QSpectrum:

1. Циклическая корреляция (основной):
   C(period) = Σ P(t) × P(t-period) / (N - period)

2. Энергия цикла:
   E(period) = |C(period)| × √(N/period) × WFA_Stability

3. МЭМ — спектральная плотность (Burg's method, опционально):
   P(f) = σ² / |1 + Σ aₖ × e^(-i2πfk)|²

4. Walk-Forward Stability:
   WFA_Stability = Count(Correlation > 0) / Total_Periods

Отличие от FFT:
- FFT: стационарные данные, запаздывание
- QSpectrum: нестационарные (цена), минимум запаздывания
- QSpectrum: учитывает устойчивость циклов через WFA
```

### Composite Line & Сигналы
```
1. Выбор трёх циклов: короткий, средний, длинный
2. Проекция каждого цикла: A × sin(2π × t / P + φ)
3. Суммирование: Composite = Σ projections
4. Детекция резонанса:
   - BUY: все 3 цикла направлены вверх
   - SELL: все 3 цикла направлены вниз
```

### Decennial Patterns
```
1. Группировка по yearDigit (0-9)
2. Нормализация каждого года к 0-1
3. Расчёт среднего для каждого дня года
4. Сравнение текущего года с паттерном через корреляцию
```

### COT Index
```
COT_Index = (Current_Net - Min_N) / (Max_N - Min_N) × 100

Где:
- Net = Commercials_Long - Commercials_Short
- N = период (26 или 52 недели)

Сигналы:
- COT_Index > 80: Commercials в покупках (BULLISH)
- COT_Index < 20: Commercials в продажах (BEARISH)
```

---

## 📊 Примеры результатов

### Annual Cycle Result

```json
{
  "cycle": [
    {"day_of_year": 1, "avg_value": 0.52, "std_dev": 0.15, "pos_percent": 0.58},
    {"day_of_year": 2, "avg_value": 0.54, "std_dev": 0.14, "pos_percent": 0.60},
    ...
  ],
  "years_used": 35,
  "is_valid": true
}
```

### Composite Line with Signals

```json
{
  "line": [0.15, 0.22, 0.18, ...],
  "short_cycle": [0.08, 0.12, 0.05, ...],
  "medium_cycle": [0.04, 0.06, 0.08, ...],
  "long_cycle": [0.03, 0.04, 0.05, ...],
  "signals": [
    {"type": "BUY", "strength": 0.78, "index": 15, "reason": "Triple resonance UP"},
    {"type": "SELL", "strength": 0.65, "index": 67, "reason": "Triple resonance DOWN"}
  ],
  "uturns": [
    {"index": 10, "type": "BOTTOM", "value": -0.12, "confidence": 0.85},
    {"index": 45, "type": "TOP", "value": 0.35, "confidence": 0.72}
  ]
}
```

### Williams Workflow Result

```json
{
  "active_assets": [
    {
      "symbol": "GLD",
      "seasonality": {...},
      "fte": {"correlation": 0.35, "status": "STRONG"},
      "decennial": {...},
      "composite": {...},
      "cot": {"last_signal": "BULLISH", "commercial_index": 85}
    }
  ],
  "signals": [
    {
      "symbol": "GLD",
      "type": "BUY",
      "strength": 0.82,
      "timestamp": "2024-03-15",
      "reason": "Composite + COT + Phenom confirmation"
    }
  ],
  "status": "SUCCESS"
}
```

---

## 📁 Структура проекта

```
cyclecast/
├── cmd/                    # Точки входа
│   ├── api/               # API сервер
│   ├── worker/            # Background worker
│   └── cli/               # CLI инструмент
├── internal/              # Внутренние пакеты
│   ├── domain/           # Доменные модели
│   ├── service/          # Бизнес-логика
│   │   ├── seasonality/  # Annual Cycle, FTE
│   │   ├── cycle/        # QSpectrum, Composite
│   │   ├── decennial/    # Decennial Patterns
│   │   ├── phenomenological/ # Исторические аналогии
│   │   ├── uturn/        # Разворотные точки
│   │   ├── cot/          # COT анализ
│   │   ├── qtb/          # Qualified Trend Break
│   │   └── workflow/     # Williams Workflow
│   ├── repository/       # Репозитории
│   └── transport/        # API handlers
├── pkg/                   # Публичные пакеты
│   ├── mathutil/         # Математические утилиты
│   └── finance/          # Финансовые инструменты
├── api/                   # API определения
├── migrations/            # SQL миграции
├── configs/               # Конфигурация
├── deployments/           # Docker, Kubernetes
├── docs/                  # Документация
└── web/                   # Frontend
```

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [PLAN.md](docs/PLAN.md) | Детальный план разработки |
| [TZ.md](docs/TZ.md) | Техническое задание |
| [TECHNICAL_SOLUTION.md](docs/TECHNICAL_SOLUTION.md) | Техническое решение |

---

## 🧪 Тестирование

```bash
# Unit тесты
make test

# Тесты с покрытием
make test-coverage

# Интеграционные тесты
go test ./tests/integration/... -v

# Нагрузочное тестирование
k6 run tests/load/api_load.js
```

---

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

## 📄 Лицензия

MIT License. См. [LICENSE](LICENSE) для деталей.

---

## ⚠️ Disclaimer

**ВАЖНО**: Данная система предназначена исключительно для исследовательских и образовательных целей. Прошлые результаты не гарантируют будущих доходов. Любые торговые решения принимаются на ваш собственный риск. Авторы не несут ответственности за финансовые потери.

---

## 📞 Контакты

- **Issues**: [GitHub Issues](https://github.com/your-org/cyclecast/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/cyclecast/discussions)

---

<p align="center">
  <b>CycleCast</b> — Циклический анализ по методологии Ларри Вильямса
</p>

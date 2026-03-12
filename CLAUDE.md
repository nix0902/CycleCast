# CLAUDE.md - Quick Reference для ИИ Агентов

> **Версия:** 3.2 Final | **Обновлено:** 2026-03-12

## 🗺️ КАРТА ПРОЕКТА (Top-Level)

```
cyclecast/
├── frontend/          # React Web Application (TypeScript)
├── backend/           # Go Core API Server
├── quant/             # Python Math/ML Services
├── infrastructure/    # Docker, K8s, Terraform
├── database/          # Migrations, Schemas, Seeds
├── docs/              # Документация проекта
├── scripts/           # Utility scripts
└── configs/           # Конфигурации (YAML, ENV)
```

---

## 📂 ДЕТАЛЬНАЯ СТРУКТУРА

### frontend/ (React + TypeScript)
```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui primitives
│   │   ├── charts/             # Lightweight Charts wrappers
│   │   ├── dashboard/          # Dashboard widgets
│   │   ├── analysis/           # Analysis panels
│   │   └── backtest/           # Backtest visualisation
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities, API clients
│   ├── stores/                 # Zustand stores
│   ├── types/                  # TypeScript types
│   └── styles/                 # Tailwind, global CSS
├── public/                     # Static assets
└── tests/                      # Frontend tests
```

### backend/ (Go)
```
backend/
├── cmd/                        # Entry points
│   ├── api/                    # API server main
│   ├── worker/                 # Background worker main
│   └── cli/                    # CLI tools main
├── internal/                   # Private packages
│   ├── domain/                 # Domain models
│   ├── service/                # Business logic
│   │   ├── marketdata/
│   │   ├── seasonality/
│   │   ├── cycle/
│   │   ├── cot/
│   │   ├── risk/
│   │   ├── backtest/
│   │   ├── lineage/
│   │   └── workflow/
│   ├── repository/             # Data access
│   ├── transport/              # API handlers
│   │   ├── rest/
│   │   ├── grpc/
│   │   └── ws/
│   └── pkg/                    # Internal utilities
├── pkg/                        # Public packages
└── tests/                      # Backend tests
```

### quant/ (Python)
```
quant/
├── qspectrum/                  # Циклическая корреляция + MEM
├── phenom/                     # DTW гибридный
├── wfa/                        # Walk-Forward Analysis
├── bootstrap/                  # Bootstrap CI (streaming)
├── chow_test/                  # Structural break detection
├── shared/                     # Shared utilities
├── proto/                      # gRPC protobuf definitions
├── tests/
└── main.py                     # gRPC server entry
```

### infrastructure/
```
infrastructure/
├── docker/                     # Dockerfiles
├── kubernetes/                 # K8s manifests
├── terraform/                  # Infrastructure as Code
└── monitoring/                 # Prometheus, Grafana
```

### database/
```
database/
├── migrations/                 # SQL migrations
├── schemas/                    # Schema definitions
├── seeds/                      # Test data
└── timescaledb/                # TimescaleDB setup
```

### docs/
```
docs/
├── TZ.md                       # Техническое задание
├── PLAN.md                     # План разработки
├── TECHNICAL_SOLUTION.md       # Техническое решение
├── FILE_STRUCTURE.md           # Детальная структура
├── API.md                      # API документация
└── algorithms/                 # Описания алгоритмов
```

---

## 🔑 КЛЮЧЕВЫЕ ФАЙЛЫ (Quick Access)

| Назначение | Путь |
|------------|------|
| **ТЗ** | `docs/TZ.md` |
| **План разработки** | `docs/PLAN.md` |
| **Тех. решение** | `docs/TECHNICAL_SOLUTION.md` |
| **API сервер** | `backend/cmd/api/main.go` |
| **Python gRPC** | `quant/main.py` |
| **Frontend entry** | `frontend/src/app/page.tsx` |
| **gRPC proto** | `quant/proto/quant.proto` |
| **DB migrations** | `database/migrations/` |
| **Docker Compose** | `infrastructure/docker/docker-compose.yml` |
| **Config** | `configs/config.yaml` |

---

## 📝 КОНВЕНЦИИ

### Именование файлов
| Тип | Pattern | Пример |
|-----|---------|--------|
| Go service | `*_service.go` | `marketdata_service.go` |
| Go repository | `*_repository.go` | `signal_repository.go` |
| Go handler | `*_handler.go` | `analysis_handler.go` |
| React component | `PascalCase.tsx` | `CompositeLineChart.tsx` |
| React hook | `use*.ts` | `useAnnualCycle.ts` |
| Python module | `snake_case.py` | `burg_mem.py` |
| Test (Go) | `*_test.go` | `backdate_test.go` |
| Test (Python) | `test_*.py` | `test_dtw.py` |
| Migration | `NNNN_description.sql` | `0001_initial_schema.sql` |

### Структура Go модуля
```
service/
├── service.go          # Interface definition
├── service_impl.go     # Implementation
├── repository.go       # Data access interface
├── repository_pg.go    # PostgreSQL implementation
├── models.go           # Domain models
└── service_test.go     # Tests
```

### Структура Python модуля
```
module/
├── __init__.py
├── core.py             # Main logic
├── utils.py            # Helpers
├── types.py            # Type definitions
└── test_core.py        # Tests
```

---

## 🚀 ЧАСТЫЕ ОПЕРАЦИИ

### Добавить новый API endpoint
1. Domain: `backend/internal/domain/new_model.go`
2. Service: `backend/internal/service/new_service/`
3. Handler: `backend/internal/transport/rest/new_handler.go`
4. Route: `backend/internal/transport/rest/routes.go`

### Добавить новый Python алгоритм
1. Module: `quant/new_algorithm/`
2. Proto: `quant/proto/quant.proto` (если нужен gRPC)
3. Integration: `quant/main.py`
4. Go client: `backend/internal/pkg/quant_client/`

### Добавить React компонент
1. Component: `frontend/src/components/category/Component.tsx`
2. Types: `frontend/src/types/component.ts`
3. Hook (если нужен): `frontend/src/hooks/useComponent.ts`

### Добавить миграцию БД
1. Migration: `database/migrations/NNNN_description.sql`
2. Apply: `make migrate-up`

---

## ⚡ COMMANDS

```bash
# Backend
make run-api          # Запуск API сервера
make run-worker       # Запуск worker
make test             # Тесты
make migrate-up       # Миграции БД

# Frontend
cd frontend && bun dev

# Python Quant
cd quant && python main.py

# Docker
docker-compose up -d
```

---

## 📊 ТЕКУЩИЙ СТАТУС

| Компонент | Статус | Фаза |
|-----------|--------|------|
| Backend (Go) | Не начат | Phase 1 |
| Python Quant | Не начат | Phase 0 |
| Frontend | Не начат | Phase 10 |
| Database | Не начат | Phase 1 |
| Infrastructure | Не начат | Phase 1 |

**Следующий шаг:** Phase 0 - Backtesting & Math Prototyping

---

_Этот файл оптимизирован для ИИ агентов с ограниченным контекстом._

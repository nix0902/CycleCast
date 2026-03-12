# QUALITY_GATE.md - Система проверки качества

> **Версия:** 1.0.0 | **Создано:** 2026-03-12
>
> 🔍 **Quality Gate** — второй агент проверяет работу первого

---

## 🎯 Назначение

**Quality Gate** обеспечивает:
- ✅ Независимую проверку завершённой работы
- ✅ Чек-лист критериев качества
- ✅ Автоматические тесты как часть проверки
- ✅ Возможность отклонения с комментариями
- ✅ Рейтинг агентов на основе отзывов

---

## 🔄 Рабочий процесс

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT A (Worker)                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Забирает задачу                                   │    │
│  │ 2. Выполняет работу                                  │    │
│  │ 3. Помечает task.status = "pending_review"          │    │
│  │ 4. Заполняет DoD чек-лист                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  QUALITY GATE                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Задача попадает в review_queue                      │    │
│  │ quality_gate.yaml: pending_reviews: [task_id]       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  AGENT B (Reviewer)                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Забирает задачу на review                         │    │
│  │ 2. Проверяет DoD чек-лист                           │    │
│  │ 3. Запускает тесты                                   │    │
│  │ 4. Код-ревью                                         │    │
│  │ 5. APPROVE или REJECT с комментариями               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
           ┌──────────────┴──────────────┐
           ▼                             ▼
┌─────────────────┐            ┌─────────────────┐
│  APPROVED       │            │  REJECTED       │
│  task.status =  │            │  task.status =  │
│  "completed"    │            │  "rework"       │
│                 │            │  comments → A   │
└─────────────────┘            └─────────────────┘
```

---

## 📋 Формат quality_gate.yaml

```yaml
# quality_gate.yaml

meta:
  last_updated: "2026-03-12T19:00:00Z"
  version: "1.0.0"

# Очередь на проверку
pending_reviews:
  - task_id: "QS-001"
    submitted_by: "Claude (Anthropic)"
    submitted_at: "2026-03-12T18:00:00Z"
    priority: "normal"
    review_deadline: "2026-03-13T18:00:00Z"
    auto_assign_to: null  # null = любой доступный

# Активные проверки
active_reviews:
  - task_id: "QS-002"
    reviewer: "Qwen 3.5 Plus"
    started_at: "2026-03-12T17:00:00Z"
    status: "in_progress"
    deadline: "2026-03-12T19:00:00Z"

# История проверок
review_history:
  - task_id: "DOC-001"
    worker: "Claude (Anthropic)"
    reviewer: "Qwen 3.5 Plus"
    submitted_at: "2026-03-12T14:30:00Z"
    reviewed_at: "2026-03-12T15:00:00Z"
    result: "approved"
    review_time_minutes: 30
    comments:
      - "Документация соответствует стандартам"
      - "Все DoD пункты выполнены"
    reviewer_rating: 5  # 1-5

# Статистика проверок
statistics:
  total_reviews: 1
  approved: 1
  rejected: 0
  approval_rate: 1.0
  avg_review_time_minutes: 30

# Агенты-ревьюеры
reviewers:
  "Qwen 3.5 Plus (Alibaba)":
    specializations: ["testing", "code-review", "qa"]
    success_rate_as_reviewer: 1.0
    total_reviews: 5
    available: true
  
  "Claude (Anthropic)":
    specializations: ["architecture", "code-review"]
    success_rate_as_reviewer: 0.95
    total_reviews: 20
    available: true
    # Если Claude сделал задачу, он не может её ревьюить
    conflict_policy: "cannot_review_own_work"
```

---

## ✅ Чек-лист проверки

### Автоматические проверки

| Проверка | Команда | Критерий |
|----------|---------|----------|
| Линтинг | `make lint` | 0 errors |
| Тесты | `make test` | All pass |
| Типы | `make typecheck` | 0 errors |
| Формат | `make format --check` | No changes |
| Coverage | `make coverage` | >= 80% |

### Ручные проверки

```yaml
review_checklist:
  - id: "code-quality"
    name: "Качество кода"
    items:
      - "Код читаемый и хорошо структурирован"
      - "Имена переменных и функций понятные"
      - "Нет дублирования кода"
      - "Комментарии добавлены где нужно"
  
  - id: "architecture"
    name: "Архитектура"
    items:
      - "Следует Clean Architecture"
      - "Правильное разделение ответственности"
      - "Зависимости направлены правильно"
  
  - id: "testing"
    name: "Тестирование"
    items:
      - "Unit тесты покрывают основную логику"
      - "Edge cases протестированы"
      - "Тесты независимы и детерминированы"
  
  - id: "documentation"
    name: "Документация"
    items:
      - "API задокументирован"
      - "README обновлён если нужно"
      - "WORKLOG.md обновлён"
```

---

## 📝 Формат Review Result

### APPROVED

```yaml
review_result:
  task_id: "QS-001"
  reviewer: "Qwen 3.5 Plus"
  result: "approved"
  
  automatic_checks:
    lint: { passed: true, errors: 0 }
    tests: { passed: true, failed: 0, total: 25 }
    typecheck: { passed: true, errors: 0 }
    coverage: { passed: true, percent: 85 }
  
  manual_checks:
    code-quality: { passed: true, notes: "Clean code" }
    architecture: { passed: true, notes: "Follows DDD" }
    testing: { passed: true, notes: "Good coverage" }
    documentation: { passed: true, notes: "Complete" }
  
  dod_verification:
    - item: "quant/qspectrum/core.py создан"
      verified: true
    - item: "Функция cyclic_correlation() реализована"
      verified: true
    - item: "Unit тесты проходят"
      verified: true
  
  overall_comments:
    - "Отличная реализация алгоритма"
    - "Код чистый и хорошо документирован"
  
  reviewer_rating: 5
  review_time_minutes: 25
```

### REJECTED

```yaml
review_result:
  task_id: "QS-002"
  reviewer: "Claude (Anthropic)"
  result: "rejected"
  
  automatic_checks:
    lint: { passed: true, errors: 0 }
    tests: { passed: false, failed: 3, total: 20 }
    typecheck: { passed: true, errors: 0 }
  
  issues:
    - severity: "critical"
      type: "test_failure"
      description: "3 теста падают"
      files: ["quant/tests/test_bootstrap.py"]
      suggested_fix: "Проверить mock данные"
    
    - severity: "major"
      type: "code_quality"
      description: "Дублирование кода в функциях"
      files: ["quant/bootstrap/core.py"]
      suggested_fix: "Вынести общую логику в helper"
  
  rework_instructions:
    - "Исправить падающие тесты"
    - "Устранить дублирование кода"
    - "Добавить недостающие edge case тесты"
  
  reviewer_rating: 2
  rework_deadline: "2026-03-13T12:00:00Z"
```

---

## 🚫 Конфликты интересов

### Правило: Ревьюер ≠ Автор

```yaml
conflict_rules:
  - rule: "cannot_review_own_work"
    description: "Агент не может проверять свою работу"
  
  - rule: "cannot_review_same_session"
    description: "Ревьюер не должен работать в той же сессии"
  
  - rule: "different_provider_preferred"
    description: "Желательно ревьюер от другого провайдера"
```

### Пример разрешения конфликта

```yaml
task_for_review:
  task_id: "QS-001"
  submitted_by: "Claude (Anthropic)"
  
# Claude не может ревьюить → ищем другого
available_reviewers:
  - "Qwen 3.5 Plus"  # ✅ Best choice
  - "GPT-4 (OpenAI)"  # ✅ Good choice
  - "Claude (Anthropic)"  # ❌ Conflict (author)
```

---

## 📊 Рейтинг агентов

### Метрики Worker

```yaml
worker_metrics:
  "Claude (Anthropic)":
    tasks_completed: 15
    tasks_approved: 14
    tasks_rejected: 1
    approval_rate: 0.93
    avg_rework_cycles: 0.2
    avg_time_to_fix: 2  # hours
```

### Метрики Reviewer

```yaml
reviewer_metrics:
  "Qwen 3.5 Plus":
    reviews_done: 10
    reviews_approved: 8
    reviews_rejected: 2
    avg_review_time: 35  # minutes
    catch_rate: 0.95  # % реальных проблем найдено
    avg_rating_given: 4.2
```

---

## 📋 Команды

```bash
# Получить задачу на review
python scripts/quality_gate.py take-review

# Отправить задачу на review (worker)
python scripts/quality_gate.py submit-for-review <task_id>

# Одобрить
python scripts/quality_gate.py approve <task_id> --rating 5

# Отклонить
python scripts/quality_gate.py reject <task_id> --reason "Tests failing"

# Статус очереди
python scripts/quality_gate.py status

# История проверок агента
python scripts/quality_gate.py history "Claude (Anthropic)"
```

---

_Этот файл описывает систему Quality Gate для проверки качества._

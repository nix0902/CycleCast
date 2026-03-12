# AUTO_ASSIGNMENT.md - Автоматическое распределение задач

> **Версия:** 1.0.0 | **Создано:** 2026-03-12
>
> 🎯 Автоматический подбор агентов для задач на основе навыков

---

## 🎯 Назначение

**Auto-Assignment** обеспечивает:
- ✅ Автоматический подбор агента под задачу
- ✅ Учёт навыков и специализации агентов
- ✅ Балансировку нагрузки между агентами
- ✅ Приоритизацию по производительности

---

## 📊 Модель навыков

### Навыки агентов (agent_skills.yaml)

```yaml
agents:
  "Claude (Anthropic)":
    skills:
      - name: "python"
        level: 9  # 1-10
        experience: "expert"
      - name: "go"
        level: 8
        experience: "advanced"
      - name: "math"
        level: 9
        experience: "expert"
      - name: "architecture"
        level: 9
        experience: "expert"
      - name: "documentation"
        level: 10
        experience: "expert"
    specializations:
      - "quantitative-analysis"
      - "algorithm-design"
      - "documentation"
    preferences:
      preferred_task_types: ["algorithm", "architecture", "documentation"]
      avoid_task_types: ["ui", "css"]
    performance:
      success_rate: 0.95
      avg_completion_time_factor: 0.9  # быстрее среднего
      last_10_tasks_outcome: ["success"] * 9 + ["partial"]

  "GPT-4 (OpenAI)":
    skills:
      - name: "python"
        level: 9
        experience: "expert"
      - name: "typescript"
        level: 9
        experience: "expert"
      - name: "react"
        level: 9
        experience: "expert"
      - name: "go"
        level: 7
        experience: "intermediate"
    specializations:
      - "frontend"
      - "api-design"
      - "testing"
    preferences:
      preferred_task_types: ["frontend", "api", "testing"]
      avoid_task_types: ["complex-math"]
    performance:
      success_rate: 0.92
      avg_completion_time_factor: 1.0

  "Kimi K2.5 (Moonshot)":
    skills:
      - name: "python"
        level: 8
        experience: "advanced"
      - name: "math"
        level: 7
        experience: "advanced"
      - name: "documentation"
        level: 8
        experience: "advanced"
    specializations:
      - "data-analysis"
      - "documentation"
    preferences:
      preferred_task_types: ["data", "documentation", "testing"]
      avoid_task_types: ["architecture", "frontend"]
    performance:
      success_rate: 0.88
      avg_completion_time_factor: 1.1

  "Qwen 3.5 Plus (Alibaba)":
    skills:
      - name: "python"
        level: 8
        experience: "advanced"
      - name: "go"
        level: 7
        experience: "intermediate"
      - name: "testing"
        level: 9
        experience: "expert"
    specializations:
      - "testing"
      - "code-review"
      - "bug-fixing"
    preferences:
      preferred_task_types: ["testing", "review", "bugfix"]
      avoid_task_types: []
    performance:
      success_rate: 0.90
      avg_completion_time_factor: 1.0
```

### Требования задач (в tasks.yaml)

```yaml
tasks:
  - id: QS-001
    title: "QSpectrum Python Prototype"
    required_skills:
      - name: "python"
        min_level: 8
      - name: "math"
        min_level: 7
    preferred_specializations:
      - "quantitative-analysis"
      - "algorithm-design"
    task_type: "algorithm"
    complexity: "high"
    estimated_hours: 8
```

---

## 🔢 Алгоритм назначения

### Формула скоринга

```
AgentScore = 
  SkillsMatch × 0.4 +
  SpecializationMatch × 0.25 +
  PerformanceScore × 0.20 +
  LoadBalance × 0.15

Где:
- SkillsMatch: % требований навыков выполнено
- SpecializationMatch: 1.0 если специализация совпадает, иначе 0.5
- PerformanceScore: success_rate × (1 - time_factor)
- LoadBalance: 1.0 / (active_tasks + 1)
```

### Пример расчёта

```
Задача: QS-001 (требует python:8+, math:7+)

Claude:
  SkillsMatch:
    - python: 9/8 = 1.0 (meets requirement)
    - math: 9/7 = 1.0 (meets requirement)
    → SkillsMatch = 1.0
  
  SpecializationMatch:
    - "quantitative-analysis" ∈ specializations → 1.0
  
  PerformanceScore:
    - success_rate = 0.95
    - time_factor = 0.9
    → 0.95 × 0.9 = 0.855
  
  LoadBalance:
    - active_tasks = 0
    → 1.0 / (0 + 1) = 1.0
  
  Total = 1.0×0.4 + 1.0×0.25 + 0.855×0.20 + 1.0×0.15
        = 0.40 + 0.25 + 0.17 + 0.15
        = 0.97

GPT-4:
  SkillsMatch:
    - python: 9/8 = 1.0 ✓
    - math: 5/7 = 0.71 ✗ (ниже минимума)
    → DISQUALIFIED (math не хватает)

Результат: Claude (0.97) → НАЗНАЧЕН
```

---

## 🔄 Рабочий процесс

```
┌─────────────────────────────────────────────────────────────┐
│  1. Новая задача добавлена в tasks.yaml                     │
│     status: pending                                          │
│     assignee: null                                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Auto-Assignment Engine запускается                       │
│     python scripts/auto_assign.py assign QS-001              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Расчёт скоринга для всех доступных агентов              │
│     → Фильтрация по минимальным требованиям                 │
│     → Ранжирование по скорингу                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Назначение лучшего агента                               │
│     tasks.yaml: assignee: "Claude"                          │
│     session.yaml: создаётся reserved сессия                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Уведомление агента                                      │
│     → Агент видит назначенную задачу в status               │
│     → Агент подтверждает (accept) или отклоняет (decline)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Команды

```bash
# Автоматическое назначение задачи
python scripts/auto_assign.py assign <task_id>

# Назначить все pending задачи
python scripts/auto_assign.py assign-all

# Посмотреть рекомендации (без назначения)
python scripts/auto_assign.py recommend <task_id>

# Обновить статистику агентов
python scripts/auto_assign.py update-stats

# Посмотреть профиль агента
python scripts/auto_assign.py agent-profile "Claude (Anthropic)"
```

---

## ⚖️ Балансировка нагрузки

### Стратегии

| Стратегия | Описание |
|-----------|----------|
| `best_fit` | Лучший по навыкам (default) |
| `round_robin` | По очереди между агентами |
| `least_loaded` | Агент с минимумом задач |
| `performance` | По success_rate |

### Конфигурация

```yaml
auto_assignment:
  strategy: "best_fit"
  min_score_threshold: 0.6  # Минимальный скоринг для назначения
  allow_manual_override: true
  max_tasks_per_agent: 3
  reassign_on_timeout: true
  reassign_on_decline: true
```

---

## 🚫 Обработка отказов

### Decline от агента

```yaml
declines:
  - task_id: "QS-001"
    agent: "Claude"
    reason: "context_limit_reached"
    timestamp: "2026-03-12T18:00:00Z"
    action: "reassign_to_next_best"
```

### Timeout (агент не принял)

```yaml
assignment_timeouts:
  - task_id: "QS-002"
    assigned_to: "Kimi"
    assigned_at: "2026-03-12T16:00:00Z"
    timeout_at: "2026-03-12T16:30:00Z"
    action: "reassign"
```

---

## 📊 Метрики

```yaml
assignment_metrics:
  total_assignments: 15
  successful_assignments: 13
  declined_assignments: 2
  auto_reassigned: 1
  
  agent_performance:
    "Claude":
      assigned: 8
      completed: 7
      declined: 1
      success_rate: 0.875
    "GPT-4":
      assigned: 5
      completed: 5
      declined: 0
      success_rate: 1.0
```

---

_Этот файл описывает систему автоматического распределения задач._

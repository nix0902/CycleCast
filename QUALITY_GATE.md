# Quality Gate - Документация

## Обзор

**Quality Gate** — система валидации завершённых задач перед их финальным принятием. Обеспечивает качество работы через автоматические проверки и ручной review.

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY GATE SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Task Completed                                                 │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  QUALITY CHECKS                          │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ Structural  │  │ Functional  │  │ Visual      │     │   │
│  │  │ Validation  │  │ Validation  │  │ Validation  │     │   │
│  │  │             │  │             │  │             │     │   │
│  │  │ • Files     │  │ • Code      │  │ • UI        │     │   │
│  │  │ • Config    │  │ • Tests     │  │ • Charts    │     │   │
│  │  │ • Progress  │  │ • Logic     │  │ • Patterns  │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │         │                │                │              │   │
│  │         └────────────────┴────────────────┘              │   │
│  │                          │                                │   │
│  └──────────────────────────┼────────────────────────────────┘   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  SCORING ENGINE                          │   │
│  │                                                          │   │
│  │  Score = Σ(checks × weights)                             │   │
│  │                                                          │   │
│  │  Thresholds:                                             │   │
│  │  • 90+ = Excellent ✅                                    │   │
│  │  • 75-89 = Good ✅                                       │   │
│  │  • 60-74 = Acceptable ⚠️                                 │   │
│  │  • <60 = Failed ❌                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│              ┌──────────────┴──────────────┐                   │
│              ▼                             ▼                    │
│  ┌──────────────────┐           ┌──────────────────┐          │
│  │    PASSED        │           │    FAILED        │          │
│  │  ✅ Task Done    │           │  ❌ Return to    │          │
│  │  Update Progress │           │     Agent        │          │
│  │  Notify User     │           │  Create Issues   │          │
│  └──────────────────┘           └──────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Категории проверок

### 1. Структурная валидация (Structural)

| Проверка | Описание | Вес |
|----------|----------|-----|
| `files_created` | Все файлы созданы | 15% |
| `files_structure` | Правильная структура | 10% |
| `config_valid` | YAML/JSON валидны | 10% |
| `progress_updated` | progress.yaml обновлён | 10% |
| `worklog_updated` | worklog.md обновлён | 5% |

### 2. Функциональная валидация (Functional)

| Проверка | Описание | Вес |
|----------|----------|-----|
| `code_compiles` | Код компилируется | 15% |
| `tests_pass` | Тесты проходят | 15% |
| `no_errors` | Нет runtime ошибок | 10% |
| `logic_correct` | Логика корректна | 10% |

### 3. Визуальная валидация (Visual)

| Проверка | Описание | Вес |
|----------|----------|-----|
| `ui_renders` | UI корректно отображается | 10% |
| `responsive` | Адаптивность работает | 5% |
| `chart_accuracy` | Графики точны | 10% |
| `pattern_recognition` | Паттерны распознаны | 5% |

## Проверки по типам задач

### Backend Tasks

```yaml
checks:
  structural:
    - files_created
    - files_structure
    - config_valid
    - progress_updated
  functional:
    - code_compiles
    - tests_pass
    - no_errors
    - api_responds
    - db_queries_work
```

### Frontend Tasks

```yaml
checks:
  structural:
    - files_created
    - components_valid
    - styles_applied
  functional:
    - code_compiles
    - no_console_errors
    - interactions_work
  visual:
    - ui_renders
    - responsive
    - accessibility
```

### Data/Analysis Tasks

```yaml
checks:
  structural:
    - output_files_created
    - format_correct
  functional:
    - calculations_correct
    - data_valid
    - no_nan_values
  visual:
    - charts_render
    - labels_correct
    - colors_accessible
```

### Vision Tasks (Candlestick/Chart Patterns)

```yaml
checks:
  structural:
    - input_processed
    - output_generated
  functional:
    - patterns_detected
    - accuracy_threshold_met
    - no_false_positives
  visual:
    - pattern_recognition
    - bounding_boxes_correct
    - confidence_scores_valid
```

## Конфигурация

```yaml
quality_gate:
  enabled: true
  min_score_threshold: 60
  
  categories:
    structural:
      weight: 0.30
      required: true
    functional:
      weight: 0.45
      required: true
    visual:
      weight: 0.25
      required: false
  
  scoring:
    excellent: 90
    good: 75
    acceptable: 60
    failed: 0
  
  actions:
    on_pass:
      - update_progress
      - notify_user
      - trigger_code_review
    on_fail:
      - create_issues
      - return_to_agent
      - notify_user
```

## Интеграция с Code Review Bot

```yaml
flow:
  1. Task Completed by Agent
  2. Quality Gate Validation
     ├── Passed (≥60) → Code Review Bot
     │                     ├── Approved → Task Done
     │                     └── Changes Required → Return to Agent
     └── Failed (<60) → Return to Agent with Issues
```

## Визуальные проверки детально

### UI Recognition Validation

```yaml
ui_checks:
  - name: "component_detection"
    description: "UI components correctly identified"
    method: "compare_with_expected"
    threshold: 0.85
  
  - name: "text_extraction"
    description: "Text correctly extracted from screenshot"
    method: "ocr_accuracy"
    threshold: 0.90
  
  - name: "layout_analysis"
    description: "Layout structure correctly analyzed"
    method: "structural_similarity"
    threshold: 0.80
```

### Candlestick Pattern Validation

```yaml
candlestick_checks:
  - name: "pattern_accuracy"
    description: "Correct pattern identification"
    method: "ground_truth_comparison"
    threshold: 0.85
  
  - name: "signal_direction"
    description: "Correct bullish/bearish signal"
    method: "direction_match"
    threshold: 0.90
  
  patterns:
    single_candle:
      - Doji
      - Hammer
      - Shooting Star
    double_candle:
      - Engulfing
      - Harami
      - Tweezer
    triple_candle:
      - Morning Star
      - Evening Star
      - Three Soldiers
```

### Chart Pattern Validation

```yaml
chart_pattern_checks:
  - name: "pattern_boundary"
    description: "Pattern boundaries correctly identified"
    method: "iou_score"
    threshold: 0.75
  
  - name: "breakout_prediction"
    description: "Breakout direction correctly predicted"
    method: "direction_accuracy"
    threshold: 0.70
  
  patterns:
    reversal:
      - Head and Shoulders
      - Double Top/Bottom
      - Triple Top/Bottom
    continuation:
      - Flag
      - Pennant
      - Triangle
```

## CLI Usage

```bash
# Запуск валидации
python scripts/quality_gate.py validate <task_id>

# Показать результаты
python scripts/quality_gate.py results <task_id>

# История проверок
python scripts/quality_gate.py history [--task-id <id>]

# Статистика
python scripts/quality_gate.py stats
```

## Отчёт о валидации

```markdown
## 🚦 Quality Gate Report

**Task**: TASK-001
**Agent**: GLM-5 (Zhipu AI)
**Date**: 2026-03-12T18:00:00Z
**Status**: ✅ PASSED

---

### 📊 Score Summary

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Structural | 95/100 | 30% | 28.5 |
| Functional | 88/100 | 45% | 39.6 |
| Visual | 92/100 | 25% | 23.0 |
| **Total** | **91.1/100** | | |

**Verdict**: Excellent ✅

---

### 🔍 Detailed Checks

#### Structural (95/100)

| Check | Status | Score |
|-------|--------|-------|
| files_created | ✅ | 100% |
| files_structure | ✅ | 100% |
| config_valid | ✅ | 100% |
| progress_updated | ⚠️ | 80% |

#### Functional (88/100)

| Check | Status | Score |
|-------|--------|-------|
| code_compiles | ✅ | 100% |
| tests_pass | ✅ | 100% |
| no_errors | ⚠️ | 85% |
| logic_correct | ✅ | 90% |

#### Visual (92/100)

| Check | Status | Score |
|-------|--------|-------|
| ui_renders | ✅ | 100% |
| responsive | ✅ | 95% |
| chart_accuracy | ✅ | 90% |
| pattern_recognition | ✅ | 85% |

---

### ⚠️ Warnings

1. `progress_updated`: Missing "last_updated" timestamp
2. `no_errors`: 2 console warnings detected

---

### 📋 Next Steps

- [ ] Code Review Bot will review the code
- [ ] Fix minor warnings (optional)
- [ ] Task will be marked as completed
```

## Обновление performance агентов

```yaml
# При прохождении Quality Gate
agent_performance_update:
  agent: "GLM-5 (Zhipu AI)"
  task: "TASK-001"
  
  quality_score: 91.1
  
  update:
    success_rate: "+0.01"
    total_tasks_completed: "+1"
    last_10_outcomes: "append success"
```

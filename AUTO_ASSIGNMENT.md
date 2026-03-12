# Auto-Assignment - Документация

## Обзор

**Auto-Assignment** — система автоматического распределения задач между ИИ-агентами на основе их навыков, специализаций и текущей нагрузки.

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTO-ASSIGNMENT SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  New Task                                                       │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────┐                                                │
│  │ Task Parser │ ──► Extract: type, skills, priority            │
│  └─────────────┘                                                │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────────────────────────────────────┐               │
│  │           AGENT MATCHER                      │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │               │
│  │  │ Skills  │ │ Special-│ │Perfor-  │       │               │
│  │  │ Match   │ │ ization │ │ mance   │       │               │
│  │  │ (40%)   │ │ (25%)   │ │ (20%)   │       │               │
│  │  └─────────┘ └─────────┘ └─────────┘       │               │
│  │  ┌─────────┐                               │               │
│  │  │ Load    │                               │               │
│  │  │Balance  │                               │               │
│  │  │ (15%)   │                               │               │
│  │  └─────────┘                               │               │
│  └─────────────────────────────────────────────┘               │
│                      │                                          │
│                      ▼                                          │
│  ┌────────────────────┐                                         │
│  │   Score & Rank     │                                         │
│  │   Agents           │                                         │
│  └────────────────────┘                                         │
│                      │                                          │
│         ┌────────────┴────────────┐                            │
│         ▼                         ▼                            │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │ Best Agent   │         │ Threshold    │                     │
│  │ Selected     │         │ Not Met      │                     │
│  │ ✅           │         │ ⚠️ Manual    │                     │
│  └──────────────┘         └──────────────┘                     │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │ Register in │                                                │
│  │ session.yaml │                                               │
│  └──────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Формула скоринга

```
Score = Σ(
  skills_match × 0.40 +
  specialization_match × 0.25 +
  performance_score × 0.20 +
  load_balance × 0.15
)
```

### Компоненты

| Компонент | Вес | Описание |
|-----------|-----|----------|
| **Skills Match** | 40% | Совпадение навыков агента с требованиями задачи |
| **Specialization** | 25% | Принадлежность к специализации задачи |
| **Performance** | 20% | Исторический success_rate агента |
| **Load Balance** | 15% | Текущая загрузка агента |

## Типы задач и навыки

### Программирование

| Тип задачи | Навыки | Приоритет агентов |
|------------|--------|-------------------|
| Python | python, numpy, pandas | GLM-5 → Claude → GPT-5 |
| TypeScript | typescript, react, nextjs | GLM-5 → GPT-5 → Gemini |
| Go | go, grpc, microservices | Claude → GLM-5 → Gemini |
| Rust | rust, tokio, systems | Claude → GLM-5 → DeepSeek |
| Frontend | css, react, ui | GPT-5 → Gemini → GLM-5 |
| Backend | python, go, sql | GLM-5 → Claude → Gemini |

### Визуальные задачи (Vision)

| Тип задачи | Навыки | Приоритет агентов |
|------------|--------|-------------------|
| UI Recognition | ui-recognition, screenshot | Gemini → GLM-5 → GPT-5 |
| Chart Recognition | chart-recognition, finance | Gemini → GLM-5 → GPT-5 |
| Candlestick Analysis | candlestick-patterns, trading | **GLM-5** → Gemini → Claude |
| Chart Patterns | chart-patterns, technical | **GLM-5** → Gemini → Claude |

### Финансовые задачи

| Тип задачи | Навыки | Приоритет агентов |
|------------|--------|-------------------|
| Cycle Analysis | cycle-analysis, fft, fte | **GLM-5** → Claude → DeepSeek |
| Technical Analysis | technical-analysis, rsi, macd | **GLM-5** → Claude → Gemini |
| Quant | math, statistics, algorithms | Claude → GLM-5 → DeepSeek |

## Конфигурация

```yaml
config:
  strategy: "best_fit"  # best_fit, round_robin, least_loaded, performance
  min_score_threshold: 0.5
  max_tasks_per_agent: 3
  assignment_timeout_minutes: 30
  
  scoring_weights:
    skills_match: 0.40
    specialization_match: 0.25
    performance_score: 0.20
    load_balance: 0.15
  
  reassign_on_timeout: true
  reassign_on_decline: true
  reassign_on_failure: true
```

## Алгоритм выбора

```python
def select_agent(task: Task, agents: List[Agent]) -> Agent:
    candidates = []
    
    for agent in agents:
        if not agent.available:
            continue
        
        # Check if agent has required skills
        required_skills = task.required_skills
        agent_skills = {s.name: s.level for s in agent.skills}
        
        skills_match = calculate_skills_match(required_skills, agent_skills)
        
        if skills_match < config.min_score_threshold:
            continue
        
        # Calculate total score
        score = (
            skills_match * 0.40 +
            specialization_match(task, agent) * 0.25 +
            agent.performance.success_rate * 0.20 +
            load_balance_score(agent) * 0.15
        )
        
        candidates.append((agent, score))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    return candidates[0][0] if candidates else None
```

## CLI Usage

```bash
# Автоматическое назначение
python scripts/auto_assign.py assign <task_id>

# Показать лучших кандидатов
python scripts/auto_assign.py candidates <task_id>

# Статистика назначений
python scripts/auto_assign.py stats

# История назначений
python scripts/auto_assign.py history [--agent <agent_name>]
```

## Интеграция

### С Handshake

```yaml
# При назначении агента
session:
  id: "SESSION-001"
  agent: "GLM-5 (Zhipu AI)"
  task_id: "TASK-001"
  assigned_by: "auto_assignment"
  assignment_score: 0.92
```

### С Quality Gate

```yaml
# После завершения задачи
quality_gate:
  task_id: "TASK-001"
  agent: "GLM-5 (Zhipu AI)"
  
  # Обновление success_rate агента
  update_performance: true
```

### С Code Review Bot

```yaml
# Автоматический запуск проверки
code_review:
  trigger: "task_completion"
  reviewer: "Qwen 3.5 (Alibaba Cloud)"  # Лучший для code-review
```

## Мониторинг

| Метрика | Описание |
|---------|----------|
| `assignments_total` | Всего назначений |
| `assignments_successful` | Успешных назначений |
| `assignments_failed` | Неудачных назначений |
| `avg_assignment_time` | Среднее время назначения |
| `agent_utilization` | Загрузка агентов |
| `skill_match_avg` | Средний match навыков |

# Agent Instructions - Протокол работы ИИ-агентов

## Обязательный протокол

**ВАЖНО**: Все ИИ-агенты ДОЛЖНЫ следовать этому протоколу при работе над проектом.

---

## 📋 Перед началом работы

### 1. Прочитать навигационные файлы

```
1. Прочитать AI.md (или CLAUDE.md для Claude)
2. Прочитать AGENT_INSTRUCTIONS.md (этот файл)
3. Прочитать progress.yaml - понять текущее состояние проекта
```

### 2. Зарегистрировать сессию

```bash
python scripts/session_manager.py register <task_id> "Agent Name" model
```

### 3. Создать checkpoint (для важных задач)

```bash
python scripts/rollback_manager.py create --type pre-task --task-id <task_id>
```

---

## 🔄 Во время работы

### Правила поведения

1. **Следовать Definition of Done** из tasks.yaml
2. **Обновлять progress.yaml** при завершении этапов
3. **Отправлять heartbeat** каждые 30 минут
   ```bash
   python scripts/session_manager.py heartbeat <session_id>
   ```

### Навыки и самооценка

Перед началом задачи проверьте свои навыки в `agent_skills.yaml`:

```yaml
# Если задача требует навыков, которых у вас нет:
- Сообщите пользователю
- Рекомендуйте другого агента
- Или запросите помощь
```

---

## 🎯 Типы задач и требования

### Backend Tasks

**Необходимые навыки:**
- python: 8+ или go: 8+ или typescript: 8+
- sql: 7+
- architecture: 7+

**Чеклист:**
- [ ] Код компилируется
- [ ] API endpoints работают
- [ ] База данных подключена
- [ ] Ошибки обработаны

### Frontend Tasks

**Необходимые навыки:**
- typescript: 8+
- css: 7+
- react: 8+ (если React)

**Чеклист:**
- [ ] UI отображается корректно
- [ ] Адаптивность работает
- [ ] Нет console errors
- [ ] Accessibility соблюдена

### Data/Analysis Tasks

**Необходимые навыки:**
- python: 8+
- math: 7+
- data-analysis: 7+

**Чеклист:**
- [ ] Данные валидны
- [ ] Вычисления корректны
- [ ] Визуализации точны
- [ ] Нет NaN/null в критичных местах

### Vision Tasks (Свечные/Графические паттерны)

**Необходимые навыки:**
- candlestick-patterns: 7+ или chart-patterns: 7+
- chart-recognition: 7+
- technical-analysis: 7+

**Чеклист:**
- [ ] Паттерны распознаны корректно
- [ ] Направление сигнала верно
- [ ] Confidence scores разумные
- [ ] Нет false positives

---

## 🕯️ Candlestick Pattern Recognition

### Односвечные паттерны

| Паттерн | Сигнал | Описание |
|---------|--------|----------|
| **Doji** | Разворот | Тело маленькое, O≈C |
| **Hammer** | Бычий | Тело сверху, длинная нижняя тень |
| **Shooting Star** | Медвежий | Тело снизу, длинная верхняя тень |
| **Marubozu** | Продолжение | Нет теней |

### Двухсвечные паттерны

| Паттерн | Сигнал | Описание |
|---------|--------|----------|
| **Bullish Engulfing** | Бычий | Бычья поглощает медвежью |
| **Bearish Engulfing** | Медвежий | Медвежья поглощает бычью |
| **Tweezer Top/Bottom** | Разворот | Две свечи с равными пиками/доньями |
| **Harami** | Разворот | Маленькая внутри большой |

### Трёхсвечные паттерны

| Паттерн | Сигнал | Описание |
|---------|--------|----------|
| **Morning Star** | Бычий | Медвежья → маленькая → бычья |
| **Evening Star** | Медвежий | Бычья → маленькая → медвежья |
| **Three White Soldiers** | Бычий | Три растущие бычьи |
| **Three Black Crows** | Медвежий | Три падающие медвежьи |

---

## 📊 Chart Pattern Recognition

### Разворотные паттерны

| Паттерн | Сигнал | Компоненты |
|---------|--------|------------|
| **Head & Shoulders** | Медвежий | Левое плечо, Голова, Правое плечо, Neckline |
| **Inverse H&S** | Бычий | Перевёрнутая форма |
| **Double Top** | Медвежий | Два пика на уровне |
| **Double Bottom** | Бычий | Два дна на уровне |

### Паттерны продолжения

| Паттерн | Сигнал | Описание |
|---------|--------|----------|
| **Flag** | Продолжение | Канал против тренда |
| **Pennant** | Продолжение | Сходящийся треугольник |
| **Triangle** | Пробой | Ascending/Descending/Symmetrical |
| **Cup & Handle** | Бычий | Чашка с ручкой |

---

## ✅ После завершения работы

### 1. Запустить Code Review Bot

```bash
python scripts/code_review_bot.py review <task_id>
```

### 2. Пройти Quality Gate

```bash
python scripts/quality_gate.py validate <task_id>
```

### 3. Обновить файлы

```yaml
# progress.yaml
- Обновить current_phase если нужно
- Увеличить tasks_completed
- Обновить metrics

# tasks.yaml
- Изменить статус задачи на "completed"
- Добавить completed_at timestamp
```

### 4. Завершить сессию

```bash
python scripts/session_manager.py complete <session_id> success "Task completed successfully"
```

### 5. Обновить worklog.md

```markdown
---
Task ID: <task_id>
Agent: <Agent Name>
Task: <Task Description>

Work Log:
- <Action 1>
- <Action 2>
- ...

Stage Summary:
- <Key results>
- <Important decisions>
- <Produced artifacts>
```

---

## 📁 Файловая структура

```
project/
├── AI.md                    # Начать здесь
├── AGENT_INSTRUCTIONS.md    # Этот файл
├── agent_skills.yaml        # Навыки агентов
├── tasks.yaml               # Очередь задач
├── progress.yaml            # Прогресс проекта
├── session.yaml             # Активные сессии
├── quality_gate.yaml        # Конфигурация QG
├── review_bot.yaml          # Конфигурация CRB
├── rollback_points.yaml     # Чекпоинты
├── worklog.md               # Журнал работ
│
├── scripts/
│   ├── session_manager.py
│   ├── auto_assign.py
│   ├── quality_gate.py
│   ├── code_review_bot.py
│   └── rollback_manager.py
│
├── snapshots/               # Чекпоинты
│
└── docs/                    # Документация
    ├── TZ.md
    ├── PLAN.md
    └── ...
```

---

## 🚫 Запрещённые действия

1. **Не** пропускать регистрацию сессии
2. **Не** работать без checkpoint на важных задачах
3. **Не** коммитить без прохождения Quality Gate
4. **Не** игнорировать ошибки Code Review Bot
5. **Не** забывать обновлять worklog.md

---

## 🔗 Связанные файлы

| Файл | Назначение |
|------|------------|
| `AUTO_ASSIGNMENT.md` | Документация Auto-Assignment |
| `QUALITY_GATE.md` | Документация Quality Gate |
| `CODE_REVIEW_BOT.md` | Документация Code Review Bot |
| `ROLLBACK_POINTS.md` | Документация Rollback Points |
| `HANDSHAKE.md` | Документация Agent Handshake |

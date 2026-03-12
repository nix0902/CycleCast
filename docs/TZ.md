# ТЕХНИЧЕСКОЕ ЗАДАНИЕ (ТЗ)
## Система циклического анализа и прогнозирования финансовых рынков
### CycleCast - Методология Ларри Вильямса

---

## 1. ОБЩИЕ СВЕДЕНИЯ

### 1.1 Наименование системы
**CycleCast** - Система циклического анализа и прогнозирования финансовых рынков

### 1.2 Назначение системы
CycleCast предназначена для:
- Моделирования поведения финансовых рынков на основе методологии Ларри Вильямса
- Поиска временных точек разворота рынка через циклический анализ
- Генерации торговых сигналов с подтверждением от "умных денег" (COT)
- Валидации прогнозов через исторические аналогии

### 1.3 Область применения
- Финансовые рынки (акции, фьючерсы, форекс, криптовалюты)
- Инвестиционные компании
- Частные трейдеры
- Финансовые аналитики

### 1.4 Методология Ларри Вильямса

Система реализует пошаговый алгоритм Ларри Вильямса:

```
Шаг 1: Сезонность (Annual Cycle) → "ЧТО торговать?"
Шаг 2: Циклы (Composite Line) → "КОГДА входить?"
Шаг 3: Исторические аналогии (Phenomenological) → Проверка
Шаг 4: COT (Commercials) → Подтверждение "Умными деньгами"
Шаг 5: Qualified Trend Break → Точка входа
```

---

## 2. ТРЕБОВАНИЯ К ФУНКЦИОНАЛЬНОСТИ

### 2.1 Модуль данных рынка (Market Data Module)

#### 2.1.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| MD-001 | Импорт исторических данных в форматах CSV, JSON, XML | Высокий |
| MD-002 | Подключение к внешним API (Yahoo Finance, Alpha Vantage, CFTC) | Высокий |
| MD-003 | Хранение OHLCV данных (Open, High, Low, Close, Volume) | Высокий |
| MD-004 | Поддержка различных таймфреймов (1min, 5min, 1h, 1d, 1w, 1M) | Высокий |
| MD-005 | Автоматическое обновление данных по расписанию | Средний |
| MD-006 | Нормализация данных (adjustment for splits, dividends) | Средний |
| MD-007 | Валидация и очистка данных (пропуски, выбросы) | Высокий |
| MD-008 | Кэширование данных в Redis для быстрого доступа | Высокий |
| MD-009 | Хранение истории минимум 30-50 лет для Seasonality | Высокий |

#### 2.1.2 Структура данных

```go
type MarketData struct {
    ID           string    `json:"id"`
    Symbol       string    `json:"symbol"`
    Timestamp    time.Time `json:"timestamp"`
    Open         float64   `json:"open"`
    High         float64   `json:"high"`
    Low          float64   `json:"low"`
    Close        float64   `json:"close"`
    Volume       int64     `json:"volume"`
    AdjustedClose float64  `json:"adjusted_close,omitempty"`
    Timeframe    string    `json:"timeframe"`
    
    // Вычисляемые поля для методологии LW
    NormalizedClose float64 `json:"normalized_close,omitempty"` // 0-1
    YearDigit       int     `json:"year_digit,omitempty"`       // 0-9 для Decennial
    DetrendedClose  float64 `json:"detrended_close,omitempty"`  // Без тренда
}
```

#### 2.1.3 API Endpoints

```
POST   /api/v1/market/import        - Импорт данных
GET    /api/v1/market/symbols       - Список инструментов
GET    /api/v1/market/symbols/{id}  - Данные по инструменту
GET    /api/v1/market/history       - Исторические данные
DELETE /api/v1/market/symbols/{id}  - Удаление данных
```

---

### 2.2 Модуль Annual Cycle (Сезонность)

#### 2.2.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| AC-001 | Загрузка исторических данных за 30-50 лет | Высокий |
| AC-002 | Детрендинг данных (удаление глобального тренда) | Высокий |
| AC-003 | Расчёт среднего значения для каждого дня года | Высокий |
| AC-004 | Нормализация годовых данных к масштабу 0-1 | Высокий |
| AC-005 | Расчёт confidence интервалов | Средний |
| AC-006 | Визуализация сезонной кривой | Средний |

#### 2.2.2 Алгоритм Annual Cycle

```go
// Псевдокод алгоритма
func CalculateAnnualCycle(prices []MarketData, years int) AnnualCycleResult {
    // 1. Фильтрация по минимальному количеству лет
    if len(uniqueYears(prices)) < years {
        return Error("Недостаточно данных")
    }
    
    // 2. Детрендинг для каждого года
    for year, yearData := range groupByYear(prices) {
        trend := CalculateTrend(yearData) // MA или линейная регрессия
        detrended[year] = yearData.Close - trend
    }
    
    // 3. Нормализация каждого года к 0-1
    for year, data := range detrended {
        min, max := MinMax(data)
        normalized[year] = (data - min) / (max - min)
    }
    
    // 4. Расчёт среднего по дням года
    for day := 1; day <= 366; day++ {
        var values []float64
        for year, data := range normalized {
            if day <= len(data) {
                values = append(values, data[day-1])
            }
        }
        avgCycle[day] = Average(values)
        confidence[day] = StdDev(values) / Average(values)
    }
    
    return AnnualCycleResult{
        Cycle:     avgCycle,
        Confidence: confidence,
        YearsUsed: len(uniqueYears(prices)),
    }
}
```

**Формулы:**

```
Детрендинг:
Detrended(t) = Price(t) - Trend_MA(t)

Нормализация:
NormalizedPrice = (Price - Min_year) / (Max_year - Min_year)

Annual Cycle:
AC(day) = Σ(year=1 to N) [NormalizedPrice(year, day)] / N
```

---

### 2.3 Модуль Forward Testing Efficiency (FTE)

#### 2.3.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| FTE-001 | Валидация сезонных моделей на out-of-sample данных | Высокий |
| FTE-002 | Расчёт корреляции прогноз/факт | Высокий |
| FTE-003 | Детекция "сломанных" сезонностей | Высокий |
| FTE-004 | Walk-Forward тестирование | Высокий |

#### 2.3.2 Алгоритм FTE

```go
// FTE валидация сезонной модели
func ValidateFTE(prices []MarketData, model AnnualCycle) FTEResult {
    // Разделение на in-sample и out-of-sample
    splitPoint := len(prices) * 0.7 // 70% in-sample
    inSample := prices[:splitPoint]
    outSample := prices[splitPoint:]
    
    // Обучение модели на in-sample
    trainedModel := TrainAnnualCycle(inSample)
    
    // Прогноз на out-sample период
    prediction := Project(trainedModel, len(outSample))
    
    // Расчёт корреляции
    correlation := PearsonCorrelation(prediction, outSample.Close)
    
    return FTEResult{
        Correlation: correlation,
        IsValid:     correlation > 0,
        Status:      getStatus(correlation),
    }
}

func getStatus(corr float64) string {
    if corr > 0.3 {
        return "STRONG"
    } else if corr > 0 {
        return "VALID"
    } else {
        return "BROKEN" // Игнорировать эту сезонность
    }
}
```

**Формула FTE:**
```
FTE = Correlation_Pearson(Projection_line, Actual_price)

r = Σ(xᵢ - x̄)(yᵢ - ȳ) / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]
```

---

### 2.4 Модуль QSpectrum и Composite Line

#### 2.4.1 QSpectrum (Циклическая корреляция + МЭМ)

> **Важно:** QSpectrum **НЕ использует FFT (преобразование Фурье)**!
> 
> Обычный спектральный анализ (FFT) часто даёт запаздывание и плохо работает с нестационарными финансовыми данными. QSpectrum разработан специально для рынков.

**Методы QSpectrum:**

1. **Циклическая корреляция (автокорреляция с лагом)** — основной метод
2. **МЭМ — Метод максимальной энтропии (Burg's method)** — для оценки спектральной плотности
3. **Walk-Forward Analysis** — для оценки устойчивости циклов во времени

| ID | Требование | Приоритет |
|----|------------|-----------|
| QS-001 | Реализация циклической корреляции для нестационарных данных | Высокий |
| QS-002 | Вычисление энергии цикла | Высокий |
| QS-003 | МЭМ (Burg's method) для спектральной плотности | Средний |
| QS-004 | Выбор 3 доминантных циклов (short/medium/long) | Высокий |
| QS-005 | Walk-Forward Analysis для валидации циклов | Высокий |

**Алгоритм QSpectrum:**

```go
func QSpectrumAnalyze(prices []float64, config QSpectrumConfig) QSpectrumResult {
    // 1. Нормализация данных
    normalized := NormalizePrices(prices)
    
    // 2. Циклическая корреляция для каждого периода (НЕ FFT!)
    for period := config.MinPeriod; period <= config.MaxPeriod; period++ {
        // Автокорреляция с лагом = period
        correlation := CyclicCorrelation(normalized, period)
        
        // Энергия цикла
        energy := CalculateEnergy(correlation, period, len(prices))
        
        // 3. Walk-Forward тестирование
        wfaResult := WalkForwardTest(normalized, period, config.WFAConfig)
        
        if wfaResult.IsSignificant {
            cycles = append(cycles, Cycle{
                Period:     period,
                Energy:     energy,
                Stability:  wfaResult.Stability,
                Correlation: correlation,
            })
        }
    }
    
    // 4. Сортировка по энергии
    SortByEnergy(cycles)
    
    // 5. Выбор топ-3 циклов (short, medium, long)
    top3 := SelectTopCycles(cycles, config.TopCycles)
    
    return QSpectrumResult{Cycles: top3}
}
```

**Формулы QSpectrum:**
```
1. Циклическая корреляция (основной метод):
   CyclicCorrelation(period) = Σ(t=period to N) [P(t) × P(t-period)] / (N - period)

2. Энергия цикла:
   Energy(period) = |CyclicCorrelation| × √(N/period) × WFA_Stability

3. МЭМ — спектральная плотность мощности (Burg's method, опционально):
   P(f) = σ² / |1 + Σ(k=1 to p) aₖ × e^(-i2πfk)|²
   
   Где:
   - σ² — дисперсия ошибки предсказания
   - aₖ — коэффициенты авторегрессии
   - p — порядок модели

4. Walk-Forward Stability:
   WFA_Stability = Count(Correlation > 0) / Total_Periods
```

**Отличие QSpectrum от FFT:**

| FFT | QSpectrum |
|-----|-----------|
| Разлагает сигнал на частоты | Ищет устойчивые циклы |
| Работает со стационарными данными | Адаптирован для нестационарных (цена) |
| Даёт запаздывание | Минимизирует запаздывание |
| Не учитывает "исчезающие циклы" | Оценивает устойчивость через WFA |
| Одна частота = один результат | Энергия = устойчивость × корреляция |

#### 2.4.2 Composite Line

| ID | Требование | Приоритет |
|----|------------|-----------|
| CL-001 | Наложение 3 волн разной длины | Высокий |
| CL-002 | Детекция точек резонанса | Высокий |
| CL-003 | Генерация сигналов BUY/SELL | Высокий |
| CL-004 | Прогноз на N дней вперёд | Высокий |

**Логика Composite Line:**

```go
type CompositeLine struct {
    ShortCycle  Cycle  // Короткий цикл (10-20 дней)
    MediumCycle Cycle  // Средний цикл (28-40 дней)
    LongCycle   Cycle  // Длинный цикл (56-80 дней)
}

func (cl *CompositeLine) Generate(forecastLength int) CompositeResult {
    result := make([]float64, forecastLength)
    shortVals := make([]float64, forecastLength)
    mediumVals := make([]float64, forecastLength)
    longVals := make([]float64, forecastLength)
    
    for i := 0; i < forecastLength; i++ {
        // Проекция каждого цикла
        shortVals[i] = cl.ShortCycle.Amplitude * 
            math.Sin(2*math.Pi*float64(i)/float64(cl.ShortCycle.Period) + cl.ShortCycle.Phase)
        mediumVals[i] = cl.MediumCycle.Amplitude * 
            math.Sin(2*math.Pi*float64(i)/float64(cl.MediumCycle.Period) + cl.MediumCycle.Phase)
        longVals[i] = cl.LongCycle.Amplitude * 
            math.Sin(2*math.Pi*float64(i)/float64(cl.LongCycle.Period) + cl.LongCycle.Phase)
        
        // Суммирование
        result[i] = shortVals[i] + mediumVals[i] + longVals[i]
    }
    
    // Детекция сигналов (резонанс)
    signals := cl.detectSignals(shortVals, mediumVals, longVals)
    
    return CompositeResult{
        Line:        result,
        ShortCycle:  shortVals,
        MediumCycle: mediumVals,
        LongCycle:   longVals,
        Signals:     signals,
    }
}

func (cl *CompositeLine) detectSignals(short, medium, long []float64) []Signal {
    var signals []Signal
    
    for i := 0; i < len(short); i++ {
        // Резонанс вверх - все три цикла направлены вверх
        if short[i] > 0 && medium[i] > 0 && long[i] > 0 {
            signals = append(signals, Signal{
                Type:     "BUY",
                Strength: CalculateStrength(short[i], medium[i], long[i]),
                Index:    i,
                Reason:   "Triple resonance UP",
            })
        }
        
        // Резонанс вниз - все три цикла направлены вниз
        if short[i] < 0 && medium[i] < 0 && long[i] < 0 {
            signals = append(signals, Signal{
                Type:     "SELL",
                Strength: CalculateStrength(math.Abs(short[i]), math.Abs(medium[i]), math.Abs(long[i])),
                Index:    i,
                Reason:   "Triple resonance DOWN",
            })
        }
    }
    
    return signals
}
```

**Формула Composite Line:**
```
CL(t) = A₁sin(2πf₁t + φ₁) + A₂sin(2πf₂t + φ₂) + A₃sin(2πf₃t + φ₃)

Где:
- A = амплитуда цикла
- f = частота (1/период)
- φ = фаза
```

---

### 2.5 Модуль Decennial Patterns

#### 2.5.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| DP-001 | Группировка данных по последней цифре года (0-9) | Высокий |
| DP-002 | Нормализация данных к масштабу 0-1 | Высокий |
| DP-003 | Расчёт усреднённого поведения для каждой цифры | Высокий |
| DP-004 | Корреляция текущего года с историческими | Высокий |
| DP-005 | Визуализация паттернов по десятилетиям | Средний |

#### 2.5.2 Алгоритм Decennial Patterns

```go
func CalculateDecennialPattern(prices []MarketData, yearDigit int) DecennialPattern {
    // 1. Фильтрация по последней цифре года
    filtered := FilterByYearDigit(prices, yearDigit)
    
    // 2. Группировка по дням года (1-365)
    grouped := GroupByDayOfYear(filtered)
    
    // 3. Нормализация каждого года
    for year, data := range grouped {
        min, max := MinMax(data.Close)
        grouped[year] = Normalize(data.Close, min, max) // 0-1
    }
    
    // 4. Расчёт среднего по дням
    pattern := CalculateAverageByDay(grouped)
    
    // 5. Расчёт confidence
    confidence := CalculateConfidence(grouped)
    
    return DecennialPattern{
        YearDigit:  yearDigit,
        Pattern:    pattern,
        Confidence: confidence,
        YearsUsed:  len(grouped),
    }
}

func FilterByYearDigit(prices []MarketData, digit int) []MarketData {
    var result []MarketData
    for _, p := range prices {
        if p.Timestamp.Year() % 10 == digit {
            result = append(result, p)
        }
    }
    return result
}
```

**Формула нормализации:**
```
NormalizedPrice = (Price - Min) / (Max - Min)
```

---

### 2.6 Модуль Phenomenological Model (Исторические аналогии)

#### 2.6.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| PM-001 | Поиск похожих паттернов в истории (DTW) | Высокий |
| PM-002 | Фильтрация по Decennial циклу (тот же yearDigit) | Высокий |
| PM-003 | Training Interval - настройка окна обучения | Высокий |
| PM-004 | Best Matches - ранжирование по схожести | Высокий |
| PM-005 | Проекция продолжения паттерна | Высокий |

#### 2.6.2 Алгоритм Phenomenological

```go
func PhenomenologicalSearch(prices []MarketData, config PhenomConfig) PhenomResult {
    // 1. Training Interval - взять последние N баров как образец
    target := prices[len(prices)-config.TrainingInterval:]
    targetNormalized := Normalize(target.Close)
    
    // 2. Определить yearDigit текущего года
    currentYearDigit := time.Now().Year() % 10
    
    var matches []PatternMatch
    
    // 3. Сканировать историю
    for i := 0; i < len(prices)-config.TrainingInterval; i++ {
        window := prices[i : i+config.TrainingInterval]
        windowYearDigit := window[len(window)-1].Timestamp.Year() % 10
        
        // 4. Фильтр по Decennial (тот же yearDigit)
        if config.UseDecennialFilter && windowYearDigit != currentYearDigit {
            continue
        }
        
        // 5. DTW расстояние
        windowNormalized := Normalize(window.Close)
        distance := DTWDistance(targetNormalized, windowNormalized)
        
        // 6. Корреляция Пирсона
        correlation := PearsonCorrelation(targetNormalized, windowNormalized)
        
        matches = append(matches, PatternMatch{
            StartIndex:    i,
            EndIndex:      i + config.TrainingInterval,
            DTWDistance:   distance,
            Correlation:   correlation,
            YearDigit:     windowYearDigit,
            Year:          window[len(window)-1].Timestamp.Year(),
        })
    }
    
    // 7. Сортировка по корреляции (убывание)
    SortByCorrelation(matches)
    
    // 8. Best Matches - топ N
    bestMatches := matches[:min(config.TopMatches, len(matches))]
    
    // 9. Проекция продолжения
    projection := CalculateProjection(bestMatches, prices)
    
    return PhenomResult{
        Target:         target,
        BestMatches:    bestMatches,
        Projection:     projection,
        AvgCorrelation: AverageCorrelation(bestMatches),
    }
}
```

**DTW (Dynamic Time Warping):**
```go
func DTWDistance(pattern1, pattern2 []float64) float64 {
    n, m := len(pattern1), len(pattern2)
    
    dtw := make([][]float64, n+1)
    for i := range dtw {
        dtw[i] = make([]float64, m+1)
        for j := range dtw[i] {
            dtw[i][j] = math.Inf(1)
        }
    }
    dtw[0][0] = 0
    
    for i := 1; i <= n; i++ {
        for j := 1; j <= m; j++ {
            cost := math.Abs(pattern1[i-1] - pattern2[j-1])
            dtw[i][j] = cost + math.Min(
                dtw[i-1][j],
                math.Min(
                    dtw[i][j-1],
                    dtw[i-1][j-1],
                ),
            )
        }
    }
    
    return dtw[n][m]
}
```

---

### 2.7 Модуль U-Turn (Разворотные точки)

#### 2.7.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| UT-001 | Детекция экстремумов Composite Line | Высокий |
| UT-002 | Анализ "кучности" разворотов | Высокий |
| UT-003 | Генерация временных меток разворота | Высокий |
| UT-004 | Confidence метрика для каждой точки | Средний |

#### 2.7.2 Алгоритм U-Turn

```go
func DetectUTurns(compositeLine []float64, cycles []Cycle) []UTurnPoint {
    var uturns []UTurnPoint
    
    for i := 1; i < len(compositeLine)-1; i++ {
        // Детекция локального максимума
        if compositeLine[i] > compositeLine[i-1] && 
           compositeLine[i] > compositeLine[i+1] {
            uturns = append(uturns, UTurnPoint{
                Index:      i,
                Type:       "TOP",
                Value:      compositeLine[i],
                Confidence: CalculateUTurnConfidence(cycles, i, "TOP"),
            })
        }
        
        // Детекция локального минимума
        if compositeLine[i] < compositeLine[i-1] && 
           compositeLine[i] < compositeLine[i+1] {
            uturns = append(uturns, UTurnPoint{
                Index:      i,
                Type:       "BOTTOM",
                Value:      compositeLine[i],
                Confidence: CalculateUTurnConfidence(cycles, i, "BOTTOM"),
            })
        }
    }
    
    return uturns
}

func CalculateUTurnConfidence(cycles []Cycle, index int, uturnType string) float64 {
    // "Кучность" - сколько циклов указывают на разворот в этой точке
    var aligned int
    
    for _, cycle := range cycles {
        phase := float64(index % cycle.Period)
        halfPeriod := float64(cycle.Period) / 2
        
        if uturnType == "TOP" {
            // Для TOP фаза должна быть около quarter или three-quarters периода
            if math.Abs(phase - halfPeriod/2) < 2 || 
               math.Abs(phase - halfPeriod*1.5) < 2 {
                aligned++
            }
        } else {
            // Для BOTTOM фаза должна быть около 0 или half периода
            if phase < 2 || math.Abs(phase - halfPeriod) < 2 {
                aligned++
            }
        }
    }
    
    return float64(aligned) / float64(len(cycles))
}
```

---

### 2.8 Модуль COT (Commitment of Traders)

#### 2.8.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| COT-001 | Импорт отчётов CFTC COT | Высокий |
| COT-002 | Анализ позиций Commercials (хеджеры) | Высокий |
| COT-003 | Расчёт COT Index (0-100) | Высокий |
| COT-004 | Детекция экстремальных позиций (>80, <20) | Высокий |
| COT-005 | Корреляция с ценой | Высокий |

#### 2.8.2 Структура данных

```go
type COTData struct {
    ID              string    `json:"id"`
    Symbol          string    `json:"symbol"`
    ReportDate      time.Time `json:"report_date"`
    
    // Позиции
    Commercials     COTPosition `json:"commercials"`
    LargeSpecs      COTPosition `json:"large_specs"`
    SmallSpecs      COTPosition `json:"small_specs"`
    
    // Индексы
    CommercialIndex float64   `json:"commercial_index"` // 0-100
    NetPosition     int64     `json:"net_position"`
    
    // Сигналы
    IsExtreme       bool      `json:"is_extreme"`
    SignalType      string    `json:"signal_type,omitempty"`
}

type COTPosition struct {
    Long      int64   `json:"long"`
    Short     int64   `json:"short"`
    Net       int64   `json:"net"`
    Change    int64   `json:"change"`
    Percentile float64 `json:"percentile"` // 0-100
}
```

#### 2.8.3 Алгоритм COT Index

```go
func CalculateCOTIndex(cotData []COTData, period int) []COTData {
    for i := period; i < len(cotData); i++ {
        // История за период
        history := cotData[i-period+1 : i+1]
        
        // Net позиции Commercials
        currentNet := cotData[i].Commercials.Net
        
        // Min и Max за период
        var minNet, maxNet int64
        for j, h := range history {
            if j == 0 {
                minNet, maxNet = h.Commercials.Net, h.Commercials.Net
            } else {
                if h.Commercials.Net < minNet {
                    minNet = h.Commercials.Net
                }
                if h.Commercials.Net > maxNet {
                    maxNet = h.Commercials.Net
                }
            }
        }
        
        // COT Index (0-100)
        rangeNet := maxNet - minNet
        if rangeNet == 0 {
            cotData[i].CommercialIndex = 50
        } else {
            cotData[i].CommercialIndex = float64(currentNet-minNet) / float64(rangeNet) * 100
        }
        
        // Детекция экстремумов
        if cotData[i].CommercialIndex > 80 {
            cotData[i].IsExtreme = true
            cotData[i].SignalType = "BULLISH" // Commercials покупают
        } else if cotData[i].CommercialIndex < 20 {
            cotData[i].IsExtreme = true
            cotData[i].SignalType = "BEARISH" // Commercials продают
        }
    }
    
    return cotData
}
```

**Формула COT Index:**
```
COT_Index = (Current_Net - Min_N) / (Max_N - Min_N) × 100

Где:
- Net = Commercials_Long - Commercials_Short
- N = период (обычно 26 или 52 недели)
```

---

### 2.9 Модуль Qualified Trend Break (QTB)

#### 2.9.1 Функциональные требования

| ID | Требование | Приоритет |
|----|------------|-----------|
| QTB-001 | Детекция пробоев трендовых линий | Высокий |
| QTB-002 | Фильтрация через Composite Line | Высокий |
| QTB-003 | Генерация сигналов Confirm / False | Высокий |

#### 2.9.2 Алгоритм Qualified Trend Break

```go
func QualifiedTrendBreak(prices []MarketData, compositeLine []float64, 
                         trendLine TrendLine) QTBResult {
    // Детекция пробоя трендовой линии
    currentPrice := prices[len(prices)-1].Close
    trendValue := trendLine.Calculate(prices[len(prices)-1].Timestamp)
    
    isBreakout := false
    breakoutDirection := ""
    
    if currentPrice > trendValue && 
       prices[len(prices)-2].Close <= trendLine.Calculate(prices[len(prices)-2].Timestamp) {
        isBreakout = true
        breakoutDirection = "UP"
    } else if currentPrice < trendValue && 
              prices[len(prices)-2].Close >= trendLine.Calculate(prices[len(prices)-2].Timestamp) {
        isBreakout = true
        breakoutDirection = "DOWN"
    }
    
    if !isBreakout {
        return QTBResult{Status: "NO_BREAKOUT"}
    }
    
    // Проверка через Composite Line
    compositeDirection := ""
    if compositeLine[len(compositeLine)-1] > compositeLine[len(compositeLine)-2] {
        compositeDirection = "UP"
    } else {
        compositeDirection = "DOWN"
    }
    
    // Квалификация пробоя
    if breakoutDirection == compositeDirection {
        return QTBResult{
            Status:    "CONFIRM",
            Direction: breakoutDirection,
            Reason:    "Composite Line подтверждает направление",
        }
    } else {
        return QTBResult{
            Status:    "FALSE",
            Direction: breakoutDirection,
            Reason:    "Composite Line направлен в противоположную сторону",
        }
    }
}
```

**Логика QTB:**
```
QTB = Confirm если:
  - Цена пробивает трендовую линию
  - И Composite Line направлен в ту же сторону

QTB = False если:
  - Цена пробивает уровень
  - Но Composite Line направлен в противоположную сторону
```

---

### 2.10 Модуль интеграции (Workflow)

#### 2.10.1 Итоговый алгоритм Ларри Вильямса

```go
func WilliamsWorkflow(config WorkflowConfig) WorkflowResult {
    // Шаг 1: Annual Cycle - определить "ЧТО торговать"
    activeAssets := []Asset{}
    for _, symbol := range config.Symbols {
        annualCycle := CalculateAnnualCycle(symbol, 30) // 30 лет
        fte := ValidateFTE(symbol, annualCycle)
        
        if fte.Correlation > 0 {
            // Найти сезонное окно
            seasonalWindow := FindSeasonalWindow(annualCycle, config.LookAheadDays)
            if seasonalWindow.Strength > 0.6 {
                activeAssets = append(activeAssets, Asset{
                    Symbol:        symbol,
                    Seasonality:   annualCycle,
                    FTE:           fte,
                    SeasonalWindow: seasonalWindow,
                })
            }
        }
    }
    
    if len(activeAssets) == 0 {
        return WorkflowResult{Status: "NO_ASSETS"}
    }
    
    // Шаг 2: Decennial - контекст года
    currentYearDigit := time.Now().Year() % 10
    for i := range activeAssets {
        decPattern := CalculateDecennialPattern(activeAssets[i].Symbol, currentYearDigit)
        activeAssets[i].DecennialPattern = decPattern
    }
    
    // Шаг 3: Composite Line - "КОГДА входить"
    for i := range activeAssets {
        qspectrum := QSpectrumAnalyze(activeAssets[i].Symbol)
        composite := GenerateCompositeLine(qspectrum.Top3Cycles, config.ForecastDays)
        uturns := DetectUTurns(composite.Line, qspectrum.Top3Cycles)
        
        activeAssets[i].CompositeLine = composite
        activeAssets[i].UTurns = uturns
    }
    
    // Шаг 4: Phenomenological - проверка историей
    for i := range activeAssets {
        phenom := PhenomenologicalSearch(activeAssets[i].Symbol, PhenomConfig{
            TrainingInterval:    100,
            UseDecennialFilter:  true,
            TopMatches:          10,
        })
        activeAssets[i].PhenomModel = phenom
    }
    
    // Шаг 5: COT - подтверждение "умными деньгами"
    for i := range activeAssets {
        cot := AnalyzeCOT(activeAssets[i].Symbol)
        activeAssets[i].COT = cot
    }
    
    // Шаг 6: Генерация сигналов
    signals := []Signal{}
    for _, asset := range activeAssets {
        // Проверка условий
        compositeSignals := asset.CompositeLine.Signals
        
        for _, sig := range compositeSignals {
            // Подтверждение от COT
            cotConfirm := false
            if sig.Type == "BUY" && asset.COT.CommercialIndex > 80 {
                cotConfirm = true
            } else if sig.Type == "SELL" && asset.COT.CommercialIndex < 20 {
                cotConfirm = true
            }
            
            // Подтверждение от Phenomenological
            phenomConfirm := false
            if sig.Type == "BUY" && asset.PhenomModel.Projection.Direction == "UP" {
                phenomConfirm = true
            } else if sig.Type == "SELL" && asset.PhenomModel.Projection.Direction == "DOWN" {
                phenomConfirm = true
            }
            
            if cotConfirm && phenomConfirm {
                signals = append(signals, Signal{
                    Symbol:    asset.Symbol,
                    Type:      sig.Type,
                    Strength:  sig.Strength,
                    Timestamp: time.Now().AddDate(0, 0, sig.Index),
                    Reason:    "Composite + COT + Phenom confirmation",
                })
            }
        }
    }
    
    return WorkflowResult{
        ActiveAssets: activeAssets,
        Signals:      signals,
        Status:       "SUCCESS",
    }
}
```

---

## 3. ТРЕБОВАНИЯ К ИНТЕРФЕЙСУ

### 3.1 Web Interface

#### 3.1.1 Главный Dashboard
- Обзор активных активов (по Seasonality + FTE)
- Текущий Decennial контекст
- Последние сигналы
- Статус COT для отслеживаемых инструментов

#### 3.1.2 Графики
- OHLC свечи
- Projection Line (Composite Line) наложенная на график
- Annual Cycle график
- Decennial Patterns визуализация

#### 3.1.3 Analysis Panel
- Выбор метода анализа (Williams Cycle Forecast)
- Параметры алгоритмов
- Результаты и статистика

---

## 4. ТРЕБОВАНИЯ К БЕЗОПАСНОСТИ

### 4.1 Аутентификация и авторизация
| ID | Требование |
|----|------------|
| SEC-001 | JWT токены для API |
| SEC-002 | Ролевая модель (Admin, Analyst, Viewer) |
| SEC-003 | Rate limiting по API ключу |
| SEC-004 | HTTPS обязательно |

### 4.2 Защита данных
| ID | Требование |
|----|------------|
| SEC-005 | Шифрование чувствительных данных |
| SEC-006 | Аудит логов действий |
| SEC-007 | Резервное копирование БД |

---

## 5. ТРЕБОВАНИЯ К ПРОИЗВОДИТЕЛЬНОСТИ

| Метрика | Требование |
|---------|------------|
| API Response Time | < 100ms (p95) |
| Annual Cycle расчёт | < 200ms |
| Composite Line генерация | < 100ms |
| WebSocket latency | < 10ms |
| Concurrent users | 1000+ |
| Data points stored | 100M+ |

---

## 6. ТРЕБОВАНИЯ К НАДЁЖНОСТИ

| Метрика | Требование |
|---------|------------|
| Uptime | 99.9% |
| RTO (Recovery Time Objective) | < 1 hour |
| RPO (Recovery Point Objective) | < 1 hour |
| Error rate | < 0.1% |

---

## 7. ТРЕБОВАНИЯ К СОВМЕСТИМОСТИ

### 7.1 Браузеры
- Chrome 100+
- Firefox 100+
- Safari 15+
- Edge 100+

### 7.2 API
- REST API (OpenAPI 3.0)
- gRPC (Protocol Buffers 3)
- WebSocket (RFC 6455)

---

## 8. ТРЕБОВАНИЯ К ДОКУМЕНТАЦИИ

| Документ | Содержание |
|----------|------------|
| API Documentation | OpenAPI спецификация, примеры |
| Developer Guide | Архитектура, алгоритмы |
| User Manual | Инструкция по использованию |
| Deployment Guide | Установка, конфигурация |

---

## 9. ПРИЁМОЧНЫЕ ИСПЫТАНИЯ

### 9.1 Функциональные тесты
| ID | Тест | Критерий |
|----|------|----------|
| AT-001 | Импорт 1M+ точек данных | Успешно, < 60 сек |
| AT-002 | Annual Cycle расчёт | Корректная сезонная кривая |
| AT-003 | FTE валидация | Детекция сломанных сезонностей |
| AT-004 | Composite Line сигналы | Детекция резонанса |
| AT-005 | Decennial Patterns | Корректная группировка по yearDigit |
| AT-006 | COT анализ | Корректный расчёт COT Index |
| AT-007 | QTB | Правильная квалификация пробоев |

### 9.2 Нагрузочные тесты
| ID | Тест | Критерий |
|----|------|----------|
| LT-001 | 1000 одновременных API запросов | Response < 200ms |
| LT-002 | WebSocket 1000 connections | Latency < 20ms |
| LT-003 | Continuous operation | Uptime > 24h |

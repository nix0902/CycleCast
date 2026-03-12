# ТЕХНИЧЕСКОЕ РЕШЕНИЕ
## Система циклического анализа и прогнозирования финансовых рынков
### CycleCast - Методология Ларри Вильямса

---

## 1. АРХИТЕКТУРА СИСТЕМЫ

### 1.1 Высокоуровневая архитектура

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PRESENTATION LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │   Web SPA       │  │   Desktop App   │  │   CLI Tool      │  │   External APIs     │  │
│  │   (React)       │  │   (Electron)    │  │   (Go CLI)      │  │   (REST/gRPC)       │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │
└───────────┼────────────────────┼────────────────────┼──────────────────────┼─────────────┘
            │                    │                    │                      │
            └────────────────────┴────────────────────┴──────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     GATEWAY LAYER                                        │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              API Gateway (Gin)                                      │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │  │
│  │  │ REST Handler  │  │ gRPC Server   │  │ WebSocket Hub │  │ GraphQL Resolver  │   │  │
│  │  │ :8080         │  │ :9090         │  │ :8080/ws      │  │ :8080/graphql     │   │  │
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────────┘   │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐  │  │
│  │  │ Middleware: Auth (JWT) → Rate Limit → Request ID → Logging → Recovery       │  │  │
│  │  └─────────────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     SERVICE LAYER                                        │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                     Методология Ларри Вильямса                                      │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │  │
│  │  │ MarketDataSvc   │  │ AnnualCycleSvc  │  │ DecennialSvc    │  │ CompositeSvc  │  │  │
│  │  │                 │  │                 │  │                 │  │               │  │  │
│  │  │ - Import        │  │ - Seasonality   │  │ - GroupByDigit  │  │ - QSpectrum   │  │  │
│  │  │ - Validate      │  │ - Detrending    │  │ - Normalize     │  │ - Composite   │  │  │
│  │  │ - Normalize     │  │ - FTE           │  │ - Patterns      │  │ - Resonance   │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │  │
│  │  │ PhenomModelSvc  │  │ UTurnSvc        │  │ COTAnalyzer     │  │ QTBSvc        │  │  │
│  │  │                 │  │                 │  │                 │  │               │  │  │
│  │  │ - DTW           │  │ - Detect        │  │ - Parse CFTC    │  │ - TrendBreak  │  │  │
│  │  │ - Similarity    │  │ - Confidence    │  │ - Commercials   │  │ - Qualify     │  │  │
│  │  │ - Projection    │  │ - Signals       │  │ - Index         │  │ - Confirm     │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   REPOSITORY LAYER                                       │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │  │
│  │  │ MarketDataRepo  │  │ CycleRepo       │  │ ProjectionRepo  │  │ COTRepo       │  │  │
│  │  │ (PostgreSQL)    │  │ (PostgreSQL)    │  │ (PostgreSQL)    │  │ (PostgreSQL)  │  │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                     │  │
│  │  │ TimeSeriesRepo  │  │ PatternRepo     │  │ CacheRepo       │                     │  │
│  │  │ (TimescaleDB)   │  │ (PostgreSQL)    │  │ (Redis)         │                     │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                     │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA LAYER                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ PostgreSQL 16   │  │ TimescaleDB     │  │ Redis 7         │  │ MinIO/S3            │  │
│  │ (Primary DB)    │  │ (Time Series)   │  │ (Cache/Queue)   │  │ (File Storage)      │  │
│  │ :5432           │  │ Extension       │  │ :6379           │  │ :9000               │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ДЕТАЛЬНОЕ ОПИСАНИЕ МОДУЛЕЙ

### 2.1 Модуль Annual Cycle (Сезонность)

#### 2.1.1 Архитектура

```go
// internal/service/seasonality/annual_cycle.go

package seasonality

import (
    "math"
    "time"
    "github.com/cyclecast/internal/domain/entity"
)

// AnnualCycleAnalyzer - анализатор сезонности
type AnnualCycleAnalyzer struct {
    config AnnualCycleConfig
}

type AnnualCycleConfig struct {
    MinYears       int     `json:"min_years"`        // Минимум лет (30)
    DetrendingMA   int     `json:"detrending_ma"`    // MA для детрендинга (200)
    ConfidenceThr  float64 `json:"confidence_thr"`   // Порог confidence (0.5)
}

type AnnualCycleResult struct {
    Cycle      []DailyPoint `json:"cycle"`       // 366 точек
    Confidence []float64    `json:"confidence"`  // Confidence для каждого дня
    YearsUsed  int          `json:"years_used"`
    IsValid    bool         `json:"is_valid"`
}

type DailyPoint struct {
    DayOfYear  int     `json:"day_of_year"`  // 1-366
    AvgValue   float64 `json:"avg_value"`    // Среднее значение
    StdDev     float64 `json:"std_dev"`      // Стандартное отклонение
    PosPercent float64 `json:"pos_percent"`  // % положительных дней
}

// Analyze - главный метод анализа сезонности
func (a *AnnualCycleAnalyzer) Analyze(prices []entity.MarketData) (*AnnualCycleResult, error) {
    // 1. Группировка по годам
    byYear := a.groupByYear(prices)
    
    // 2. Проверка минимального количества лет
    if len(byYear) < a.config.MinYears {
        return nil, errors.New("недостаточно данных для сезонного анализа")
    }
    
    // 3. Детрендинг каждого года
    detrended := make(map[int][]float64)
    for year, data := range byYear {
        detrended[year] = a.detrend(data)
    }
    
    // 4. Нормализация каждого года к 0-1
    normalized := make(map[int][]float64)
    for year, data := range detrended {
        normalized[year] = a.normalize(data)
    }
    
    // 5. Расчёт среднего по дням года
    cycle := a.calculateCycle(normalized)
    
    // 6. Расчёт confidence
    confidence := a.calculateConfidence(normalized, cycle)
    
    return &AnnualCycleResult{
        Cycle:      cycle,
        Confidence: confidence,
        YearsUsed:  len(byYear),
        IsValid:    a.validateResult(confidence),
    }, nil
}

// detrend - удаление глобального тренда
func (a *AnnualCycleAnalyzer) detrend(data []entity.MarketData) []float64 {
    // MA для тренда
    ma := calculateMA(data, a.config.DetrendingMA)
    
    // Detrended = Price - Trend
    detrended := make([]float64, len(data))
    for i, p := range data {
        detrended[i] = p.Close - ma[i]
    }
    
    return detrended
}

// normalize - нормализация к масштабу 0-1
func (a *AnnualCycleAnalyzer) normalize(data []float64) []float64 {
    min, max := minMax(data)
    range_ := max - min
    
    if range_ == 0 {
        range_ = 1
    }
    
    normalized := make([]float64, len(data))
    for i, v := range data {
        normalized[i] = (v - min) / range_
    }
    
    return normalized
}

// calculateCycle - расчёт среднего значения для каждого дня года
func (a *AnnualCycleAnalyzer) calculateCycle(normalized map[int][]float64) []DailyPoint {
    cycle := make([]DailyPoint, 366)
    
    for day := 1; day <= 366; day++ {
        var values []float64
        var positives int
        
        for _, yearData := range normalized {
            idx := day - 1
            if idx < len(yearData) {
                values = append(values, yearData[idx])
                if yearData[idx] > 0.5 {
                    positives++
                }
            }
        }
        
        if len(values) > 0 {
            cycle[day-1] = DailyPoint{
                DayOfYear:  day,
                AvgValue:   average(values),
                StdDev:     stdDev(values),
                PosPercent: float64(positives) / float64(len(values)),
            }
        }
    }
    
    return cycle
}

// calculateConfidence - расчёт confidence для каждого дня
func (a *AnnualCycleAnalyzer) calculateConfidence(normalized map[int][]float64, cycle []DailyPoint) []float64 {
    confidence := make([]float64, 366)
    
    for day := 1; day <= 366; day++ {
        var values []float64
        for _, yearData := range normalized {
            idx := day - 1
            if idx < len(yearData) {
                values = append(values, yearData[idx])
            }
        }
        
        if len(values) > 0 {
            // Confidence = 1 - CV (коэффициент вариации)
            mean := average(values)
            std := stdDev(values)
            if mean != 0 {
                cv := std / math.Abs(mean)
                confidence[day-1] = math.Max(0, 1-cv)
            }
        }
    }
    
    return confidence
}

// FindSeasonalWindow - поиск сезонного окна
func (a *AnnualCycleAnalyzer) FindSeasonalWindow(cycle []DailyPoint, currentDay int, lookahead int) SeasonalWindow {
    endDay := currentDay + lookahead
    if endDay > 366 {
        endDay = 366
    }
    
    var bullishDays, bearishDays int
    var bullishStrength, bearishStrength float64
    
    for day := currentDay; day <= endDay; day++ {
        idx := (day - 1) % 366
        if cycle[idx].AvgValue > 0.55 { // Бычий день
            bullishDays++
            bullishStrength += cycle[idx].AvgValue * cycle[idx].PosPercent
        } else if cycle[idx].AvgValue < 0.45 { // Медвежий день
            bearishDays++
            bearishStrength += (1 - cycle[idx].AvgValue) * (1 - cycle[idx].PosPercent)
        }
    }
    
    if bullishStrength > bearishStrength {
        return SeasonalWindow{
            Direction: "BULLISH",
            Strength:  bullishStrength / float64(bullishDays+1),
            Days:      bullishDays,
        }
    } else {
        return SeasonalWindow{
            Direction: "BEARISH",
            Strength:  bearishStrength / float64(bearishDays+1),
            Days:      bearishDays,
        }
    }
}
```

---

### 2.2 Модуль Forward Testing Efficiency (FTE)

```go
// internal/service/seasonality/fte.go

package seasonality

// FTEValidator - валидатор через Forward Testing Efficiency
type FTEValidator struct {
    config FTEConfig
}

type FTEConfig struct {
    InSampleRatio  float64 `json:"in_sample_ratio"`  // 0.7
    MinCorrelation float64 `json:"min_correlation"`  // 0.0
}

type FTEResult struct {
    Correlation  float64 `json:"correlation"`   // Корреляция прогноз/факт
    IsValid      bool    `json:"is_valid"`      // Модель работает
    Status       string  `json:"status"`        // STRONG, VALID, BROKEN
    InSampleSize int     `json:"in_sample_size"`
    OutSampleSize int    `json:"out_sample_size"`
}

// Validate - валидация сезонной модели
func (f *FTEValidator) Validate(prices []entity.MarketData, model AnnualCycleResult) *FTEResult {
    n := len(prices)
    inSampleSize := int(float64(n) * f.config.InSampleRatio)
    outSampleSize := n - inSampleSize
    
    // In-sample данные для обучения
    inSample := prices[:inSampleSize]
    // Out-of-sample данные для тестирования
    outSample := prices[inSampleSize:]
    
    // Прогноз на out-of-sample период по сезонной модели
    prediction := f.project(model, outSample)
    
    // Расчёт корреляции Пирсона
    correlation := pearsonCorrelation(prediction, extractClose(outSample))
    
    // Определение статуса
    status := "BROKEN"
    if correlation > 0.3 {
        status = "STRONG"
    } else if correlation > 0 {
        status = "VALID"
    }
    
    return &FTEResult{
        Correlation:   correlation,
        IsValid:       correlation > f.config.MinCorrelation,
        Status:        status,
        InSampleSize:  inSampleSize,
        OutSampleSize: outSampleSize,
    }
}

// project - генерация прогноза по сезонной модели
func (f *FTEValidator) project(model AnnualCycleResult, outSample []entity.MarketData) []float64 {
    prediction := make([]float64, len(outSample))
    
    for i, p := range outSample {
        dayOfYear := p.Timestamp.YearDay()
        if dayOfYear <= 366 {
            prediction[i] = model.Cycle[dayOfYear-1].AvgValue
        }
    }
    
    return prediction
}
```

---

### 2.3 Модуль QSpectrum (Циклическая корреляция + МЭМ)

> **Важно:** QSpectrum **НЕ использует FFT (преобразование Фурье)**!
> 
> Обычный спектральный анализ (FFT) часто даёт запаздывание и плохо работает с нестационарными финансовыми данными. QSpectrum разработан специально для рынков.

**Методы QSpectrum:**

1. **Циклическая корреляция (автокорреляция с лагом)** — основной метод, адаптированный для нестационарных данных
2. **МЭМ — Метод максимальной энтропии (Burg's method)** — для оценки спектральной плотности мощности
3. **Walk-Forward Analysis** — для оценки устойчивости циклов во времени

**Ключевые формулы:**

```
1. Циклическая корреляция:
   CyclicCorrelation(period) = Σ(t=period to N) [P(t) × P(t-period)] / (N - period)

2. Энергия цикла:
   Energy(period) = |CyclicCorrelation| × √(N/period) × WFA_Stability

3. МЭМ — спектральная плотность мощности (Burg's method):
   P(f) = σ² / |1 + Σ(k=1 to p) aₖ × e^(-i2πfk)|²
```

```go
// internal/service/cycle/qspectrum.go

package cycle

import (
    "math"
    "github.com/cyclecast/internal/domain/entity"
)

// =============================================================================
// QSpectrum - Анализатор циклов для нестационарных финансовых данных
// =============================================================================
// 
// ВАЖНО: QSpectrum НЕ использует FFT (преобразование Фурье)!
// 
// Причины отказа от FFT:
// 1. FFT даёт запаздывание на финансовых данных
// 2. FFT работает только со стационарными данными (цена - нестационарна)
// 3. FFT не учитывает "исчезающие циклы" (циклы, которые появляются и исчезают)
// 
// QSpectrum использует:
// 1. Циклическую корреляцию (автокорреляция с лагом) - основной метод
// 2. МЭМ (Метод максимальной энтропии / Burg's method) - для спектральной плотности
// 3. Walk-Forward Analysis - для оценки устойчивости циклов
// =============================================================================

// QSpectrumAnalyzer - анализатор QSpectrum
type QSpectrumAnalyzer struct {
    config QSpectrumConfig
}

type QSpectrumConfig struct {
    MinPeriod       int        `json:"min_period"`        // Минимальный период (10)
    MaxPeriod       int        `json:"max_period"`        // Максимальный период (200)
    EnergyThreshold float64    `json:"energy_threshold"`  // Порог энергии (0.1)
    TopCycles       int        `json:"top_cycles"`        // Количество циклов (3)
    UseMEM          bool       `json:"use_mem"`           // Использовать МЭМ (опционально)
    MEMOrder        int        `json:"mem_order"`         // Порядок модели МЭМ (50)
    WFAConfig       WFAConfig  `json:"wfa_config"`        // Walk-Forward конфигурация
}

type QSpectrumResult struct {
    Cycles        []Cycle        `json:"cycles"`
    Top3Cycles    []Cycle        `json:"top_3_cycles"`
    Spectrum      []SpectrumPeak `json:"spectrum"`
    MEMSpectrum   []MEMPPoint    `json:"mem_spectrum,omitempty"` // Спектр МЭМ (опционально)
}

type Cycle struct {
    Period       int     `json:"period"`        // Период в днях
    Energy       float64 `json:"energy"`        // Энергия цикла
    Stability    float64 `json:"stability"`     // Устойчивость (WFA)
    Correlation  float64 `json:"correlation"`   // Циклическая корреляция
    Phase        float64 `json:"phase"`         // Фаза в радианах
    Amplitude    float64 `json:"amplitude"`     // Амплитуда
}

type SpectrumPeak struct {
    Period     int     `json:"period"`
    Energy     float64 `json:"energy"`
    Correlation float64 `json:"correlation"`
}

type MEMPoint struct {
    Frequency   float64 `json:"frequency"`   // Частота
    Period      int     `json:"period"`      // Период в днях
    Power       float64 `json:"power"`       // Спектральная плотность мощности
}

// Analyze - главный метод анализа
func (q *QSpectrumAnalyzer) Analyze(prices []float64) (*QSpectrumResult, error) {
    // 1. Нормализация данных
    normalized := q.normalize(prices)
    
    // 2. Циклическая корреляция для каждого периода (НЕ FFT!)
    spectrum := q.calculateSpectrum(normalized)
    
    // 3. Walk-Forward Analysis для каждого пика
    cycles := q.extractCycles(spectrum, normalized)
    
    // 4. Сортировка по энергии
    q.sortByEnergy(cycles)
    
    // 5. Выбор топ-3 циклов (short, medium, long)
    top3 := q.selectTop3Cycles(cycles)
    
    // 6. Опционально: МЭМ спектр
    var memSpectrum []MEMPoint
    if q.config.UseMEM {
        memSpectrum = q.calculateMEMSpectrum(normalized)
    }
    
    return &QSpectrumResult{
        Cycles:      cycles,
        Top3Cycles:  top3,
        Spectrum:    spectrum,
        MEMSpectrum: memSpectrum,
    }, nil
}

// =============================================================================
// МЕТОД 1: ЦИКЛИЧЕСКАЯ КОРРЕЛЯЦИЯ (основной метод)
// =============================================================================

// calculateSpectrum - расчёт спектра циклической корреляции
// Это НЕ FFT! Это автокорреляция с лагом, адаптированная для нестационарных данных.
func (q *QSpectrumAnalyzer) calculateSpectrum(data []float64) []SpectrumPeak {
    n := len(data)
    spectrum := make([]SpectrumPeak, 0)
    
    for period := q.config.MinPeriod; period <= q.config.MaxPeriod && period < n/2; period++ {
        // Циклическая корреляция (автокорреляция с лагом = period)
        correlation := q.cyclicCorrelation(data, period)
        
        // Энергия цикла
        energy := q.calculateEnergy(correlation, period, n)
        
        if energy > q.config.EnergyThreshold {
            spectrum = append(spectrum, SpectrumPeak{
                Period:     period,
                Energy:     energy,
                Correlation: correlation,
            })
        }
    }
    
    return spectrum
}

// cyclicCorrelation - циклическая корреляция (автокорреляция с лагом)
// 
// Формула:
// CyclicCorrelation(period) = Σ(t=period to N) [P(t) × P(t-period)] / (N - period)
//
// Эта формула измеряет, насколько цена коррелирует сама с собой
// при сдвиге на period баров назад.
func (q *QSpectrumAnalyzer) cyclicCorrelation(data []float64, period int) float64 {
    n := len(data)
    if period >= n {
        return 0
    }
    
    var sumCorr float64
    var count int
    
    for i := period; i < n; i++ {
        // Автокорреляция с лагом = period
        sumCorr += data[i] * data[i-period]
        count++
    }
    
    if count == 0 {
        return 0
    }
    
    return sumCorr / float64(count)
}

// calculateEnergy - вычисление энергии цикла
// 
// Формула:
// Energy(period) = |CyclicCorrelation| × √(N/period) × WFA_Stability
//
// Энергия учитывает:
// 1. Силу корреляции (чем выше - тем значимее цикл)
// 2. Количество данных (чем больше - тем надёжнее)
// 3. Устойчивость во времени (через WFA)
func (q *QSpectrumAnalyzer) calculateEnergy(correlation float64, period int, n int) float64 {
    stabilityFactor := math.Sqrt(float64(n) / float64(period))
    return math.Abs(correlation) * stabilityFactor
}

// =============================================================================
// МЕТОД 2: МЭМ (МЕТОД МАКСИМАЛЬНОЙ ЭНТРОПИИ / BURG'S METHOD)
// =============================================================================

// calculateMEMSpectrum - расчёт спектра методом максимальной энтропии
// 
// МЭМ (Burg's method) - авторегрессионный метод для оценки спектральной плотности.
// В отличие от FFT, МЭМ:
// - Лучше работает с короткими данными
// - Даёт более высокое разрешение по частоте
// - Адаптирован для нестационарных сигналов
//
// Формула:
// P(f) = σ² / |1 + Σ(k=1 to p) aₖ × e^(-i2πfk)|²
func (q *QSpectrumAnalyzer) calculateMEMSpectrum(data []float64) []MEMPoint {
    // 1. Расчёт коэффициентов авторегрессии методом Burg
    arCoeffs, sigma2 := q.burgMethod(data, q.config.MEMOrder)
    
    // 2. Расчёт спектра мощности
    n := len(data)
    spectrum := make([]MEMPoint, 0)
    
    // Частоты от 1/MaxPeriod до 1/MinPeriod
    minFreq := 1.0 / float64(q.config.MaxPeriod)
    maxFreq := 1.0 / float64(q.config.MinPeriod)
    freqStep := (maxFreq - minFreq) / float64(n)
    
    for f := minFreq; f <= maxFreq; f += freqStep {
        // Расчёт P(f) = σ² / |1 + Σ aₖ × e^(-i2πfk)|²
        sumReal := 1.0
        sumImag := 0.0
        
        for k, a := range arCoeffs {
            angle := -2 * math.Pi * f * float64(k+1)
            sumReal += a * math.Cos(angle)
            sumImag += a * math.Sin(angle)
        }
        
        magnitude := math.Sqrt(sumReal*sumReal + sumImag*sumImag)
        power := sigma2 / (magnitude * magnitude)
        
        period := int(1.0 / f)
        
        spectrum = append(spectrum, MEMPoint{
            Frequency: f,
            Period:    period,
            Power:     power,
        })
    }
    
    return spectrum
}

// burgMethod - расчёт коэффициентов авторегрессии методом Burg
// 
// Возвращает:
// - arCoeffs: коэффициенты авторегрессии a₁, a₂, ..., aₚ
// - sigma2: дисперсия ошибки предсказания
func (q *QSpectrumAnalyzer) burgMethod(data []float64, order int) ([]float64, float64) {
    n := len(data)
    if n <= order {
        return nil, 0
    }
    
    // Инициализация
    a := make([]float64, order+1)
    a[0] = 1.0
    
    // Прямые и обратные ошибки
    ef := make([]float64, n)
    eb := make([]float64, n)
    copy(ef, data)
    copy(eb, data)
    
    var sigma2 float64
    for i := 0; i < n; i++ {
        sigma2 += data[i] * data[i]
    }
    sigma2 /= float64(n)
    
    // Рекурсия Левинсона-Дурбина с модификацией Burg
    for m := 1; m <= order; m++ {
        // Расчёт коэффициента отражения
        var num, den float64
        for i := m; i < n; i++ {
            num += ef[i] * eb[i-1]
            den += ef[i]*ef[i] + eb[i-1]*eb[i-1]
        }
        
        if den == 0 {
            break
        }
        
        km := 2 * num / den
        
        // Обновление коэффициентов
        for i := 0; i <= m/2; i++ {
            temp := a[i] - km*a[m-i]
            a[m-i] = a[m-i] - km*a[i]
            a[i] = temp
        }
        
        // Обновление ошибок
        for i := n - 1; i >= m; i-- {
            ef[i] = ef[i] - km*eb[i-1]
            eb[i] = eb[i-1] - km*ef[i]
        }
        
        // Обновление дисперсии
        sigma2 *= (1 - km*km)
    }
    
    return a[1:], sigma2
}

// =============================================================================
// WALK-FORWARD ANALYSIS (Валидация устойчивости)
// =============================================================================

// extractCycles - извлечение значимых циклов с WFA валидацией
func (q *QSpectrumAnalyzer) extractCycles(spectrum []SpectrumPeak, data []float64) []Cycle {
    var cycles []Cycle
    
    wfa := NewWFAAnalyzer(q.config.WFAConfig)
    
    for _, peak := range spectrum {
        // Walk-Forward тест - проверка устойчивости цикла
        wfaResult := wfa.Test(data, peak.Period)
        
        if wfaResult.IsSignificant {
            // Расчёт фазы и амплитуды
            phase, amplitude := q.extractPhaseAmplitude(data, peak.Period)
            
            cycles = append(cycles, Cycle{
                Period:      peak.Period,
                Energy:      peak.Energy * wfaResult.Stability,
                Stability:   wfaResult.Stability,
                Correlation: peak.Correlation,
                Phase:       phase,
                Amplitude:   amplitude,
            })
        }
    }
    
    return cycles
}

// selectTop3Cycles - выбор 3 циклов (short, medium, long)
func (q *QSpectrumAnalyzer) selectTop3Cycles(cycles []Cycle) []Cycle {
    if len(cycles) <= 3 {
        return cycles
    }
    
    // Сортировка по периоду
    sortedByPeriod := make([]Cycle, len(cycles))
    copy(sortedByPeriod, cycles)
    sort.Slice(sortedByPeriod, func(i, j int) bool {
        return sortedByPeriod[i].Period < sortedByPeriod[j].Period
    })
    
    // Выбор короткого, среднего и длинного
    n := len(sortedByPeriod)
    shortIdx := 0
    mediumIdx := n / 3
    longIdx := 2 * n / 3
    
    return []Cycle{
        sortedByPeriod[shortIdx],
        sortedByPeriod[mediumIdx],
        sortedByPeriod[longIdx],
    }
}

// extractPhaseAmplitude - извлечение фазы и амплитуды цикла
func (q *QSpectrumAnalyzer) extractPhaseAmplitude(data []float64, period int) (phase, amplitude float64) {
    n := len(data)
    
    // Синус-косинусная декомпозиция
    var sinSum, cosSum float64
    
    for i := 0; i < n; i++ {
        angle := 2 * math.Pi * float64(i) / float64(period)
        sinSum += data[i] * math.Sin(angle)
        cosSum += data[i] * math.Cos(angle)
    }
    
    sinSum *= 2 / float64(n)
    cosSum *= 2 / float64(n)
    
    // Фаза
    phase = math.Atan2(sinSum, cosSum)
    
    // Амплитуда
    amplitude = math.Sqrt(sinSum*sinSum + cosSum*cosSum)
    
    return phase, amplitude
}
```

---

### 2.4 Модуль Composite Line

```go
// internal/service/cycle/composite.go

package cycle

import (
    "math"
    "time"
)

// CompositeLineGenerator - генератор Composite Line
type CompositeLineGenerator struct {
    shortCycle  Cycle
    mediumCycle Cycle
    longCycle   Cycle
}

type CompositeLineResult struct {
    Line        []float64 `json:"line"`         // Суммарная линия
    ShortCycle  []float64 `json:"short_cycle"`  // Проекция короткого цикла
    MediumCycle []float64 `json:"medium_cycle"` // Проекция среднего цикла
    LongCycle   []float64 `json:"long_cycle"`   // Проекция длинного цикла
    Signals     []Signal  `json:"signals"`      // Сигналы BUY/SELL
    UTurns      []UTurn   `json:"uturns"`       // Разворотные точки
}

type Signal struct {
    Type       string    `json:"type"`        // BUY, SELL
    Strength   float64   `json:"strength"`    // 0-1
    Index      int       `json:"index"`       // Индекс в прогнозе
    Timestamp  time.Time `json:"timestamp"`
    Reason     string    `json:"reason"`      // Описание причины
}

type UTurn struct {
    Index      int     `json:"index"`       // Индекс
    Type       string  `json:"type"`        // TOP, BOTTOM
    Value      float64 `json:"value"`       // Значение
    Confidence float64 `json:"confidence"`  // 0-1
}

// NewCompositeLineGenerator - конструктор
func NewCompositeLineGenerator(cycles []Cycle) *CompositeLineGenerator {
    if len(cycles) < 3 {
        return nil
    }
    
    return &CompositeLineGenerator{
        shortCycle:  cycles[0],  // Короткий (10-20 дней)
        mediumCycle: cycles[1],  // Средний (28-40 дней)
        longCycle:   cycles[2],  // Длинный (56-80 дней)
    }
}

// Generate - генерация Composite Line
func (g *CompositeLineGenerator) Generate(forecastLength int) *CompositeLineResult {
    line := make([]float64, forecastLength)
    shortVals := make([]float64, forecastLength)
    mediumVals := make([]float64, forecastLength)
    longVals := make([]float64, forecastLength)
    
    for i := 0; i < forecastLength; i++ {
        // Проекция каждого цикла
        shortVals[i] = g.projectCycle(g.shortCycle, i)
        mediumVals[i] = g.projectCycle(g.mediumCycle, i)
        longVals[i] = g.projectCycle(g.longCycle, i)
        
        // Суммирование
        line[i] = shortVals[i] + mediumVals[i] + longVals[i]
    }
    
    // Детекция сигналов (резонанс)
    signals := g.detectSignals(shortVals, mediumVals, longVals)
    
    // Детекция разворотных точек
    uturns := g.detectUTurns(line)
    
    return &CompositeLineResult{
        Line:        line,
        ShortCycle:  shortVals,
        MediumCycle: mediumVals,
        LongCycle:   longVals,
        Signals:     signals,
        UTurns:      uturns,
    }
}

// projectCycle - проекция цикла
func (g *CompositeLineGenerator) projectCycle(c Cycle, index int) float64 {
    return c.Amplitude * math.Sin(2*math.Pi*float64(index)/float64(c.Period) + c.Phase)
}

// detectSignals - детекция сигналов (резонанс)
func (g *CompositeLineGenerator) detectSignals(short, medium, long []float64) []Signal {
    var signals []Signal
    
    for i := 1; i < len(short); i++ {
        // Производные (направление)
        shortDir := short[i] - short[i-1]
        mediumDir := medium[i] - medium[i-1]
        longDir := long[i] - long[i-1]
        
        // Резонанс вверх - все три направлены вверх
        if shortDir > 0 && mediumDir > 0 && longDir > 0 {
            strength := g.calculateStrength(math.Abs(short[i]), math.Abs(medium[i]), math.Abs(long[i]))
            signals = append(signals, Signal{
                Type:     "BUY",
                Strength: strength,
                Index:    i,
                Reason:   "Triple resonance UP",
            })
        }
        
        // Резонанс вниз - все три направлены вниз
        if shortDir < 0 && mediumDir < 0 && longDir < 0 {
            strength := g.calculateStrength(math.Abs(short[i]), math.Abs(medium[i]), math.Abs(long[i]))
            signals = append(signals, Signal{
                Type:     "SELL",
                Strength: strength,
                Index:    i,
                Reason:   "Triple resonance DOWN",
            })
        }
    }
    
    // Фильтрация близких сигналов (оставляем только сильнейшие)
    signals = g.filterSignals(signals)
    
    return signals
}

// calculateStrength - расчёт силы сигнала
func (g *CompositeLineGenerator) calculateStrength(short, medium, long float64) float64 {
    avg := (short + medium + long) / 3
    return math.Min(1.0, avg*2)
}

// detectUTurns - детекция разворотных точек
func (g *CompositeLineGenerator) detectUTurns(line []float64) []UTurn {
    var uturns []UTurn
    
    for i := 1; i < len(line)-1; i++ {
        // Локальный максимум
        if line[i] > line[i-1] && line[i] > line[i+1] {
            uturns = append(uturns, UTurn{
                Index:      i,
                Type:       "TOP",
                Value:      line[i],
                Confidence: g.calculateUTurnConfidence(i, "TOP"),
            })
        }
        
        // Локальный минимум
        if line[i] < line[i-1] && line[i] < line[i+1] {
            uturns = append(uturns, UTurn{
                Index:      i,
                Type:       "BOTTOM",
                Value:      line[i],
                Confidence: g.calculateUTurnConfidence(i, "BOTTOM"),
            })
        }
    }
    
    return uturns
}

// calculateUTurnConfidence - расчёт confidence для разворотной точки
func (g *CompositeLineGenerator) calculateUTurnConfidence(index int, uturnType string) float64 {
    cycles := []Cycle{g.shortCycle, g.mediumCycle, g.longCycle}
    var aligned int
    
    for _, c := range cycles {
        phase := float64(index % c.Period)
        halfPeriod := float64(c.Period) / 2
        
        if uturnType == "TOP" {
            // Для TOP фаза должна быть около quarter периода
            if math.Abs(phase - halfPeriod/2) < 2 {
                aligned++
            }
        } else {
            // Для BOTTOM фаза должна быть около 0
            if phase < 2 || math.Abs(phase - halfPeriod) < 2 {
                aligned++
            }
        }
    }
    
    return float64(aligned) / float64(len(cycles))
}

// filterSignals - фильтрация близких сигналов
func (g *CompositeLineGenerator) filterSignals(signals []Signal) []Signal {
    if len(signals) <= 1 {
        return signals
    }
    
    // Группировка по типу
    buySignals := []Signal{}
    sellSignals := []Signal{}
    
    for _, s := range signals {
        if s.Type == "BUY" {
            buySignals = append(buySignals, s)
        } else {
            sellSignals = append(sellSignals, s)
        }
    }
    
    // Оставляем только сильнейшие в окне 5 дней
    filteredBuy := g.filterWindow(buySignals, 5)
    filteredSell := g.filterWindow(sellSignals, 5)
    
    return append(filteredBuy, filteredSell...)
}

func (g *CompositeLineGenerator) filterWindow(signals []Signal, window int) []Signal {
    if len(signals) <= 1 {
        return signals
    }
    
    var filtered []Signal
    
    for i := 0; i < len(signals); i++ {
        // Проверяем, есть ли более сильный сигнал в окне
        keep := true
        for j := 0; j < len(signals); j++ {
            if i != j && 
               math.Abs(float64(signals[i].Index - signals[j].Index)) < float64(window) &&
               signals[j].Strength > signals[i].Strength {
                keep = false
                break
            }
        }
        if keep {
            filtered = append(filtered, signals[i])
        }
    }
    
    return filtered
}
```

---

### 2.5 Модуль Decennial Patterns

```go
// internal/service/decennial/patterns.go

package decennial

import (
    "time"
    "github.com/cyclecast/internal/domain/entity"
)

// DecennialAnalyzer - анализатор десятилетних паттернов
type DecennialAnalyzer struct{}

type DecennialPattern struct {
    YearDigit  int          `json:"year_digit"`  // 0-9
    DailyData  []DailyPoint `json:"daily_data"`  // 365 точек
    Confidence float64      `json:"confidence"`  // 0-1
    YearsUsed  []int        `json:"years_used"`  // Какие годы использованы
}

type DailyPoint struct {
    DayOfYear  int     `json:"day_of_year"`  // 1-365
    AvgReturn  float64 `json:"avg_return"`   // Среднее значение
    StdDev     float64 `json:"std_dev"`      // Стандартное отклонение
    PosPercent float64 `json:"pos_percent"`  // % положительных дней
}

// Analyze - анализ десятилетних паттернов
func (d *DecennialAnalyzer) Analyze(prices []entity.MarketData, yearDigit int) (*DecennialPattern, error) {
    // 1. Фильтрация по последней цифре года
    filtered := d.filterByYearDigit(prices, yearDigit)
    
    // 2. Группировка по годам
    byYear := d.groupByYear(filtered)
    
    // 3. Нормализация каждого года к 0-1
    normalized := make(map[int][]float64)
    for year, data := range byYear {
        normalized[year] = d.normalizeYear(data)
    }
    
    // 4. Расчёт среднего по дням
    dailyData := d.calculateDailyAverages(normalized)
    
    // 5. Расчёт confidence
    confidence := d.calculateConfidence(normalized)
    
    // 6. Список использованных годов
    yearsUsed := make([]int, 0, len(byYear))
    for year := range byYear {
        yearsUsed = append(yearsUsed, year)
    }
    
    return &DecennialPattern{
        YearDigit:  yearDigit,
        DailyData:  dailyData,
        Confidence: confidence,
        YearsUsed:  yearsUsed,
    }, nil
}

// filterByYearDigit - фильтрация по последней цифре года
func (d *DecennialAnalyzer) filterByYearDigit(prices []entity.MarketData, digit int) []entity.MarketData {
    var result []entity.MarketData
    for _, p := range prices {
        if p.Timestamp.Year()%10 == digit {
            result = append(result, p)
        }
    }
    return result
}

// groupByYear - группировка по годам
func (d *DecennialAnalyzer) groupByYear(prices []entity.MarketData) map[int][]entity.MarketData {
    result := make(map[int][]entity.MarketData)
    for _, p := range prices {
        year := p.Timestamp.Year()
        result[year] = append(result[year], p)
    }
    return result
}

// normalizeYear - нормализация годовых данных к масштабу 0-1
func (d *DecennialAnalyzer) normalizeYear(data []entity.MarketData) []float64 {
    if len(data) == 0 {
        return nil
    }
    
    // Находим min и max close за год
    minClose := data[0].Close
    maxClose := data[0].Close
    for _, p := range data {
        if p.Close < minClose {
            minClose = p.Close
        }
        if p.Close > maxClose {
            maxClose = p.Close
        }
    }
    
    // Нормализуем
    range_ := maxClose - minClose
    if range_ == 0 {
        range_ = 1
    }
    
    normalized := make([]float64, len(data))
    for i, p := range data {
        normalized[i] = (p.Close - minClose) / range_
    }
    
    return normalized
}

// calculateDailyAverages - расчёт средних значений по дням года
func (d *DecennialAnalyzer) calculateDailyAverages(normalized map[int][]float64) []DailyPoint {
    dailyData := make([]DailyPoint, 366)
    
    for day := 1; day <= 366; day++ {
        var values []float64
        var positives int
        
        for _, yearData := range normalized {
            if day <= len(yearData) {
                values = append(values, yearData[day-1])
                if yearData[day-1] > 0.5 {
                    positives++
                }
            }
        }
        
        if len(values) > 0 {
            dailyData[day-1] = DailyPoint{
                DayOfYear:  day,
                AvgReturn:  average(values),
                StdDev:     stdDev(values),
                PosPercent: float64(positives) / float64(len(values)),
            }
        }
    }
    
    return dailyData
}

// CompareWithCurrentYear - сравнение с текущим годом
func (d *DecennialAnalyzer) CompareWithCurrentYear(pattern *DecennialPattern, currentPrices []entity.MarketData) (*ComparisonResult, error) {
    // Нормализация текущего года
    normalizedCurrent := d.normalizeYear(currentPrices)
    
    // Расчёт корреляции
    var patternValues []float64
    var currentValues []float64
    
    for i, val := range normalizedCurrent {
        if i < len(pattern.DailyData) {
            patternValues = append(patternValues, pattern.DailyData[i].AvgReturn)
            currentValues = append(currentValues, val)
        }
    }
    
    correlation := pearsonCorrelation(patternValues, currentValues)
    
    return &ComparisonResult{
        Correlation:      correlation,
        SimilarityScore:  (correlation + 1) / 2, // 0-1
        PatternYearDigit: pattern.YearDigit,
    }, nil
}
```

---

### 2.6 Модуль Phenomenological Model

```go
// internal/service/phenomenological/model.go

package phenomenological

import (
    "github.com/cyclecast/internal/domain/entity"
)

// PhenomModel - модель исторических аналогий
type PhenomModel struct {
    config PhenomConfig
}

type PhenomConfig struct {
    TrainingInterval   int  `json:"training_interval"`    // Окно обучения (100 баров)
    UseDecennialFilter bool `json:"use_decennial_filter"` // Фильтр по Decennial
    TopMatches         int  `json:"top_matches"`          // Топ совпадений (10)
}

type PhenomResult struct {
    Target         []float64      `json:"target"`          // Целевой паттерн
    BestMatches    []PatternMatch `json:"best_matches"`    // Лучшие совпадения
    Projection     []float64      `json:"projection"`      // Проекция продолжения
    AvgCorrelation float64        `json:"avg_correlation"` // Средняя корреляция
}

type PatternMatch struct {
    StartIndex  int     `json:"start_index"`
    EndIndex    int     `json:"end_index"`
    DTWDistance float64 `json:"dtw_distance"`
    Correlation float64 `json:"correlation"`
    Year        int     `json:"year"`
    YearDigit   int     `json:"year_digit"`
}

// Search - поиск исторических аналогий
func (p *PhenomModel) Search(prices []entity.MarketData) *PhenomResult {
    n := len(prices)
    if n < p.config.TrainingInterval {
        return nil
    }
    
    // 1. Training Interval - взять последние N баров как образец
    target := prices[n-p.config.TrainingInterval:]
    targetNormalized := normalizePrices(target)
    
    // 2. Определить yearDigit текущего года
    currentYearDigit := time.Now().Year() % 10
    
    var matches []PatternMatch
    
    // 3. Сканировать историю
    for i := 0; i < n-p.config.TrainingInterval-1; i++ {
        window := prices[i : i+p.config.TrainingInterval]
        lastDate := window[len(window)-1].Timestamp
        windowYearDigit := lastDate.Year() % 10
        
        // 4. Фильтр по Decennial (тот же yearDigit)
        if p.config.UseDecennialFilter && windowYearDigit != currentYearDigit {
            continue
        }
        
        // 5. DTW расстояние
        windowNormalized := normalizePrices(window)
        distance := DTWDistance(targetNormalized, windowNormalized)
        
        // 6. Корреляция Пирсона
        correlation := pearsonCorrelation(targetNormalized, windowNormalized)
        
        matches = append(matches, PatternMatch{
            StartIndex:  i,
            EndIndex:    i + p.config.TrainingInterval,
            DTWDistance: distance,
            Correlation: correlation,
            Year:        lastDate.Year(),
            YearDigit:   windowYearDigit,
        })
    }
    
    // 7. Сортировка по корреляции (убывание)
    sort.Slice(matches, func(i, j int) bool {
        return matches[i].Correlation > matches[j].Correlation
    })
    
    // 8. Best Matches - топ N
    topMatches := matches
    if len(matches) > p.config.TopMatches {
        topMatches = matches[:p.config.TopMatches]
    }
    
    // 9. Проекция продолжения
    projection := p.calculateProjection(prices, topMatches)
    
    // 10. Средняя корреляция
    var avgCorr float64
    for _, m := range topMatches {
        avgCorr += m.Correlation
    }
    if len(topMatches) > 0 {
        avgCorr /= float64(len(topMatches))
    }
    
    return &PhenomResult{
        Target:         targetNormalized,
        BestMatches:    topMatches,
        Projection:     projection,
        AvgCorrelation: avgCorr,
    }
}

// calculateProjection - расчёт проекции продолжения
func (p *PhenomModel) calculateProjection(prices []entity.MarketData, matches []PatternMatch) []float64 {
    if len(matches) == 0 {
        return nil
    }
    
    // Для каждого совпадения берём продолжение паттерна
    var projections [][]float64
    maxLen := 0
    
    for _, m := range matches {
        if m.EndIndex < len(prices) {
            continuation := prices[m.EndIndex:]
            normalized := normalizePrices(continuation)
            projections = append(projections, normalized)
            if len(normalized) > maxLen {
                maxLen = len(normalized)
            }
        }
    }
    
    // Усредняем проекции
    result := make([]float64, maxLen)
    counts := make([]int, maxLen)
    
    for _, proj := range projections {
        for i, v := range proj {
            result[i] += v
            counts[i]++
        }
    }
    
    for i := range result {
        if counts[i] > 0 {
            result[i] /= float64(counts[i])
        }
    }
    
    return result
}

// DTWDistance - Dynamic Time Warping расстояние
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

### 2.7 Модуль COT Analysis

```go
// internal/service/cot/analyzer.go

package cot

import (
    "time"
)

// COTAnalyzer - анализатор COT данных
type COTAnalyzer struct{}

type COTData struct {
    Symbol          string       `json:"symbol"`
    ReportDate      time.Time    `json:"report_date"`
    Commercials     COTPosition  `json:"commercials"`
    LargeSpecs      COTPosition  `json:"large_specs"`
    SmallSpecs      COTPosition  `json:"small_specs"`
    CommercialIndex float64      `json:"commercial_index"` // 0-100
    IsExtreme       bool         `json:"is_extreme"`
    SignalType      string       `json:"signal_type,omitempty"`
}

type COTPosition struct {
    Long       int64   `json:"long"`
    Short      int64   `json:"short"`
    Net        int64   `json:"net"`
    Percentile float64 `json:"percentile"` // 0-100
}

type COTResult struct {
    Data          []COTData `json:"data"`
    LastSignal    string    `json:"last_signal"`
    ExtremeLevel  float64   `json:"extreme_level"`
}

// Analyze - анализ COT данных
func (c *COTAnalyzer) Analyze(cotData []COTData, period int) *COTResult {
    // Расчёт COT Index
    c.calculateCOTIndex(cotData, period)
    
    // Детекция экстремумов
    c.detectExtremes(cotData)
    
    // Последний сигнал
    lastSignal := ""
    if len(cotData) > 0 {
        last := cotData[len(cotData)-1]
        if last.SignalType != "" {
            lastSignal = last.SignalType
        }
    }
    
    return &COTResult{
        Data:         cotData,
        LastSignal:   lastSignal,
        ExtremeLevel: 0, // Заполняется при детекции
    }
}

// calculateCOTIndex - расчёт COT Index
func (c *COTAnalyzer) calculateCOTIndex(cotData []COTData, period int) {
    for i := period - 1; i < len(cotData); i++ {
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
    }
}

// detectExtremes - детекция экстремальных позиций
func (c *COTAnalyzer) detectExtremes(cotData []COTData) {
    for i := range cotData {
        idx := cotData[i].CommercialIndex
        
        if idx > 80 {
            cotData[i].IsExtreme = true
            cotData[i].SignalType = "BULLISH" // Commercials в покупках
        } else if idx < 20 {
            cotData[i].IsExtreme = true
            cotData[i].SignalType = "BEARISH" // Commercials в продажах
        }
    }
}
```

---

### 2.8 Модуль Qualified Trend Break

```go
// internal/service/qtb/trend_break.go

package qtb

import (
    "github.com/cyclecast/internal/domain/entity"
)

// QTBAnalyzer - анализатор Qualified Trend Break
type QTBAnalyzer struct{}

type TrendLine struct {
    StartPrice float64
    StartIndex int
    Slope      float64
}

type QTBResult struct {
    Status    string  `json:"status"`     // NO_BREAKOUT, CONFIRM, FALSE
    Direction string  `json:"direction"`  // UP, DOWN
    Reason    string  `json:"reason"`
}

// Analyze - анализ пробоя тренда
func (q *QTBAnalyzer) Analyze(prices []entity.MarketData, compositeLine []float64, trendLine TrendLine) *QTBResult {
    n := len(prices)
    if n < 2 || len(compositeLine) < 2 {
        return &QTBResult{Status: "NO_BREAKOUT"}
    }
    
    // Детекция пробоя трендовой линии
    currentPrice := prices[n-1].Close
    prevPrice := prices[n-2].Close
    
    trendValue := trendLine.Calculate(n - 1)
    prevTrendValue := trendLine.Calculate(n - 2)
    
    isBreakout := false
    breakoutDirection := ""
    
    // Пробой вверх
    if currentPrice > trendValue && prevPrice <= prevTrendValue {
        isBreakout = true
        breakoutDirection = "UP"
    }
    
    // Пробой вниз
    if currentPrice < trendValue && prevPrice >= prevTrendValue {
        isBreakout = true
        breakoutDirection = "DOWN"
    }
    
    if !isBreakout {
        return &QTBResult{Status: "NO_BREAKOUT"}
    }
    
    // Проверка через Composite Line
    compositeDir := ""
    m := len(compositeLine)
    if compositeLine[m-1] > compositeLine[m-2] {
        compositeDir = "UP"
    } else {
        compositeDir = "DOWN"
    }
    
    // Квалификация пробоя
    if breakoutDirection == compositeDir {
        return &QTBResult{
            Status:    "CONFIRM",
            Direction: breakoutDirection,
            Reason:    "Composite Line подтверждает направление",
        }
    } else {
        return &QTBResult{
            Status:    "FALSE",
            Direction: breakoutDirection,
            Reason:    "Composite Line направлен в противоположную сторону",
        }
    }
}

// Calculate - расчёт значения трендовой линии
func (t *TrendLine) Calculate(index int) float64 {
    return t.StartPrice + t.Slope*float64(index-t.StartIndex)
}
```

---

### 2.9 Модуль интеграции (Williams Workflow)

```go
// internal/service/workflow/williams.go

package workflow

import (
    "github.com/cyclecast/internal/service/seasonality"
    "github.com/cyclecast/internal/service/decennial"
    "github.com/cyclecast/internal/service/cycle"
    "github.com/cyclecast/internal/service/phenomenological"
    "github.com/cyclecast/internal/service/cot"
    "github.com/cyclecast/internal/service/qtb"
)

// WilliamsWorkflow - главный workflow по методологии Ларри Вильямса
type WilliamsWorkflow struct {
    annualCycle    *seasonality.AnnualCycleAnalyzer
    fteValidator   *seasonality.FTEValidator
    decennial      *decennial.DecennialAnalyzer
    qspectrum      *cycle.QSpectrumAnalyzer
    composite      *cycle.CompositeLineGenerator
    phenom         *phenomenological.PhenomModel
    cotAnalyzer    *cot.COTAnalyzer
    qtbAnalyzer    *qtb.QTBAnalyzer
}

type WorkflowConfig struct {
    Symbols        []string `json:"symbols"`
    LookAheadDays  int      `json:"look_ahead_days"`  // 30-90 дней
    ForecastDays   int      `json:"forecast_days"`    // Прогноз Composite Line
    MinFTE         float64  `json:"min_fte"`          // Минимальный FTE (0.0)
}

type WorkflowResult struct {
    ActiveAssets []AssetAnalysis `json:"active_assets"`
    Signals      []FinalSignal   `json:"signals"`
    Status       string          `json:"status"`
}

type AssetAnalysis struct {
    Symbol          string                           `json:"symbol"`
    Seasonality     *seasonality.AnnualCycleResult   `json:"seasonality"`
    FTE             *seasonality.FTEResult           `json:"fte"`
    Decennial       *decennial.DecennialPattern      `json:"decennial"`
    Composite       *cycle.CompositeLineResult       `json:"composite"`
    Phenom          *phenomenological.PhenomResult   `json:"phenom"`
    COT             *cot.COTResult                   `json:"cot"`
}

type FinalSignal struct {
    Symbol    string    `json:"symbol"`
    Type      string    `json:"type"`      // BUY, SELL
    Strength  float64   `json:"strength"`  // 0-1
    Timestamp time.Time `json:"timestamp"`
    Reason    string    `json:"reason"`
}

// Execute - выполнение workflow
func (w *WilliamsWorkflow) Execute(config WorkflowConfig) *WorkflowResult {
    // Шаг 1: Annual Cycle - определить "ЧТО торговать"
    activeAssets := w.selectAssetsBySeasonality(config)
    
    if len(activeAssets) == 0 {
        return &WorkflowResult{Status: "NO_ASSETS"}
    }
    
    // Шаг 2: Decennial - контекст года
    currentYearDigit := time.Now().Year() % 10
    for i := range activeAssets {
        pattern, _ := w.decennial.Analyze(activeAssets[i].Prices, currentYearDigit)
        activeAssets[i].Decennial = pattern
    }
    
    // Шаг 3: Composite Line - "КОГДА входить"
    for i := range activeAssets {
        result, _ := w.qspectrum.Analyze(extractClose(activeAssets[i].Prices))
        if len(result.Top3Cycles) == 3 {
            gen := cycle.NewCompositeLineGenerator(result.Top3Cycles)
            activeAssets[i].Composite = gen.Generate(config.ForecastDays)
        }
    }
    
    // Шаг 4: Phenomenological - проверка историей
    for i := range activeAssets {
        activeAssets[i].Phenom = w.phenom.Search(activeAssets[i].Prices)
    }
    
    // Шаг 5: COT - подтверждение "умными деньгами"
    for i := range activeAssets {
        cotData := w.loadCOTData(activeAssets[i].Symbol)
        activeAssets[i].COT = w.cotAnalyzer.Analyze(cotData, 26)
    }
    
    // Шаг 6: Генерация итоговых сигналов
    signals := w.generateSignals(activeAssets)
    
    return &WorkflowResult{
        ActiveAssets: activeAssets,
        Signals:      signals,
        Status:       "SUCCESS",
    }
}

// selectAssetsBySeasonality - отбор активов по сезонности
func (w *WilliamsWorkflow) selectAssetsBySeasonality(config WorkflowConfig) []AssetAnalysis {
    var activeAssets []AssetAnalysis
    
    for _, symbol := range config.Symbols {
        prices := w.loadPrices(symbol)
        
        // Annual Cycle
        annualCycle, err := w.annualCycle.Analyze(prices)
        if err != nil {
            continue
        }
        
        // FTE валидация
        fte := w.fteValidator.Validate(prices, *annualCycle)
        if !fte.IsValid || fte.Correlation < config.MinFTE {
            continue
        }
        
        // Поиск сезонного окна
        currentDay := time.Now().YearDay()
        window := w.annualCycle.FindSeasonalWindow(annualCycle.Cycle, currentDay, config.LookAheadDays)
        
        if window.Strength > 0.6 {
            activeAssets = append(activeAssets, AssetAnalysis{
                Symbol:      symbol,
                Prices:      prices,
                Seasonality: annualCycle,
                FTE:         fte,
            })
        }
    }
    
    return activeAssets
}

// generateSignals - генерация итоговых сигналов
func (w *WilliamsWorkflow) generateSignals(assets []AssetAnalysis) []FinalSignal {
    var signals []FinalSignal
    
    for _, asset := range assets {
        if asset.Composite == nil {
            continue
        }
        
        // Анализ сигналов Composite Line
        for _, sig := range asset.Composite.Signals {
            // Подтверждение от COT
            cotConfirm := false
            if asset.COT != nil {
                if sig.Type == "BUY" && asset.COT.LastSignal == "BULLISH" {
                    cotConfirm = true
                } else if sig.Type == "SELL" && asset.COT.LastSignal == "BEARISH" {
                    cotConfirm = true
                }
            }
            
            // Подтверждение от Phenom
            phenomConfirm := false
            if asset.Phenom != nil {
                projDir := "NEUTRAL"
                if len(asset.Phenom.Projection) > 0 {
                    last := asset.Phenom.Projection[len(asset.Phenom.Projection)-1]
                    first := asset.Phenom.Projection[0]
                    if last > first {
                        projDir = "UP"
                    } else if last < first {
                        projDir = "DOWN"
                    }
                }
                
                if sig.Type == "BUY" && projDir == "UP" {
                    phenomConfirm = true
                } else if sig.Type == "SELL" && projDir == "DOWN" {
                    phenomConfirm = true
                }
            }
            
            // Генерация сигнала если все подтверждения
            if cotConfirm && phenomConfirm {
                signals = append(signals, FinalSignal{
                    Symbol:    asset.Symbol,
                    Type:      sig.Type,
                    Strength:  sig.Strength,
                    Timestamp: time.Now().AddDate(0, 0, sig.Index),
                    Reason:    "Composite + COT + Phenom confirmation",
                })
            }
        }
    }
    
    return signals
}
```

---

## 3. СХЕМА БАЗЫ ДАННЫХ

### 3.1 PostgreSQL Schema

```sql
-- migrations/001_init.up.sql

-- Расширение TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Инструменты
CREATE TABLE instruments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200),
    exchange VARCHAR(50),
    type VARCHAR(20) NOT NULL, -- STOCK, INDEX, FOREX, COMMODITY, CRYPTO, FUTURES
    currency VARCHAR(10) DEFAULT 'USD',
    tick_size DECIMAL(20, 10),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Исторические данные (TimescaleDB hypertable)
CREATE TABLE market_data (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL, -- 1m, 5m, 1h, 1d, 1w, 1M
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(20, 8),
    normalized_close DECIMAL(10, 6), -- 0-1
    year_digit SMALLINT, -- 0-9 для Decennial
    detrended_close DECIMAL(20, 8),
    PRIMARY KEY (time, instrument_id, timeframe)
);

-- Преобразование в hypertable
SELECT create_hypertable('market_data', 'time');

-- Индексы
CREATE INDEX idx_market_data_instrument ON market_data(instrument_id);
CREATE INDEX idx_market_data_timeframe ON market_data(timeframe);
CREATE INDEX idx_market_data_year_digit ON market_data(year_digit);

-- Циклы
CREATE TABLE cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    period INTEGER NOT NULL,
    energy DECIMAL(10, 6),
    stability DECIMAL(10, 6),
    correlation DECIMAL(10, 6),
    phase DECIMAL(10, 6),
    amplitude DECIMAL(20, 8),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    UNIQUE (instrument_id, timeframe, period)
);

-- Composite Lines
CREATE TABLE composite_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    short_cycle_id UUID REFERENCES cycles(id),
    medium_cycle_id UUID REFERENCES cycles(id),
    long_cycle_id UUID REFERENCES cycles(id),
    line_data JSONB NOT NULL,
    signals JSONB,
    uturns JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Annual Cycles
CREATE TABLE annual_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    year_digit SMALLINT, -- NULL для общего Annual Cycle, 0-9 для Decennial
    cycle_data JSONB NOT NULL,
    confidence_data JSONB,
    years_used INTEGER,
    is_valid BOOLEAN,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (instrument_id, year_digit)
);

-- COT Data
CREATE TABLE cot_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    report_date DATE NOT NULL,
    commercials_long BIGINT,
    commercials_short BIGINT,
    commercials_net BIGINT,
    large_specs_long BIGINT,
    large_specs_short BIGINT,
    small_specs_long BIGINT,
    small_specs_short BIGINT,
    commercial_index DECIMAL(5, 2), -- 0-100
    is_extreme BOOLEAN,
    signal_type VARCHAR(20),
    UNIQUE (instrument_id, report_date)
);

-- Phenomenological Matches
CREATE TABLE phenom_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    training_interval INTEGER NOT NULL,
    target_start TIMESTAMP WITH TIME ZONE,
    match_year INTEGER,
    match_year_digit SMALLINT,
    correlation DECIMAL(10, 6),
    dtw_distance DECIMAL(20, 8),
    projection_data JSONB,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Прогнозы
CREATE TABLE projections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    timeframe VARCHAR(10) NOT NULL,
    projection_type VARCHAR(50) NOT NULL, -- COMPOSITE, PHENOM, DECENNIAL
    projection_data JSONB NOT NULL,
    confidence DECIMAL(5, 4),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_from TIMESTAMP WITH TIME ZONE,
    valid_until TIMESTAMP WITH TIME ZONE
);

-- Сигналы
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    signal_type VARCHAR(10) NOT NULL, -- BUY, SELL
    strength DECIMAL(5, 4),
    reason TEXT,
    target_time TIMESTAMP WITH TIME ZONE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, TRIGGERED, EXPIRED
    triggered_at TIMESTAMP WITH TIME ZONE,
    price_at_signal DECIMAL(20, 8)
);
```

---

## 4. API ENDPOINTS

### 4.1 REST API

```
# Market Data
POST   /api/v1/market/import                  - Импорт данных
GET    /api/v1/market/symbols                 - Список инструментов
GET    /api/v1/market/symbols/{symbol}        - Данные по инструменту
GET    /api/v1/market/symbols/{symbol}/history - Исторические данные

# Annual Cycle
POST   /api/v1/analysis/annual-cycle          - Расчёт Annual Cycle
GET    /api/v1/analysis/annual-cycle/{symbol} - Получить сохранённый

# FTE
POST   /api/v1/analysis/fte                   - FTE валидация

# QSpectrum & Composite Line
POST   /api/v1/analysis/qspectrum             - QSpectrum анализ
POST   /api/v1/analysis/composite             - Composite Line

# Decennial Patterns
POST   /api/v1/analysis/decennial             - Decennial анализ
GET    /api/v1/analysis/decennial/{digit}     - Паттерн по цифре

# Phenomenological
POST   /api/v1/analysis/phenom                - Поиск аналогий

# U-Turn
POST   /api/v1/analysis/uturn                 - Детекция U-Turn

# COT
GET    /api/v1/cot/{symbol}                   - COT данные
POST   /api/v1/cot/import                     - Импорт COT

# Qualified Trend Break
POST   /api/v1/analysis/qtb                   - QTB анализ

# Workflow (Ларри Вильямс)
POST   /api/v1/workflow/williams              - Полный workflow
GET    /api/v1/signals/{symbol}               - Активные сигналы
```

---

## 5. ФОРМУЛЫ И АЛГОРИТМЫ

### 5.1 Annual Cycle
```
Детрендинг:
Detrended(t) = Price(t) - MA(t)

Нормализация:
NormalizedPrice = (Price - Min_year) / (Max_year - Min_year)

Annual Cycle:
AC(day) = Σ(year=1 to N) [NormalizedPrice(year, day)] / N
```

### 5.2 Forward Testing Efficiency
```
FTE = Correlation_Pearson(Projection_line, Actual_price)

r = Σ(xᵢ - x̄)(yᵢ - ȳ) / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]

Статус:
- FTE > 0.3: STRONG
- FTE > 0: VALID
- FTE < 0: BROKEN (игнорировать)
```

### 5.3 QSpectrum (Циклическая корреляция + МЭМ)

> **QSpectrum ≠ FFT!** Разработан специально для нестационарных финансовых данных.

```
МЕТОД 1: Циклическая корреляция (основной)
─────────────────────────────────────────
CyclicCorrelation(period) = Σ(t=period to N) [P(t) × P(t-period)] / (N - period)

Энергия цикла:
Energy(period) = |CyclicCorrelation| × √(N/period) × WFA_Stability

МЕТОД 2: МЭМ — Метод максимальной энтропии (Burg's method)
───────────────────────────────────────────────────────────
Спектральная плотность мощности:
P(f) = σ² / |1 + Σ(k=1 to p) aₖ × e^(-i2πfk)|²

Где:
- σ² — дисперсия ошибки предсказания
- aₖ — коэффициенты авторегрессии (вычисляются методом Burg)
- p — порядок модели

МЕТОД 3: Walk-Forward Stability
───────────────────────────────
WFA_Stability = Count(Correlation > 0) / Total_Periods

ОТЛИЧИЕ ОТ FFT:
───────────────
┌─────────────────────────────┬─────────────────────────────────┐
│ FFT                         │ QSpectrum                        │
├─────────────────────────────┼─────────────────────────────────┤
│ Стационарные данные         │ Нестационарные (цена)            │
│ Запаздывание                │ Минимум запаздывания             │
│ Не учитывает "исчезающие"   │ WFA оценивает устойчивость       │
│ Одна частота = результат    │ Энергия = устойчивость × коррел. │
└─────────────────────────────┴─────────────────────────────────┘
```

### 5.4 Composite Line
```
CL(t) = A₁sin(2πf₁t + φ₁) + A₂sin(2πf₂t + φ₂) + A₃sin(2πf₃t + φ₃)

Где:
- A = амплитуда
- f = частота (1/период)
- φ = фаза

Резонанс (сигналы):
- BUY: все 3 цикла направлены вверх (производная > 0)
- SELL: все 3 цикла направлены вниз (производная < 0)
```

### 5.5 Decennial Patterns
```
DP(digit, day) = Average(NormalizedPrice) for years where year%10 == digit

Нормализация:
NormalizedPrice = (Price - Min_year) / (Max_year - Min_year)
```

### 5.6 COT Index
```
COT_Index = (Current_Net - Min_N) / (Max_N - Min_N) × 100

Где:
- Net = Commercials_Long - Commercials_Short
- N = период (26 или 52 недели)

Экстремумы:
- COT_Index > 80: BULLISH (Commercials покупают)
- COT_Index < 20: BEARISH (Commercials продают)
```

### 5.7 DTW (Dynamic Time Warping)
```
DTW(i,j) = |xᵢ - yⱼ| + min(DTW(i-1,j), DTW(i,j-1), DTW(i-1,j-1))

Similarity = 1 / (1 + DTW_distance)
```

---

## 6. ИТОГОВЫЙ АЛГОРИТМ ЛАРРИ ВИЛЬЯМСА

```
1. Annual Cycle (Seasonality):
   - Загрузить 30-50 лет данных
   - Рассчитать сезонную кривую
   - FTE валидация (игнорировать если FTE < 0)
   - Найти активы с сильным сезонным окном
   
2. Decennial Patterns:
   - Определить yearDigit текущего года
   - Загрузить паттерн для этой цифры
   - Оценить контекст года (бычий/медвежий)
   
3. Composite Line (Williams Cycle Forecast):
   - QSpectrum: найти 3 доминантных цикла
   - Наложить 3 волны (short/medium/long)
   - Найти точки резонанса (BUY/SELL)
   
4. Phenomenological Model:
   - Взять Training Interval (последние N баров)
   - Найти Best Matches в истории
   - Фильтр по Decennial (тот же yearDigit)
   - Проекция продолжения
   
5. COT (Commercials):
   - Загрузить позиции хеджеров
   - Рассчитать COT Index
   - Найти экстремумы (>80 / <20)
   
6. Qualified Trend Break:
   - Детектировать пробой трендовой линии
   - Подтвердить направлением Composite Line
   
7. Итоговый сигнал:
   - Composite Line указывает направление
   - COT подтверждает (Commercials на той же стороне)
   - Phenom подтверждает (исторические аналогии)
   - QTB подтверждает (пробой квалифицирован)
   
8. Исполнение:
   - Вход в сделку при всех подтверждениях
   - Выход по времени (через N дней по циклу)
```

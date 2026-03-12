# ТЕХНИЧЕСКОЕ РЕШЕНИЕ
## Система циклического анализа и прогнозирования финансовых рынков
### CycleCast - Методология Ларри Вильямса v3.0

---

## 1. АРХИТЕКТУРА СИСТЕМЫ

### 1.1 Высокоуровневая архитектура
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    PRESENTATION LAYER                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐   │
│  │   Web SPA     │  │   Desktop     │  │   CLI Tool    │  │   External API  │   │
│  │   (React)     │  │   (Electron)  │  │   (Go CLI)    │  │   (REST/gRPC)   │   │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └────────┬────────┘   │
└──────────┼──────────────────┼──────────────────┼───────────────────┼────────────┘
           └──────────────────┴──────────────────┴───────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                     GATEWAY LAYER                                 │ 
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                              API Gateway (Gin)                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │ REST :8080  │  │ gRPC :9090  │  │ WS :8080/ws │  │ Auth/RateLimit  │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                          │
           ┌──────────────────────────────┴──────────────────────────────┐
           ▼                                                             ▼
┌─────────────────────────────────────┐       ┌─────────────────────────────────────┐
│         GO BACKEND (Core)           │       │      PYTHON QUANT (Math/ML)         │
│  ┌─────────────────────────────┐    │  gRPC │  ┌─────────────────────────────┐    │
│  │   Service Layer             │    │ ◄───► │  │   QSpectrum (Burg's MEM)    │    │
│  │   - MarketDataSvc           │    │       │  │   Phenomenological (DTW)    │    │
│  │   - AnnualCycleSvc          │    │       │  │   Walk-Forward Analysis     │    │
│  │   - CompositeSvc            │    │       │  │   ML Filters (XGBoost)      │    │
│  │   - COT/GBTC Analyzer       │    │       │  │   Bootstrap CI              │    │
│  │   - Risk Management         │    │       │  └─────────────────────────────┘    │
│  │   - Backtest Engine         │    │                                            │
│  └─────────────────────────────┘    │       ┌─────────────────────────────┐    │
│                                      │       │   Libraries:                  │    │
│  ┌─────────────────────────────┐    │       │   - NumPy, SciPy              │    │
│  │   Repository Layer          │    │       │   - Statsmodels               │    │
│  │   - PostgreSQL              │    │       │   - scikit-learn              │    │
│  │   - TimescaleDB             │    │       └─────────────────────────────┘    │
│  │   - Redis                   │    │                                            │
│  └─────────────────────────────┘    │                                            │
└─────────────────────────────────────┘                                            │
           │                                                                       │
           ▼                                                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA LAYER                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐   │
│  │ PostgreSQL 16 │  │ TimescaleDB   │  │ Redis 7       │  │ HashiCorp Vault │   │
│  │ (Primary DB)  │  │ (Time Series) │  │ (Cache/Queue) │  │ (Secrets)       │   │
│  └───────────────┘  └───────────────┘  └───────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. СХЕМА БАЗЫ ДАННЫХ

### 2.1 Таблица `instruments` (обновлённая)
```sql
CREATE TABLE instruments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol              VARCHAR(20) NOT NULL UNIQUE,
    name                VARCHAR(200),
    exchange            VARCHAR(50),
    type                VARCHAR(20) NOT NULL,  -- STOCK, INDEX, FOREX, COMMODITY, CRYPTO, FUTURES
    currency            VARCHAR(10) DEFAULT 'USD',
    tick_size           DECIMAL(20, 10),
    is_active           BOOLEAN DEFAULT true,
    
    -- Crypto/GBTC адаптация
    proxy_type          VARCHAR(20),           -- 'FUTURES', 'TRUST', 'ETF'
    regime_change_date  DATE,                  -- Для GBTC: '2024-01-11'
    day_close_utc       TIME,                  -- Для BTC: '20:00:00'
    signal_direction    SMALLINT DEFAULT 1,    -- 1 (прямая), -1 (инверсия)
    proxy_list          JSONB,                 -- ["GBTC", "IBIT"]
    proxy_weights       JSONB,                 -- {"GBTC": 0.5, "IBIT": 0.3, "FBIT": 0.2}
    fte_threshold       NUMERIC DEFAULT 0.05,  -- Адаптивный порог FTE
    min_signal_distance INT DEFAULT 21,        -- Мин. расстояние между сигналами (дни)
    
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.2 Таблица `market_data` (TimescaleDB)
```sql
CREATE TABLE market_data (
    time                TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument_id       UUID NOT NULL REFERENCES instruments(id),
    timeframe           VARCHAR(10) NOT NULL,
    open                DECIMAL(20, 8) NOT NULL,
    high                DECIMAL(20, 8) NOT NULL,
    low                 DECIMAL(20, 8) NOT NULL,
    close               DECIMAL(20, 8) NOT NULL,
    volume              BIGINT,
    adjusted_close      DECIMAL(20, 8),
    normalized_close    DECIMAL(10, 6),
    year_digit          SMALLINT,
    detrended_close     DECIMAL(20, 8),
    PRIMARY KEY (time, instrument_id, timeframe)
);

SELECT create_hypertable('market_data', 'time');
```

### 2.3 Таблица `cot_data` (обновлённая)
```sql
CREATE TABLE cot_data (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id       UUID NOT NULL REFERENCES instruments(id),
    report_date         DATE NOT NULL,
    
    -- Позиции (фьючерсы)
    commercials_long    BIGINT,
    commercials_short   BIGINT,
    commercials_net     BIGINT,
    large_specs_long    BIGINT,
    large_specs_short   BIGINT,
    small_specs_long    BIGINT,
    small_specs_short   BIGINT,
    
    -- Трасты/ETF (GBTC)
    premium             DECIMAL(10, 4),
    nav                 DECIMAL(20, 8),
    
    -- Индексы
    commercial_index    DECIMAL(5, 2),
    is_extreme          BOOLEAN,
    signal_type         VARCHAR(20),
    
    -- Статистическая значимость (НОВОЕ)
    p_value             DECIMAL(5, 4),
    ci_lower            DECIMAL(5, 4),
    ci_upper            DECIMAL(5, 4),
    n_observations      INTEGER,
    
    UNIQUE (instrument_id, report_date)
);
```

### 2.4 Таблица `backtest_results` (НОВАЯ)
```sql
CREATE TABLE backtest_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_name       VARCHAR(100) NOT NULL,
    instrument_id       UUID REFERENCES instruments(id),
    
    -- Период
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    is_in_sample        BOOLEAN,
    
    -- Метрики
    total_return        DECIMAL(10, 4),
    cagr                DECIMAL(10, 4),
    sharpe_ratio        DECIMAL(10, 4),
    max_drawdown        DECIMAL(10, 4),
    win_rate            DECIMAL(5, 4),
    profit_factor       DECIMAL(10, 4),
    total_trades        INTEGER,
    
    -- Статистика (НОВОЕ)
    p_value             DECIMAL(5, 4),
    bootstrap_ci_lower  DECIMAL(10, 4),
    bootstrap_ci_upper  DECIMAL(10, 4),
    
    -- Equity curve (JSON)
    equity_curve        JSONB,
    
    calculated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.5 Таблица `signals` (обновлённая)
```sql
CREATE TABLE signals (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id       UUID NOT NULL REFERENCES instruments(id),
    signal_type         VARCHAR(10) NOT NULL,  -- BUY, SELL
    strength            DECIMAL(5, 4),
    initial_strength    DECIMAL(5, 4),         -- Для Signal Decay
    half_life_days      INTEGER DEFAULT 14,    -- Для Signal Decay
    age_days            INTEGER DEFAULT 0,
    reason              TEXT,
    target_time         TIMESTAMP WITH TIME ZONE,
    generated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status              VARCHAR(20) DEFAULT 'PENDING',
    triggered_at        TIMESTAMP WITH TIME ZONE,
    price_at_signal     DECIMAL(20, 8),
    
    -- Статистическая значимость (НОВОЕ)
    p_value             DECIMAL(5, 4),
    confidence_level    DECIMAL(5, 4),
    
    -- Risk Management (НОВОЕ)
    position_size       DECIMAL(20, 8),
    stop_loss           DECIMAL(20, 8),
    take_profit         DECIMAL(20, 8)
);
```

### 2.6 Таблица `cycles`
```sql
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
```

### 2.7 Таблица `composite_lines`
```sql
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
```

### 2.8 Таблица `annual_cycles`
```sql
CREATE TABLE annual_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    year_digit SMALLINT, -- NULL для общего Annual Cycle, 0-9 для Decennial
    cycle_data JSONB NOT NULL,
    confidence_data JSONB,
    years_used INTEGER,
    is_valid BOOLEAN,
    fte_correlation DECIMAL(5, 4),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (instrument_id, year_digit)
);
```

---

## 3. МОДУЛИ И СЕРВИСЫ

### 3.1 Go Backend (Core)
| Модуль | Путь | Описание |
|--------|------|----------|
| MarketData | `internal/service/marketdata/` | Импорт, валидация, кэш |
| AnnualCycle | `internal/service/seasonality/` | Сезонность, FTE |
| Composite | `internal/service/cycle/` | Composite Line, U-Turn |
| COT/GBTC | `internal/service/cot/` | COT + GBTC адаптация |
| Risk | `internal/service/risk/` | Position Sizing, Stop-Loss, Signal Decay |
| Backtest | `internal/service/backtest/` | Симуляция на истории, Bootstrap |
| Workflow | `internal/service/workflow/` | Интеграция всех модулей |
| Statistics | `internal/service/stats/` | p-value, CI, Chow Test |

### 3.2 Python Quant (Math/ML)
| Модуль | Путь | Описание |
|--------|------|----------|
| QSpectrum | `quant/qspectrum/` | Циклическая корреляция, Burg's MEM |
| Phenomenological | `quant/phenom/` | DTW, поиск аналогий |
| WFA | `quant/wfa/` | Walk-Forward Analysis |
| ML Filters | `quant/ml/` | XGBoost, режимы рынка |
| Bootstrap | `quant/bootstrap/` | Доверительные интервалы |

### 3.3 gRPC Proto (интерфейс Go ↔ Python)
```protobuf
syntax = "proto3";

package quant;

service QuantService {
    rpc QSpectrum(QSpectrumRequest) returns (QSpectrumResponse);
    rpc PhenomSearch(PhenomRequest) returns (PhenomResponse);
    rpc WalkForward(WFARequest) returns (WFAResponse);
    rpc Bootstrap(BootstrapRequest) returns (BootstrapResponse);
    rpc ChowTest(ChowTestRequest) returns (ChowTestResponse);
}

message QSpectrumRequest {
    repeated double prices = 1;
    int32 min_period = 2;
    int32 max_period = 3;
    double energy_threshold = 4;
    bool use_mem = 5;
    int32 mem_order = 6;
}

message Cycle {
    int32 period = 1;
    double energy = 2;
    double stability = 3;
    double correlation = 4;
    double phase = 5;
    double amplitude = 6;
}

message QSpectrumResponse {
    repeated Cycle cycles = 1;
    repeated Cycle top3 = 2;
}

message PhenomRequest {
    repeated double prices = 1;
    int32 training_interval = 2;
    bool use_decennial_filter = 3;
    int32 current_year_digit = 4;
    int32 top_matches = 5;
}

message PatternMatch {
    int32 start_index = 1;
    int32 end_index = 2;
    double dtw_distance = 3;
    double correlation = 4;
    int32 year = 5;
}

message PhenomResponse {
    repeated PatternMatch best_matches = 1;
    repeated double projection = 2;
    double avg_correlation = 3;
}

message BootstrapRequest {
    repeated double returns = 1;
    int32 iterations = 2;  // 1000
    double confidence_level = 3;  // 0.95
}

message BootstrapResponse {
    double ci_lower = 1;
    double ci_upper = 2;
    double p_value = 3;
    double mean = 4;
    double std = 5;
}

message ChowTestRequest {
    repeated double data = 1;
    int32 breakpoint = 2;
}

message ChowTestResponse {
    double f_statistic = 1;
    double p_value = 2;
    bool is_structural_break = 3;
}
```

---

## 4. API ENDPOINTS

### 4.1 REST API
```
# Market Data
POST   /api/v1/market/import
GET    /api/v1/market/symbols
GET    /api/v1/market/symbols/{id}
GET    /api/v1/market/history
GET    /api/v1/market/history/aligned
DELETE /api/v1/market/symbols/{id}

# Analysis
POST   /api/v1/analysis/annual-cycle
POST   /api/v1/analysis/fte
POST   /api/v1/analysis/qspectrum
POST   /api/v1/analysis/composite
POST   /api/v1/analysis/decennial
POST   /api/v1/analysis/phenom
POST   /api/v1/analysis/uturn

# COT/GBTC
GET    /api/v1/cot/{symbol}
POST   /api/v1/cot/import
POST   /api/v1/cot/gbtc

# Risk & Backtest
POST   /api/v1/risk/calculate
POST   /api/v1/backtest/run
GET    /api/v1/backtest/results/{id}
GET    /api/v1/backtest/results

# Workflow
POST   /api/v1/workflow/williams
GET    /api/v1/signals/{symbol}
GET    /api/v1/signals

# Statistics (НОВОЕ)
GET    /api/v1/stats/significance/{signal_id}
POST   /api/v1/stats/chow-test
POST   /api/v1/stats/bootstrap
```

### 4.2 gRPC (внутренний)
```
POST   /grpc/quant/qspectrum
POST   /grpc/quant/phenom
POST   /grpc/quant/wfa
POST   /grpc/quant/bootstrap
POST   /grpc/quant/chow-test
```

---

## 5. КОНФИГУРАЦИЯ

### 5.1 config.yaml (пример)
```yaml
server:
  port: 8080
  grpc_port: 9090

database:
  postgres: "postgresql://user:pass@localhost:5432/cyclecast"
  redis: "redis://localhost:6379"

python_service:
  url: "python-quant:50051"
  timeout: 30s

backtest:
  require_before_production: true
  min_sharpe: 1.0
  max_drawdown: 0.20
  bootstrap_iterations: 1000

crypto:
  fte_threshold: 0.08
  min_years: 10
  day_close_utc: "20:00:00"

gbtc:
  regime_change_date: "2024-01-11"
  signal_direction: -1
  proxy_list: ["GBTC", "IBIT"]
  min_signal_distance_days: 21

risk:
  per_trade_percent: 0.02
  max_drawdown: 0.20
  signal_half_life_days: 14

statistics:
  p_value_threshold: 0.05
  confidence_level: 0.95
```

---

## 6. ФОРМУЛЫ И АЛГОРИТМЫ

### 6.1 Annual Cycle
```
Детрендинг:
Detrended = Price - MA(t)

Нормализация:
NormalizedPrice = (Price - Min_year) / (Max_year - Min_year)

Annual Cycle:
AC(day) = Σ(year=1 to N) [NormalizedPrice(year, day)] / N
```

### 6.2 QSpectrum (Циклическая корреляция + МЭМ)
```
QSpectrum ≠ FFT! Разработан для нестационарных финансовых данных.

1. Циклическая корреляция (основной):
   CyclicCorrelation(period) = Σ P(t) × P(t-period) / (N - period)

2. Энергия цикла:
   Energy(period) = |CyclicCorrelation| × √(N/period) × WFA_Stability

3. МЭМ — спектральная плотность (Burg's method):
   P(f) = σ² / |1 + Σ aₖ × e^(-i2πfk)|²

4. Walk-Forward Stability:
   WFA_Stability = Count(Correlation > 0) / Total_Periods
```

### 6.3 Composite Line
```
CL(t) = A₁sin(2πf₁t + φ₁) + A₂sin(2πf₂t + φ₂) + A₃sin(2πf₃t + φ₃)

Сигналы:
- BUY:  все 3 цикла направлены вверх (производная > 0)
- SELL: все 3 цикла направлены вниз (производная < 0)
```

### 6.4 Decennial Patterns
```
DP(digit, day) = Average(NormalizedPrice) for years where year%10 == digit
```

### 6.5 COT Index (Futures)
```
COT_Index = (Current_Net - Min_N) / (Max_N - Min_N) × 100

Сигналы:
- COT_Index > 80: BULLISH (Commercials в покупках)
- COT_Index < 20: BEARISH (Commercials в продажах)
```

### 6.6 GBTC Index (Percentile Rank, НОВОЕ)
```
Index_t = #{τ ∈ W : P_τ < P_t} / |W| × 100

Сигналы (signal_direction = -1):
- GBTC_Index > 80: BEARISH (эйфория, институты продают)
- GBTC_Index < 20: BULLISH (паника, институты покупают)

Robust нормализация (Percentile Rank):
PR(X) = Count(x_i < X) / N × 100%
```

### 6.7 Signal Decay Function (НОВОЕ)
```
Effective_Strength = Initial_Strength × 0.5^(AgeDays / HalfLifeDays)
HalfLifeDays = 14 (по умолчанию)
```

### 6.8 Liquidity-Weighted Aggregation (НОВОЕ)
```
Index_final,t = Σ(w_i × Index_i,t) / Σw_i
где w_i = Volume_i × AUM_i
```

### 6.9 Bootstrap CI
```
Для n итераций (обычно 1000):
1. Семплировать returns с заменой
2. Рассчитать метрику
3. После n итераций взять 2.5% и 97.5% перцентили

CI_95% = [P_2.5, P_97.5]
```

### 6.10 Chow Test (Structural Break)
```
F = [(RSS_full - (RSS_1 + RSS_2)) / k] / [(RSS_1 + RSS_2) / (n - 2k)]

Где:
- RSS_full: RSS для всей выборки
- RSS_1, RSS_2: RSS для подвыборок до и после брейкпоинта
- k: количество параметров
- n: размер выборки

Если p-value < 0.05 → структурный сдвиг присутствует
```

---

## 7. КОД МОДУЛЕЙ (Go)

### 7.1 COT/GBTC Analyzer
```go
// internal/service/cot/analyzer.go

package cot

import (
    "math"
    "time"
)

// COTAnalyzer - анализатор COT/GBTC данных
type COTAnalyzer struct {
    config COTConfig
}

type COTConfig struct {
    WindowN             int       `json:"window_n"`              // 26 недель
    ExtremeHigh         float64   `json:"extreme_high"`          // 80
    ExtremeLow          float64   `json:"extreme_low"`           // 20
    SignalDirection     int       `json:"signal_direction"`      // 1 или -1
    RegimeChangeDate    *time.Time `json:"regime_change_date"`  // Для GBTC
    MinSignalDistance   int       `json:"min_signal_distance"`   // 21 день
    UsePercentileRank   bool      `json:"use_percentile_rank"`   // true для GBTC
}

// Analyze - анализ COT/GBTC данных
func (c *COTAnalyzer) Analyze(data []COTData, instrument Instrument) *COTResult {
    // Фильтрация по regime_change_date
    if instrument.RegimeChangeDate != nil {
        data = c.filterByRegime(data, *instrument.RegimeChangeDate)
    }
    
    // Расчёт индекса
    var indices []float64
    if c.config.UsePercentileRank {
        indices = c.calculatePercentileRank(data, instrument)
    } else {
        indices = c.calculateStandardIndex(data)
    }
    
    // Детекция экстремумов
    signals := c.detectExtremes(indices, data, instrument.SignalDirection)
    
    // Фильтр автокорреляции
    signals = c.applyAutocorrelationFilter(signals, instrument.MinSignalDistance)
    
    // Статистическая значимость
    for i := range signals {
        signals[i].PValue = c.calculatePValue(signals[i], data)
        signals[i].CI_Lower, signals[i].CI_Upper = c.calculateBootstrapCI(signals[i], data, 1000)
    }
    
    return &COTResult{
        Indices:      indices,
        Signals:      signals,
        LastSignal:   c.getLastSignal(signals),
    }
}

// calculatePercentileRank - Robust нормализация (НОВОЕ)
func (c *COTAnalyzer) calculatePercentileRank(data []COTData, instrument Instrument) []float64 {
    window := c.config.WindowN
    indices := make([]float64, len(data))
    
    for i := window; i < len(data); i++ {
        windowData := data[i-window : i]
        currentPremium := data[i].Premium
        
        // Percentile Rank: PR(X) = Count(x_i < X) / N × 100%
        count := 0
        for _, d := range windowData {
            if d.Premium < currentPremium {
                count++
            }
        }
        indices[i] = float64(count) / float64(len(windowData)) * 100
    }
    
    return indices
}

// applyAutocorrelationFilter - фильтр автокорреляции (НОВОЕ)
func (c *COTAnalyzer) applyAutocorrelationFilter(signals []Signal, minDistance int) []Signal {
    if len(signals) == 0 {
        return signals
    }
    
    var filtered []Signal
    lastSignalDate := time.Time{}
    
    for _, s := range signals {
        if lastSignalDate.IsZero() || s.ReportDate.Sub(lastSignalDate) >= time.Duration(minDistance)*24*time.Hour {
            filtered = append(filtered, s)
            lastSignalDate = s.ReportDate
        }
    }
    
    return filtered
}

// calculateBootstrapCI - Bootstrap доверительные интервалы (НОВОЕ)
func (c *COTAnalyzer) calculateBootstrapCI(signal Signal, data []COTData, iterations int) (lower, upper float64) {
    // Bootstrap с заменой
    returns := c.extractReturnsAroundSignal(signal, data, 21) // ±21 день
    
    bootstrapMeans := make([]float64, iterations)
    for i := 0; i < iterations; i++ {
        sample := c.resampleWithReplacement(returns)
        bootstrapMeans[i] = mean(sample)
    }
    
    // 95% CI
    sort.Float64s(bootstrapMeans)
    lower = bootstrapMeans[int(float64(iterations)*0.025)]
    upper = bootstrapMeans[int(float64(iterations)*0.975)]
    
    return lower, upper
}
```

### 7.2 Risk Management
```go
// internal/service/risk/manager.go

package risk

import (
    "math"
)

// RiskManager - управление рисками
type RiskManager struct {
    config RiskConfig
}

type RiskConfig struct {
    PerTradePercent  float64 `json:"per_trade_percent"`   // 0.02 (2%)
    MaxDrawdown      float64 `json:"max_drawdown"`        // 0.20 (20%)
    SignalHalfLife   int     `json:"signal_half_life"`    // 14 дней
    RiskFreeRate     float64 `json:"risk_free_rate"`      // 0.02
}

type Position struct {
    Size          float64   `json:"size"`
    Entry         float64   `json:"entry"`
    StopLoss      float64   `json:"stop_loss"`
    TakeProfit    float64   `json:"take_profit"`
    EffectiveStrength float64 `json:"effective_strength"`
    RiskAmount    float64   `json:"risk_amount"`
    IsRejected    bool      `json:"is_rejected"`
    RejectReason  string    `json:"reject_reason,omitempty"`
}

// CalculatePosition - расчёт размера позиции
func (r *RiskManager) CalculatePosition(signal Signal, account Account) Position {
    // Проверка Max Drawdown
    if account.CurrentDrawdown >= r.config.MaxDrawdown {
        return Position{IsRejected: true, RejectReason: "Max Drawdown exceeded"}
    }
    
    // Signal Decay
    effectiveStrength := signal.InitialStrength * math.Pow(0.5, float64(signal.AgeDays)/float64(r.config.SignalHalfLife))
    
    // Размер риска
    riskAmount := account.Balance * r.config.PerTradePercent * effectiveStrength
    
    // Stop-Loss расстояние
    stopDistance := math.Abs(signal.EntryPrice - signal.StopLoss)
    if stopDistance == 0 {
        return Position{IsRejected: true, RejectReason: "Invalid Stop-Loss"}
    }
    
    // Размер позиции
    positionSize := riskAmount / stopDistance
    
    return Position{
        Size:             positionSize,
        Entry:            signal.EntryPrice,
        StopLoss:         signal.StopLoss,
        TakeProfit:       signal.TakeProfit,
        EffectiveStrength: effectiveStrength,
        RiskAmount:       riskAmount,
        IsRejected:       false,
    }
}

// CalculateSharpe - расчёт Sharpe Ratio
func (r *RiskManager) CalculateSharpe(returns []float64) float64 {
    if len(returns) == 0 {
        return 0
    }
    
    meanRet := mean(returns)
    stdRet := stdDev(returns)
    
    if stdRet == 0 {
        return 0
    }
    
    return (meanRet - r.config.RiskFreeRate) / stdRet * math.Sqrt(252)
}
```

### 7.3 Backtest Engine
```go
// internal/service/backtest/engine.go

package backtest

import (
    "math"
    "time"
)

// BacktestEngine - движок бэктестинга
type BacktestEngine struct {
    config BacktestConfig
}

type BacktestConfig struct {
    Commission       float64 `json:"commission"`        // 0.001 (0.1%)
    Slippage        float64 `json:"slippage"`         // 0.0005 (0.05%)
    InSampleRatio   float64 `json:"in_sample_ratio"`  // 0.7
    BootstrapIter   int     `json:"bootstrap_iter"`   // 1000
}

type BacktestResult struct {
    TotalReturn      float64   `json:"total_return"`
    CAGR             float64   `json:"cagr"`
    SharpeRatio      float64   `json:"sharpe_ratio"`
    MaxDrawdown      float64   `json:"max_drawdown"`
    WinRate          float64   `json:"win_rate"`
    ProfitFactor     float64   `json:"profit_factor"`
    TotalTrades      int       `json:"total_trades"`
    
    // Статистика (НОВОЕ)
    PValue           float64   `json:"p_value"`
    BootstrapCILower float64   `json:"bootstrap_ci_lower"`
    BootstrapCIUpper float64   `json:"bootstrap_ci_upper"`
    
    EquityCurve      []float64 `json:"equity_curve"`
    Trades           []Trade   `json:"trades"`
}

// Run - запуск бэктеста
func (b *BacktestEngine) Run(prices []MarketData, strategy Strategy) *BacktestResult {
    // Разделение In-Sample / Out-of-Sample
    split := int(float64(len(prices)) * b.config.InSampleRatio)
    inSample := prices[:split]
    outSample := prices[split:]
    
    // Обучение стратегии на In-Sample
    strategy.Train(inSample)
    
    // Симуляция на Out-of-Sample
    var trades []Trade
    equity := []float64{10000} // Начальный капитал
    balance := 10000.0
    peak := balance
    
    for i := 1; i < len(outSample); i++ {
        signal := strategy.GenerateSignal(outSample[:i])
        
        if signal.Type != "" {
            trade := b.executeTrade(signal, outSample[i], balance)
            trades = append(trades, trade)
            balance += trade.Profit
        }
        
        equity = append(equity, balance)
        if balance > peak {
            peak = balance
        }
    }
    
    // Расчёт метрик
    result := &BacktestResult{
        TotalReturn: (balance - 10000) / 10000 * 100,
        EquityCurve: equity,
        Trades:      trades,
    }
    
    result.CAGR = b.calculateCAGR(equity, len(outSample))
    result.SharpeRatio = b.calculateSharpe(trades)
    result.MaxDrawdown = b.calculateMaxDrawdown(equity)
    result.WinRate = b.calculateWinRate(trades)
    result.ProfitFactor = b.calculateProfitFactor(trades)
    result.TotalTrades = len(trades)
    
    // Bootstrap CI (НОВОЕ)
    result.BootstrapCILower, result.BootstrapCIUpper, result.PValue = b.bootstrap(trades, b.config.BootstrapIter)
    
    return result
}

// bootstrap - расчёт доверительных интервалов через bootstrap
func (b *BacktestEngine) bootstrap(trades []Trade, iterations int) (lower, upper, pValue float64) {
    if len(trades) < 10 {
        return 0, 0, 1
    }
    
    returns := make([]float64, len(trades))
    for i, t := range trades {
        returns[i] = t.Profit / t.EntryPrice
    }
    
    // Bootstrap
    bootstrapMeans := make([]float64, iterations)
    for i := 0; i < iterations; i++ {
        sample := resampleWithReplacement(returns)
        bootstrapMeans[i] = mean(sample)
    }
    
    sort.Float64s(bootstrapMeans)
    
    // 95% CI
    lower = bootstrapMeans[int(float64(iterations)*0.025)]
    upper = bootstrapMeans[int(float64(iterations)*0.975)]
    
    // p-value (доля <= 0)
    count := 0
    for _, m := range bootstrapMeans {
        if m <= 0 {
            count++
        }
    }
    pValue = float64(count) / float64(iterations)
    
    return lower, upper, pValue
}
```

---

## 8. КОД МОДУЛЕЙ (Python)

### 8.1 QSpectrum с Burg's MEM
```python
# quant/qspectrum/analyzer.py

import numpy as np
from scipy import signal
from typing import List, Tuple

class QSpectrumAnalyzer:
    """QSpectrum - НЕ использует FFT!"""
    
    def __init__(self, min_period: int = 10, max_period: int = 200, 
                 use_mem: bool = True, mem_order: int = 50):
        self.min_period = min_period
        self.max_period = max_period
        self.use_mem = use_mem
        self.mem_order = mem_order
    
    def analyze(self, prices: np.ndarray) -> dict:
        """Главный метод анализа"""
        # Нормализация
        normalized = self._normalize(prices)
        
        # Циклическая корреляция (НЕ FFT!)
        spectrum = self._calculate_spectrum(normalized)
        
        # WFA устойчивости
        cycles = self._extract_cycles(spectrum, normalized)
        
        # Сортировка по энергии
        cycles.sort(key=lambda x: x['energy'], reverse=True)
        
        # Топ-3 цикла
        top3 = cycles[:3] if len(cycles) >= 3 else cycles
        
        return {
            'cycles': cycles,
            'top3': top3,
            'spectrum': spectrum
        }
    
    def _calculate_spectrum(self, data: np.ndarray) -> List[dict]:
        """Расчёт спектра циклической корреляции"""
        n = len(data)
        spectrum = []
        
        for period in range(self.min_period, min(self.max_period, n // 2)):
            # Циклическая корреляция
            correlation = self._cyclic_correlation(data, period)
            
            # Энергия
            energy = abs(correlation) * np.sqrt(n / period)
            
            if energy > 0.1:
                spectrum.append({
                    'period': period,
                    'correlation': correlation,
                    'energy': energy
                })
        
        return spectrum
    
    def _cyclic_correlation(self, data: np.ndarray, period: int) -> float:
        """Циклическая корреляция (автокорреляция с лагом)"""
        n = len(data)
        if period >= n:
            return 0.0
        
        sum_corr = np.sum(data[period:] * data[:-period])
        return sum_corr / (n - period)
    
    def burg_mem(self, data: np.ndarray, order: int) -> Tuple[np.ndarray, float]:
        """Burg's Method для МЭМ"""
        n = len(data)
        
        # Инициализация
        a = np.zeros(order + 1)
        a[0] = 1.0
        
        ef = data.copy()
        eb = data.copy()
        
        sigma2 = np.var(data)
        
        for m in range(1, order + 1):
            # Коэффициент отражения
            num = 2 * np.sum(ef[m:] * eb[:-m])
            den = np.sum(ef[m:]**2) + np.sum(eb[:-m]**2)
            
            if den == 0:
                break
            
            km = num / den
            
            # Обновление коэффициентов
            a_new = a.copy()
            for i in range((m // 2) + 1):
                a_new[i] = a[i] - km * a[m - i]
                a_new[m - i] = a[m - i] - km * a[i]
            a = a_new
            
            # Обновление ошибок
            ef_new = ef.copy()
            for i in range(m, n):
                ef_new[i] = ef[i] - km * eb[i - 1]
                eb[i] = eb[i - 1] - km * ef[i]
            ef = ef_new
            
            sigma2 *= (1 - km**2)
        
        return a[1:], sigma2
    
    def mem_spectrum(self, data: np.ndarray, freqs: np.ndarray) -> np.ndarray:
        """Спектральная плотность мощности по МЭМ"""
        a, sigma2 = self.burg_mem(data, self.mem_order)
        
        power = np.zeros(len(freqs))
        for i, f in enumerate(freqs):
            z = np.exp(-2j * np.pi * f * np.arange(1, len(a) + 1))
            denom = abs(1 + np.sum(a * z))**2
            power[i] = sigma2 / denom
        
        return power
```

### 8.2 Bootstrap CI
```python
# quant/bootstrap/calculator.py

import numpy as np
from typing import Tuple

class BootstrapCalculator:
    """Расчёт доверительных интервалов через Bootstrap"""
    
    def __init__(self, iterations: int = 1000, confidence: float = 0.95):
        self.iterations = iterations
        self.confidence = confidence
    
    def calculate_ci(self, returns: np.ndarray) -> Tuple[float, float, float]:
        """Расчёт CI и p-value"""
        n = len(returns)
        if n < 10:
            return 0.0, 0.0, 1.0
        
        # Bootstrap с заменой
        bootstrap_means = np.zeros(self.iterations)
        for i in range(self.iterations):
            sample = np.random.choice(returns, size=n, replace=True)
            bootstrap_means[i] = np.mean(sample)
        
        # Сортировка
        bootstrap_means.sort()
        
        # Перцентили
        alpha = (1 - self.confidence) / 2
        lower = bootstrap_means[int(self.iterations * alpha)]
        upper = bootstrap_means[int(self.iterations * (1 - alpha))]
        
        # p-value
        p_value = np.sum(bootstrap_means <= 0) / self.iterations
        
        return lower, upper, p_value
```

---

## 9. БЕЗОПАСНОСТЬ

### 9.1 Secrets Management
```
- API-ключи бирж → HashiCorp Vault
- DB credentials → Environment Variables (Docker Secrets)
- JWT keys → Rotated monthly
```

### 9.2 Audit Logging
```
- Все действия пользователей логируются
- Изменения конфигурации трекаются
- Доступ к API-ключам аудитится
```

---

## 10. ДЕПЛОЙ

### 10.1 Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: 
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8080:8080"
      - "9090:9090"
    depends_on:
      - postgres
      - redis
      - python-quant
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/cyclecast
      - REDIS_URL=redis://redis:6379
      - PYTHON_GRPC_URL=python-quant:50051

  python-quant:
    build:
      context: ./quant
      dockerfile: Dockerfile
    ports:
      - "50051:50051"

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=cyclecast
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redisdata:/data

  vault:
    image: hashicorp/vault:latest
    ports:
      - "8200:8200"

volumes:
  pgdata:
  redisdata:
```

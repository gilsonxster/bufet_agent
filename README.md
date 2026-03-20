# Bufet Agent

Bufet Agent is an advanced, multi-agent financial analysis system built on the **Google ADK** framework. It is designed to autonomously research a stock watchlist, evaluate algorithmic financial health metrics, synthesize opinions using legendary investor personas, and output a comprehensive master report grounded by real-time macroeconomic news.

## Architecture

The system utilizes a `SequentialAgent` pipeline to enforce a strict chain of thought, alongside a `ParallelAgent` panel to simulate debate and diverse insights. The execution flow is as follows:

1. **Researcher Agent**
2. **The Analyst Panel (Parallel Execution)**
3. **Head Portfolio Manager**
4. **Macro-Economic News Reviewer**

All agents share context via an `InMemorySessionService`, allowing each agent downstream to evaluate the full programmatic output and qualitative opinions of the agents upstream.

---

## Capabilities & Personas

### 1. The Researcher Agent
- **Description:** Scrapes deep financial data from `yfinance`.
- **Capabilities:** Extracts raw Balance Sheet, Cash Flow, and Financial Data. It programmatically maps factors like Net Income, CapEx, Long-Term Debt, Inventory Growth, and ROIC.

### 2. The Analyst Panel
A `ParallelAgent` that runs four distinct investing personas simultaneously to evaluate the raw numerical data:

* **Warren Buffett Analyst:** Evaluates the numbers based purely on value, economic moats, and financial durability (Return on Equity, margins, debt-to-equity).
* **Peter Lynch Analyst:** Evaluates the numbers specifically looking for Growth at a Reasonable Price (GARP). Focuses on PE reasonableness, earnings growth, and the PEG ratio.
* **Benjamin Graham Analyst:** Evaluates the numbers strictly searching for undervalued stocks with a high margin of safety (defensive balance sheets, current ratios).
* **The Legendary Investment Committee:** A hybrid intelligence that runs the `evaluate_stock_legendary` algorithm. It calculates Owner Earnings, the 3-Year Debt Rule, PEGY Ratios, and Inventory Lag checks to emit a strict programmatic Score out of 100 before writing its thesis.

### 3. The Head Portfolio Manager
- **Description:** The synthesizer.
- **Capabilities:** Digests the four separate output reports from the Analyst Panel. Based purely on overlapping consensus and the strength of the arguments, it selects exactly the **Top 5** best stocks from the watchlist and explains its reasoning.

### 4. Macro-Economic News Reviewer
- **Description:** Grounded news aggregator.
- **Capabilities:** Armed with Google Search tools, this agent queries real-time global macroeconomic data, geopolitical events, and specific news for the Top 5 chosen companies. It writes the final **BUFET AGENT MASTER ANALYSIS REPORT** merging fundamentals with real-world catalysts.

---

## Setup & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Set your Gemini API Key in your environment or a `.env` file in the root directory:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the Pipeline
```bash
python bufet_agent.py
```

> **Note on Quotas**: The Parallel Analyst Panel initiates four complex LLM queries simultaneously. If you are using a free-tier Gemini API Key, you may encounter `429 RESOURCE_EXHAUSTED` (15 Requests Per Minute limit). Ensure you space out your full pipeline executions.

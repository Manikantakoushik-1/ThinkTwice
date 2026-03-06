# ThinkTwice

🧠 **Self-Reflecting LLM Agent (Reflexion-Style)** — Attempt → Evaluate → Reflect → Retry using **FREE LLM APIs**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Real-World Showcase

See the reflexion loop tackle **real interview problems** — from LRU Cache implementations to
cascading-failure analysis and compound-growth calculations.

```bash
# Full showcase: 5 tasks across all categories
python showcase.py

# Quick demo (2 tasks)
python showcase.py --quick

# Focus on one category
python showcase.py --category algorithms
python showcase.py --category data_science
python showcase.py --category system_design
python showcase.py --category debugging
python showcase.py --category business

# Deeper reflection (5 attempts instead of 3)
python showcase.py --max-attempts 5

# Show full solutions
python showcase.py --verbose

# Standard 3-task demo
python main.py

# Jump straight to showcase from main.py
python main.py --showcase
```

Results are saved to `results/showcase_results.json` after each run.

---

## 📊 What Makes This Different

Most LLM demos run a problem once. ThinkTwice runs it in a **Baseline → Reflect → Retry** loop and
shows you exactly where (and why) reflection made the difference.

```
Baseline  (1 attempt)    ✗  incorrect  score=0.00
Reflexion (3 attempts)   ✓  CORRECT    score=1.00   🚀 Reflection loop FIXED this task!

  💡 Reflection insights:
    [1] Off-by-one in loop range — should iterate n-1 times not n
        → Strategy: Change range(n) to range(n-1) and return a directly
```

The showcase script prints a side-by-side comparison table at the end:

```
╭──────────────────────────────────────────────────────────╮
│  📊  Baseline vs Reflexion — Summary                     │
├──────────────────┬──────────────┬────────┬───────┬───────┤
│ Task             │ Category     │ Base   │ Refx  │ Impr? │
├──────────────────┼──────────────┼────────┼───────┼───────┤
│ rw_ds_002        │ 📊 Data Sci  │   ✗    │   ✓   │ 🚀 YES│
│ rw_algo_001      │ ⚡ Algorithm  │   ✗    │   ✓   │ 🚀 YES│
│ rw_sd_002        │ 🏗️  Sys Des  │   ✓    │   ✓   │  —    │
│ rw_dbg_001       │ 🐛 Debug     │   ✗    │   ✓   │ 🚀 YES│
│ rw_biz_001       │ 💼 Business  │   ✗    │   ✓   │ 🚀 YES│
╰──────────────────┴──────────────┴────────┴───────┴───────╯
```

---

## 🗂️ Real-World Task Categories

| Category | Task Type | Examples |
|----------|-----------|---------|
| **📊 Data Science** | `math` | A/B test analysis, runway calculations, storage sizing |
| **⚡ Algorithms** | `code` | LRU Cache, merge intervals, valid brackets |
| **🏗️ System Design** | `logic` | URL shortener design, cascading failures, feed architecture |
| **🐛 Debugging** | `code` | Off-by-one bugs, two-sum fix, in-place dedup |
| **💼 Business Math** | `math` | Compound interest, tax brackets, LTV:CAC ratio |

All tasks are in `src/tasks/real_world.py` and use the standard `Task` + `TaskLoader` interface.

---

## 🖥️ Web UI

Launch the interactive Streamlit dashboard to demo ThinkTwice visually:

```bash
# Install dependencies (includes streamlit & plotly)
pip install -r requirements.txt

# Run the dashboard
streamlit run ui/app.py
```

The dashboard opens at `http://localhost:8501` and offers three pages:

| Page | Description |
|------|-------------|
| **🏠 Interactive Solver** | Enter a task, watch the Reflexion loop step-by-step (Attempt → Evaluate → Reflect → Retry) |
| **📊 Benchmark Dashboard** | Compare Baseline (1 attempt) vs Reflexion across task sets with charts |
| **🏗️ Architecture** | Visual explanation of every component and the Reflexion paper reference |

Enter your API key in the sidebar (Gemini / Groq / HuggingFace), select max attempts, and solve any built-in or custom task.

---

## Architecture

```
Task Input
    │
    ▼
┌─────────┐     ┌─────────────┐     ┌────────────┐
│  Actor  │────▶│  Evaluator  │────▶│  Correct?  │──YES──▶ ✓ Done
│(generate│     │(check answer│     └────────────┘
│solution)│     │  / run code)│           │ NO
└─────────┘     └─────────────┘           │
     ▲                                    ▼
     │                           ┌─────────────────┐
     │                           │    Reflector    │
     │                           │(analyze failure)│
     │                           └────────┬────────┘
     │                                    │
     │                           ┌────────▼────────┐
     └───────────────────────────│ Episodic Memory │
          (inject reflections)   │(store insights) │
                                 └─────────────────┘
                   (repeat up to N attempts)
```

## Components

| Component | Role | File |
|-----------|------|------|
| **Actor** | Generates solutions using an LLM | `src/agent/actor.py` |
| **Evaluator** | Checks correctness (exact match / code execution / LLM-as-judge) | `src/agent/evaluator.py` |
| **Reflector** | Analyzes failures and extracts actionable insights | `src/agent/reflector.py` |
| **EpisodicMemory** | Stores reflections across attempts | `src/memory/episodic_memory.py` |
| **ReflexionAgent** | Orchestrates the full loop | `src/agent/reflexion_agent.py` |
| **LLMClient** | Unified multi-provider LLM client | `src/utils/llm_client.py` |

---

## Free API Setup

You need **at least one** of the following free API keys:

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| **Google Gemini** | 1,500 req/day · 1M tokens/min | https://aistudio.google.com/apikey |
| **Groq** | 14,400 req/day | https://console.groq.com/keys |
| **HuggingFace** | 1,000 req/day | https://huggingface.co/settings/tokens |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Manikantakoushik-1/ThinkTwice.git
cd ThinkTwice

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your key, e.g.:
# GEMINI_API_KEY=your_key_here

# 4. Run the demo
python main.py
```

---

## Running Experiments

```bash
# Math reasoning (GSM8K-style)
python experiments/run_gsm8k.py

# Code generation (HumanEval-style)
python experiments/run_humaneval.py

# Logic puzzles
python experiments/run_logic.py

# Planning tasks
python experiments/run_planning.py

# Analyze all results
python experiments/analyze_results.py
```

---

## Task Types

| Type | Description | Evaluation |
|------|-------------|------------|
| **math** | GSM8K-style word problems + business maths | Exact numeric match |
| **code** | HumanEval-style + interview coding problems | Code execution + test assertions |
| **logic** | Classic constraint puzzles + system design | LLM-as-judge |
| **planning** | Open-ended system design | LLM-as-judge |

---

## Project Structure

```
ThinkTwice/
├── main.py                      # Quick demo script (--showcase flag)
├── showcase.py                  # Real-world showcase demo ← NEW
├── requirements.txt
├── setup.py
├── .env.example                 # API key template
├── src/
│   ├── agent/
│   │   ├── actor.py             # LLM solution generator
│   │   ├── evaluator.py         # Correctness checker
│   │   ├── reflector.py         # Self-reflection engine
│   │   └── reflexion_agent.py   # Main orchestrator
│   ├── memory/
│   │   └── episodic_memory.py   # Reflection storage
│   ├── tasks/
│   │   ├── base_task.py
│   │   ├── math_reasoning.py    # GSM8K-style (10 tasks)
│   │   ├── code_generation.py   # HumanEval-style (7 tasks)
│   │   ├── logic_puzzles.py
│   │   ├── planning.py
│   │   └── real_world.py        # Real-world tasks (5 categories) ← NEW
│   └── utils/
│       ├── llm_client.py        # Multi-provider LLM client
│       └── logger.py
├── tests/                       # Unit & integration tests
├── experiments/                 # Benchmark scripts
└── results/                     # Experiment output (git-ignored)
```

---

## How It Works

ThinkTwice implements the **Reflexion** pattern from [Shinn et al. (2023)](https://arxiv.org/abs/2303.11366):

1. **Attempt** — The *Actor* generates a solution to the task using the LLM.
2. **Evaluate** — The *Evaluator* checks correctness (numeric match, code execution, or LLM-as-judge).
3. **Reflect** — On failure, the *Reflector* asks the LLM: *"What went wrong and how to fix it?"*
4. **Remember** — The structured reflection is stored in *EpisodicMemory*.
5. **Retry** — The Actor tries again, this time with the reflection injected into its prompt.

This loop repeats up to `max_attempts` times.

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## License

MIT — see [LICENSE](LICENSE).

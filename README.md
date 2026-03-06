# ThinkTwice

🧠 **Self-Reflecting LLM Agent (Reflexion-Style)** — Attempt → Evaluate → Reflect → Retry using **FREE LLM APIs**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
| **math** | GSM8K-style word problems | Exact numeric match |
| **code** | HumanEval-style Python functions | Code execution + test assertions |
| **logic** | Classic constraint puzzles | LLM-as-judge |
| **planning** | Open-ended system design | LLM-as-judge |

---

## Project Structure

```
ThinkTwice/
├── main.py                      # Quick demo script
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
│   │   ├── math_reasoning.py
│   │   ├── code_generation.py
│   │   ├── logic_puzzles.py
│   │   └── planning.py
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

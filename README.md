# Edge LLM Jetson Lab

Practical LLM/VLM applications running on **Jetson Orin NX 8GB** using `llama.cpp`

---

## 🎯 Goal

This repository explores what is *realistically achievable* with **LLMs on constrained edge devices**, specifically:

- **Jetson Orin NX 8GB (primary target)**
- Fully local inference (no cloud dependency)
- Multi-app coexistence (LLM + automation + video pipelines)
- System-level optimization under tight memory limits

---

## 🧠 Why 8GB Matters

Most LLM demos assume abundant GPU memory.  
This repo focuses on the opposite:

> **What can you actually run on a "good enough" edge device?**

Key challenges:
- Limited unified memory (8GB shared CPU/GPU)
- KV cache constraints
- Model quantization tradeoffs
- Concurrent workloads (LLM + CV + services)

---

## ⚙️ System Setup

**Hardware**
- Jetson Orin NX 8GB

**Core Stack**
- [`llama.cpp`](https://github.com/ggerganov/llama.cpp)
- Mistral 7B (Q4_K_M or similar quantized models)
- Python (venv-based apps)
- Optional: Docker

---

## 📊 What Works on 8GB (Guidelines)

| Component | Recommended |
|----------|------------|
| Model | Mistral 7B Q4_K_M |
| Context Size | 512–1024 |
| GPU Layers | Tune (~20–30 depending on workload) |
| Concurrency | 1 active LLM task |
| Swap | Optional (use carefully) |

> These are practical starting points — tuning is part of the goal of this repo.

---

## 🧩 Projects

### 1. `news-digest-llm`
> Daily autonomous agent: fetch → summarize → email

- Pulls RSS/news feeds
- Uses local LLM for summarization
- Sends daily digest via email
- Runs via cron

👉 Demonstrates:
- Long-running automation
- Prompt design for summarization
- Low-frequency batch inference

---

### (Planned / In Progress)

#### `rtsp-llm-agent`
- RTSP stream → event → LLM summary  
- Edge video intelligence pipeline

#### `local-rag`
- Query local logs / documents using LLM  
- Lightweight retrieval without heavy infra

#### `vision-language-agent`
- CLIP / embeddings + LLM reasoning  
- Semantic understanding of scenes

---

## 📁 Repository Structure
```
edge-llm-jetson/
│
├── news-digest-llm/
├── rtsp-llm-agent/ (planned)
├── local-rag/ (planned)
│
├── shared/ # reusable modules (planned)
├── docs/
└── README.md
```


---

## 🚀 Getting Started (Example)

```bash
git clone https://github.com/<your-username>/edge-llm-jetson.git
cd edge-llm-jetson/news-digest-llm

bash setup.sh
```

---

## 🔧 Optimization Focus Areas

This repo is not just about running models — it's about pushing limits:

- GPU layer offloading (-ngl)
- Memory footprint tuning
- Prompt efficiency
- Throughput vs latency tradeoffs
- Multi-process contention

---

## 🧪 Philosophy
- Start simple → iterate fast
- Measure everything (latency, memory, stability)
- Prefer practical systems over benchmarks
- Design for real edge deployment, not demos

---

## 📌 Future Directions
- Multi-agent workflows on edge
- LLM + VLM hybrid pipelines
- Integration with VMS (e.g., Frigate / Nx)
- RAG + video metadata search
- Systemd-based orchestration (replace cron)

---

🤝 Contributions

Ideas, optimizations, and new edge use cases are welcome.


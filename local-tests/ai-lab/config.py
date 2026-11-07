"""ai-lab configuration: model table, pricing, research caps.

Pricing source: GET /v1/models on 2026-11-07 (prompt/completion $/M tokens).
Re-fetch before a new campaign; never assume prices are stable.
Local Ollama models cost $0 by definition (own hardware, own power).
"""

BASE_URL = "https://api.vultrinference.com/v1"

# Research budget (defaults; overridable per campaign, never raisable
# silently — any raise must be a committed config change + report note).
BUDGET_USD = 10.0
MAX_REQUESTS = 200
MAX_CONCURRENT = 1  # sequential until parallel accounting is proven
MAX_RETRIES = 2  # transient 429/5xx only; never retry 401/400
DEFAULT_MAX_OUT = 1536
DEFAULT_TIMEOUT_S = 180

MODELS = {
    # Vultr Serverless Inference (paid; ledger-gated)
    "glm-5.3": {"provider": "vultr", "in_per_m": 0.75, "out_per_m": 3.00,
                "ctx": 1048576, "role": "flagship reasoner"},
    "deepseek-v4.1-flash-1017": {"provider": "vultr", "in_per_m": 0.15,
                                 "out_per_m": 0.60, "ctx": 1048576,
                                 "role": "efficient reasoner"},
    "mimo-v2.6-flash": {"provider": "vultr", "in_per_m": 0.10,
                        "out_per_m": 0.25, "ctx": 1048576,
                        "role": "cheap fast baseline"},
    "muse-glimmer-30b": {"provider": "vultr", "in_per_m": 0.25,
                         "out_per_m": 1.00, "ctx": 131072,
                         "role": "dense-30B diversity"},
    # Local Ollama (free; daemon must be running)
    "qwythos-9b-abliterated:optimized": {"provider": "ollama",
                                         "in_per_m": 0.0, "out_per_m": 0.0,
                                         "ctx": 8192, "role": "v4 9B repeat"},
    "qwen2.5-coder-14b-opt:latest": {"provider": "ollama", "in_per_m": 0.0,
                                     "out_per_m": 0.0, "ctx": 8192,
                                     "role": "v4 14B repeat"},
}

VERDICTS = ("DOCUMENTARY BLOCKER IDENTIFIED",
            "NO DOCUMENTARY BLOCKER FOUND IN REVIEWED SOURCES",
            "INSUFFICIENT EVIDENCE")

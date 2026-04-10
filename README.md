
# SOC Security Environment for OpenEnv

A reinforcement learning environment where an AI agent acts as a Tier-1 SOC analyst. The agent receives security alerts (phishing, brute force, malware) and chooses mitigation actions while balancing security vs. business disruption.

## Concept

The environment simulates a Security Operations Center (SOC). The agent observes an alert and outputs a discrete action. The environment returns a reward that encourages correct, fast, and minimally disruptive responses.

## Observation Space

A dictionary with these keys (from the `SecurityAlert` model):

| Key | Type | Description |
|-----|------|-------------|
| `current_alert.severity` | int (0-4) | 0=info,1=low,2=medium,3=high,4=critical |
| `current_alert.rule_name` | str | Alert rule name (e.g., "PsExec Remote Execution") |
| `current_alert.description` | str | Human-readable description |
| `current_alert.source_ip` | str | Source IP address (or empty) |
| `current_alert.dest_ip` | str | Destination IP address (or empty) |
| `compromise_level` | float (0.0–1.0) | How compromised the environment is |
| `step_count` | int | Number of steps taken so far |

## Action Space

Discrete integer actions (0–3):

| Action | Value | Use case |
|--------|-------|----------|
| `ALLOW` | 0 | Ignore alert (false positive or low risk) |
| `BLOCK_IP` | 1 | Block source IP at firewall |
| `ISOLATE_HOST` | 2 | Quarantine the affected host |
| `ESCALATE` | 3 | Send to Tier-2 analyst for review |

## Tasks (Difficulty Levels)

The environment supports three pre-defined tasks via the `task_id` parameter:

| Task ID | Name | Difficulty | Description | Recommended action |
|---------|------|------------|-------------|---------------------|
| `tier1` | Phishing triage | Easy | Suspicious email link, outbound to malicious IP | `BLOCK_IP` or `ESCALATE` |
| `tier2` | Lateral movement | Medium | PsExec remote execution, new service creation | `ISOLATE_HOST` or `ESCALATE` |
| `tier3` | Ransomware | Hard | PowerShell encoded command, file extension changes, ransom note | `ISOLATE_HOST` immediately |

## Reward Design

The reward function is opinionated to prioritize correct containment while penalizing business interruption:

| Event | Reward |
|-------|--------|
| Correctly blocking a malicious IP | +10 |
| Isolating a compromised host | +15 |
| Escalating a critical alert | +5 |
| Blocking low‑severity alert | -2 (business interruption) |
| Ignoring a high‑severity alert | -30 |
| Ignoring a critical alert | -50 + compromise increase |
| Allowing malware (critical mistake) | -100 and episode ends |
| Compromise level reaches 1.0 | -200 and episode ends |
| Episode completed safely | +20 (implicit in final score) |

Final episode scores are evaluated by the `grader.py` module, which also applies safety/availability penalties.

## LLM Agent Integration

The project includes `inference.py`, which uses the OpenAI client to call a **Llama-3** model (or any OpenAI‑compatible endpoint). The agent acts as a Tier-1 SOC analyst, receiving alerts and outputting JSON actions.

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLAMA_API_KEY` | API key for the LLM endpoint | `sk-...` |
| `LLAMA_BASE_URL` | Base URL of the OpenAI‑compatible endpoint | `http://localhost:8000/v1` |

If not set, the script will use dummy values and fail – you must provide a valid endpoint.

### Running with a Local Llama Server

One easy way is to use [Ollama](https://ollama.com/):

ollama pull llama3
ollama serve

Then set:

export LLAMA_API_KEY="ollama"
export LLAMA_BASE_URL="http://localhost:11434/v1"

Installation

git clone <your-repo>
cd soc_security_env
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

Usage

Run the agent on a specific task

export LLAMA_API_KEY=your_key
export LLAMA_BASE_URL=http://your-llm-server:8000/v1
python inference.py tier1   # or tier2, tier3


Run the environment manually (no LLM)

from environment import SOCEnv
env = SOCEnv(task_id="tier1", seed=42)
obs, info = env.reset()
action = 1  # BLOCK_IP
obs, reward, terminated, truncated, info = env.step(action)

Evaluate a run


from tasks import get_task_alerts
from grader import evaluate_run

alerts = get_task_alerts("tier1")
actions = [1, 3]  # example actions
result = evaluate_run(alerts, actions)
print(result["score"])

Docker

A Dockerfile is provided for deployment (e.g., on Hugging Face Spaces). It uses a non‑root user and installs dependencies.

Build and run:


docker build -t soc-env .
docker run -e LLAMA_API_KEY=your_key -e LLAMA_BASE_URL=your_url soc-env

Project Structure

├── environment.py   # Gymnasium environment
├── models.py        # Pydantic models (SecurityAlert, ProcessTree)
├── tasks.py         # Alert generation for three difficulty tiers
├── grader.py        # Final scoring logic (safety vs availability)
├── inference.py     # LLM agent loop (OpenAI client + Llama-3)
├── openenv.yaml     # OpenEnv specification
├── Dockerfile       # Container definition
├── requirements.txt # Python dependencies
└── README.md        # This file

License

MIT

# SOC Security Environment for RL

A professional, production-ready reinforcement learning environment where an AI agent acts as a **Tier-1 SOC analyst**. The agent processes security alerts (phishing, brute force, malware) and chooses actions to mitigate threats while minimizing business disruption.

## Concept

The environment simulates a Security Operations Center (SOC) where an analyst must triage alerts. The agent receives an **observation** (alert details) and outputs a **discrete action**. The environment returns a **reward** that balances:
- Correct threat mitigation
- Speed (low latency)
- Business disruption (unnecessary aggressive actions)

## Observation Space

A dictionary with the following keys (from the Pydantic `Alert` model):

| Key     | Type   | Description                          |
|---------|--------|--------------------------------------|
| `id`    | string | Unique alert ID                      |
| `srcIP` | string | Source IP address                    |
| `typ`   | string | Threat type (phishing, brute_force, malware_execution) |
| `sev`   | int    | Severity (1–10, 10=most severe)      |
| `ts`    | string | ISO timestamp of detection           |

## Action Space

Discrete actions (0–4):

| Action | Meaning               | Typical use                     |
|--------|-----------------------|----------------------------------|
| 0      | ALLOW                 | False positive, ignore           |
| 1      | INVESTIGATE           | Gather more data                 |
| 2      | ISOLATE_HOST          | Disconnect host from network     |
| 3      | BLOCK_IP              | Block source IP at firewall      |
| 4      | REVOKE_CREDENTIALS    | Invalidate user credentials      |

## Task Difficulty Levels

The environment supports three pre‑defined tasks (set via `task` parameter in `SOCEnv` or `SOC_TASK_ID` env var):

| Task ID | Name                | Difficulty | Description                                      | Expected Action |
|---------|---------------------|------------|--------------------------------------------------|------------------|
| 1       | Phishing Triage     | Easy       | Low‑severity phishing email from internal user  | INVESTIGATE (1)  |
| 2       | Brute Force Block   | Medium     | High‑severity brute force from malicious IP     | BLOCK_IP (3)     |
| 3       | Malware Containment | Hard       | Malware execution detected – must contain       | ISOLATE_HOST (2) |

## Reward Design

The reward is **opinionated** to encourage correct, fast, and minimally disruptive actions:

| Event                                        | Reward |
|----------------------------------------------|--------|
| Correct action                               | +10    |
| Incorrect action                             | -5     |
| False negative (ignore severity ≥7)          | -15    |
| Ignoring malware (ALLOW)                     | -50    |
| Unnecessary aggressive action (isolate/block) | -3     |
| Latency penalty (per step)                   | -0.5   |
| Action fatigue (same action 3× in a row)     | -5     |
| Episode resolved safely                      | +20    |
| System compromised                           | -40    |
| Resolution after compromise                  | -30    |

Final scores are clamped between -100 and 100.

## Installation

```bash
git clone <repo>
cd cybersecurity-soc-openenv
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
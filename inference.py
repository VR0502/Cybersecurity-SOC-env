#!/usr/bin/env python3
import os
import json
from openai import OpenAI
from environment import SOCEnv
from grader import grade

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")

MAX_STEPS = 10
TEMPERATURE = 0.0
MAX_TOKENS = 10

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    err = error if error else "null"
    done_str = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={err}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_prompt(obs):
    sys = "You are a SOC analyst. Choose one action: 0=ALLOW,1=INVESTIGATE,2=ISOLATE_HOST,3=BLOCK_IP,4=REVOKE_CREDENTIALS. Output only the number."
    usr = f"Alert: {json.dumps(obs)}"
    return sys, usr

def parse_action(txt):
    txt = txt.strip()
    for ch in txt:
        if ch.isdigit():
            return int(ch)
    return 0

def run_episode(env, client, task_name, benchmark):
    obs, _ = env.reset()
    log_start(task_name, benchmark, MODEL_NAME)
    done = False
    step = 0
    actions = []
    rewards_list = []
    total_reward = 0.0
    error = None
    try:
        while not done and step < MAX_STEPS:
            step += 1
            sys_p, usr_p = build_prompt(obs)
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role":"system","content":sys_p},{"role":"user","content":usr_p}],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            action_str = resp.choices[0].message.content
            action = parse_action(action_str)
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
            rewards_list.append(reward)
            actions.append(action)
            log_step(step, str(action), reward, done, error)
            if truncated:
                done = True
                break
    except Exception as e:
        error = str(e)
        log_step(step, "error", 0.0, True, error)
    result = grade(actions, env.alertsHist, rewards_list, info, env.task)
    score = result["score"]
    success = score >= 0.5
    log_end(success, step, score, rewards_list)
    return score

def main():
    if not HF_TOKEN:
        print("Warning: HF_TOKEN not set", flush=True)
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    benchmark = "soc_security_env"
    tasks = [1,2,3]
    for tid in tasks:
        env = SOCEnv(task=tid, maxSteps=MAX_STEPS)
        task_name = {1:"phish_triage",2:"brute_block",3:"malware_contain"}[tid]
        score = run_episode(env, client, task_name, benchmark)
        print(f"Task {tid} final score: {score:.3f}", flush=True)

if __name__ == "__main__":
    main()
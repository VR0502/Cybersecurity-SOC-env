#!/usr/bin/env python3
from environment import SOCEnv

def test(task_id):
    env = SOCEnv(task=task_id, maxSteps=5)
    obs, _ = env.reset()
    print(f"Task {task_id} initial observation: {obs}")
    for i in range(5):
        act = input(f"Step {i+1} action (0-4): ")
        if not act: act = "0"
        obs, rew, done, trunc, info = env.step(int(act))
        print(f"  -> reward={rew:.2f}, done={done}, info={info}")
        if done or trunc:
            break
    print(f"Final state: {env.state()}")

if __name__ == "__main__":
    import sys
    tid = int(sys.argv[1]) if len(sys.argv)>1 else 1
    test(tid)
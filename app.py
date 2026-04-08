from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from environment import SOCEnv
import json

app = FastAPI()
env = None

class StepRequest(BaseModel):
    action: int

class ResetResponse(BaseModel):
    observation: dict
    info: dict

class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool
    info: dict

class StateResponse(BaseModel):
    state: dict

@app.on_event("startup")
def startup():
    global env
    env = SOCEnv(task=1, maxSteps=10)

@app.post("/reset")
def reset():
    global env
    obs, info = env.reset()
    return ResetResponse(observation=obs, info=info)

@app.post("/step")
def step(req: StepRequest):
    global env
    obs, reward, done, _, info = env.step(req.action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/state")
def state():
    return StateResponse(state=env.state())

@app.get("/")
def root():
    return {"message": "SOC Environment Server is running"}
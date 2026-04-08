import gymnasium as gym
import numpy as np
from gymnasium import spaces
from models import Alert, ThreatType, Observation, Action, Reward
from alerts import ALERT_SCENARIOS

class SOCEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, task=1, maxSteps=10, seed=None):
        super().__init__()
        self.task = task
        self.maxSteps = maxSteps
        if seed:
            np.random.seed(seed)
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Dict({
            "id": spaces.Text(36),
            "srcIP": spaces.Text(15),
            "typ": spaces.Text(20),
            "sev": spaces.Discrete(11, start=1),
            "ts": spaces.Text(32)
        })
        self.alert = None
        self.owned = False
        self.infect = 0.0
        self.stepCnt = 0
        self.acts = []
        self.alertsHist = []
        self._loadAlert()

    def _loadAlert(self):
        if self.task == 1:
            alert_data = ALERT_SCENARIOS["phishing_low"]
        elif self.task == 2:
            alert_data = ALERT_SCENARIOS["brute_force_high"]
        else:
            alert_data = ALERT_SCENARIOS["malware_critical"]
        self.alert = Alert(**alert_data)
        self.alertsHist.append(self.alert)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.owned = False
        self.infect = 0.0
        self.stepCnt = 0
        self.acts = []
        self.alertsHist = []
        self._loadAlert()
        obs = self._getObs()
        return obs, {"task": self.task}

    def _getObs(self):
        a = self.alert
        return {
            "id": a.id,
            "srcIP": a.srcIP,
            "typ": a.typ.value,
            "sev": a.sev,
            "ts": a.ts.isoformat()
        }

    def step(self, act):
        self.stepCnt += 1
        self.acts.append(act)
        rew = 0.0
        done = False
        trunc = self.stepCnt >= self.maxSteps
        a = self.alert

        if a.typ == ThreatType.MALWARE and act == 0:
            rew -= 50.0
            self.owned = True
            self.infect = 1.0
        elif self._correct(act):
            rew += 10.0
        else:
            rew -= 5.0
            if act == 0 and a.sev >= 7:
                rew -= 15.0

        if act in [2,3,4] and not self._correct(act):
            rew -= 3.0

        rew -= 0.5 * self.stepCnt

        if a.typ == ThreatType.MALWARE and act == 0:
            self.infect = min(1.0, self.infect + 0.4)

        if not done and not trunc:
            nxt = self._nextAlert(act)
            if nxt is None:
                done = True
                if not self.owned:
                    rew += 20.0
                else:
                    rew -= 30.0
            else:
                self.alert = nxt
                self.alertsHist.append(self.alert)

        if self.owned or self.infect >= 0.8:
            done = True
            rew -= 40.0

        if len(self.acts) >= 3:
            if self.acts[-1] == self.acts[-2] == self.acts[-3]:
                rew -= 5.0

        info = {"infect": self.infect, "owned": self.owned, "steps": self.stepCnt}
        obs = self._getObs()
        return obs, rew, done, trunc, info

    def _correct(self, act):
        a = self.alert
        if a.typ == ThreatType.PHISHING:
            return act == 1
        if a.typ == ThreatType.BRUTE_FORCE:
            return act == 3
        if a.typ == ThreatType.MALWARE:
            return act in [2,3]
        if a.sev >= 7:
            return act in [1,2,3]
        return act == 0

    def _nextAlert(self, act):
        if self._correct(act):
            return None
        if self.alert.typ == ThreatType.MALWARE and act == 0 and not self.owned:
            return Alert(srcIP=self.alert.srcIP, typ=ThreatType.BRUTE_FORCE, sev=10)
        new_sev = min(10, self.alert.sev + 2)
        return Alert(srcIP=self.alert.srcIP, typ=self.alert.typ, sev=new_sev)

    def state(self):
        return {
            "alert": self.alert.dict() if self.alert else None,
            "owned": self.owned,
            "infect": self.infect,
            "step": self.stepCnt
        }
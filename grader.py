def grade(acts, alerts, rewards, info, tid):
    exp = {1:1,2:3,3:2}.get(tid,0)
    raw = sum(rewards)
    fn = 0.0
    for i, al in enumerate(alerts):
        if al.sev >= 7:
            if i < len(acts) and acts[i] == 0:
                fn += 15.0
    fat = 0.0
    if len(acts) >= 3:
        if acts[-1] == acts[-2] == acts[-3]:
            fat = 8.0
    match = False
    if acts:
        if acts[-1] == exp:
            match = True
        else:
            fat += 5.0
    compPen = 40.0 if info.get("owned", False) else 0.0
    final = raw - fn - fat - compPen
    final = max(-100.0, min(100.0, final))
    score = (final + 100.0) / 200.0
    return {"score": score, "raw": raw, "fn_pen": fn, "fatigue": fat, "comp_pen": compPen, "match": match}
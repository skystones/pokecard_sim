def compare_scores(a,b,epsilon: float=1e-9):
    if abs(a[0]-b[0])>epsilon: return 1 if a[0]>b[0] else -1
    if abs(a[1]-b[1])<=epsilon: return 0
    return 1 if a[1]>b[1] else -1

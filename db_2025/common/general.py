from datetime import datetime


def ts() -> float:
    return datetime.now().timestamp()


def duration(st: float) -> str:
    return f'{ts() - st:.3f}s'

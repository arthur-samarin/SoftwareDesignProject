from typing import List


def group_by_k(k: int, l: List):
    return [l[i:i + k] for i in range(0, len(l), k)]

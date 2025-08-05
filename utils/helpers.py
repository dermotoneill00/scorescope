
import hashlib
from typing import Dict, Tuple

def get_score_color_class(score: int) -> str:
    if score >= 8:
        return "score-excellent"
    elif score >= 6:
        return "score-good"
    elif score >= 4:
        return "score-average"
    else:
        return "score-poor"

def calculate_weighted_score(scores: Dict[str, Tuple[int, str]], weights: Dict[str, int]) -> float:
    total_weighted = sum(scores[cat][0] * weights[cat] for cat in weights.keys())
    total_weights = sum(weights.values())
    return round(total_weighted / total_weights, 2)

def get_file_hash(uploaded_file) -> str:
    return hashlib.md5(uploaded_file.getvalue()).hexdigest()

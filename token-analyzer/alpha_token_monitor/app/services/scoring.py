def alert_level_from_score(score: float) -> str:
    if score >= 85:
        return "P0"
    if score >= 70:
        return "P1"
    if score >= 50:
        return "P2"
    if score >= 30:
        return "P3"
    return "LOW"


def score_wallet_receive_signal(
    watch_address_confidence: float = 0,
    is_new_token: bool = False,
    is_first_seen_for_address: bool = False,
    direction: str = "in",
) -> tuple[float, float]:
    importance = 0
    confidence = float(watch_address_confidence or 0)

    if direction == "in":
        importance += 40

    if is_first_seen_for_address:
        importance += 20

    if is_new_token:
        importance += 20

    if confidence >= 80:
        importance += 15
    elif confidence >= 60:
        importance += 10
    elif confidence >= 40:
        importance += 5

    confidence = min(100, confidence + (20 if is_first_seen_for_address else 0))

    return min(100, importance), min(100, confidence)

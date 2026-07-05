def calculate_risk_score(
    voice_similarity,
    antispoof_score,
    liveness_score,
    scam_patterns,
):
    risk = 0

    risk += (1 - voice_similarity) * 0.30
    risk += antispoof_score * 0.30
    risk += (1 - liveness_score) * 0.20
    risk += min(scam_patterns * 0.10, 0.20)

    return round(min(risk, 1.0), 2)


def make_decision(risk_score):
    if risk_score < 0.35:
        return "ALLOW"

    elif risk_score < 0.70:
        return "REVIEW"

    return "BLOCK"

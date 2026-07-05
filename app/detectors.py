from typing import Dict, Any, List


def analyze_voice_similarity(
    similarity_score: float,
    call_duration: int = None,
    noise_level: float = None
) -> Dict[str, Any]:
    score = similarity_score
    
    if call_duration is not None:
        if call_duration < 30:
            score *= 0.95
    
    if noise_level is not None:
        if noise_level > 0.7:
            score *= 0.90
    
    final_score = round(min(max(score, 0.0), 1.0), 2)
    
    if final_score >= 0.8:
        explanation = "High voice similarity - voice matches the expected pattern"
    elif final_score >= 0.5:
        explanation = "Moderate voice similarity - some deviations detected"
    elif final_score >= 0.3:
        explanation = "Low voice similarity - significant differences from pattern"
    else:
        explanation = "Very low voice similarity - voice does not match expected pattern"
    
    if noise_level is not None and noise_level > 0.7:
        explanation += " (high background noise affects analysis)"
    
    return {
        "score": final_score,
        "explanation": explanation,
        "raw_similarity": similarity_score
    }


def detect_spoofing(
    antispoof_score: float,
    voice_similarity: float = None,
    call_duration: int = None
) -> Dict[str, Any]:
    score = antispoof_score
    
    if voice_similarity is not None:
        if voice_similarity < 0.4:
            score = min(score * 1.2, 1.0)
        elif voice_similarity > 0.8:
            score = score * 0.9
    
    if call_duration is not None and call_duration < 20:
        score = min(score * 1.1, 1.0)
    
    final_score = round(min(max(score, 0.0), 1.0), 2)
    
    if final_score > 0.7:
        explanation = "High spoofing risk detected - voice may be synthetically generated"
    elif final_score > 0.4:
        explanation = "Moderate spoofing risk - further verification recommended"
    elif final_score > 0.2:
        explanation = "Low spoofing risk - voice appears authentic"
    else:
        explanation = "Very low spoofing risk - no synthetic voice indicators"
    
    if voice_similarity is not None and voice_similarity < 0.4:
        explanation += " (low voice similarity increases spoofing suspicion)"
    
    return {
        "score": final_score,
        "explanation": explanation,
        "raw_antispoof": antispoof_score
    }


def evaluate_liveness(
    liveness_score: float,
    call_duration: int = None,
    noise_level: float = None
) -> Dict[str, Any]:
    score = 1.0 - liveness_score
    
    if call_duration is not None:
        if call_duration > 120:
            score *= 0.95
        elif call_duration < 30:
            score = min(score * 1.1, 1.0)
    
    if noise_level is not None:
        if noise_level > 0.8:
            score = min(score * 1.15, 1.0)
    
    final_score = round(min(max(score, 0.0), 1.0), 2)
    
    if final_score > 0.7:
        explanation = "Low liveness score - caller may not be a live person"
    elif final_score > 0.4:
        explanation = "Moderate liveness score - live presence uncertain"
    elif final_score > 0.2:
        explanation = "Good liveness score - caller appears to be live"
    else:
        explanation = "High liveness score - strong evidence of live caller"
    
    if liveness_score > 0.8:
        explanation += " (strong liveness indicators detected)"
    
    return {
        "score": final_score,
        "explanation": explanation,
        "raw_liveness": liveness_score
    }


def analyze_scam_patterns(
    scam_patterns: int,
    call_duration: int = None
) -> Dict[str, Any]:
    normalized_score = min(scam_patterns / 5.0, 1.0)
    
    if call_duration is not None:
        if call_duration < 60 and scam_patterns > 2:
            normalized_score = min(normalized_score * 1.2, 1.0)
        elif call_duration > 180 and scam_patterns <= 2:
            normalized_score = normalized_score * 0.8
    
    final_score = round(min(max(normalized_score, 0.0), 1.0), 2)
    
    if scam_patterns >= 4:
        explanation = f"Multiple scam patterns detected ({scam_patterns} patterns) - high fraud risk"
    elif scam_patterns >= 2:
        explanation = f"Several scam patterns detected ({scam_patterns} patterns) - moderate fraud risk"
    elif scam_patterns >= 1:
        explanation = f"One scam pattern detected - low fraud risk"
    else:
        explanation = "No scam patterns detected - call appears legitimate"
    
    pattern_details = []
    if scam_patterns > 0:
        if scam_patterns >= 1:
            pattern_details.append("unusual request for personal information")
        if scam_patterns >= 2:
            pattern_details.append("pressure to make immediate payment")
        if scam_patterns >= 3:
            pattern_details.append("caller claims to be from official institution")
        if scam_patterns >= 4:
            pattern_details.append("threats of legal consequences")
        if scam_patterns >= 5:
            pattern_details.append("request for remote access to device")
        
        if pattern_details:
            explanation += f" (patterns: {', '.join(pattern_details[:3])})"
    
    return {
        "score": final_score,
        "explanation": explanation,
        "scam_patterns_count": scam_patterns,
        "normalized_score": normalized_score
    }


def generate_explanations(
    voice_similarity: float,
    antispoof_score: float,
    liveness_score: float,
    scam_patterns: int,
    risk_score: float = None
) -> List[str]:
    explanations = []
    
    if voice_similarity < 0.4:
        explanations.append("Niska zgodność z głosem referencyjnym - głos rozmówcy znacząco odbiega od wzorca")
    elif voice_similarity < 0.6:
        explanations.append("Umiarkowana zgodność z głosem referencyjnym - występują pewne odchylenia")
    
    if antispoof_score > 0.7:
        explanations.append("Wysokie prawdopodobieństwo syntetycznej mowy - głos może być generowany sztucznie")
    elif antispoof_score > 0.5:
        explanations.append("Umiarkowane ryzyko syntetycznej mowy - zalecana dalsza weryfikacja")
    
    if liveness_score < 0.3:
        explanations.append("Bardzo niski wynik żywotności - rozmówca prawdopodobnie nie jest żywą osobą")
    elif liveness_score < 0.5:
        explanations.append("Niski wynik żywotności - trudno potwierdzić, że rozmówca jest żywą osobą")
    
    if scam_patterns > 3:
        explanations.append(f"Wykryto wiele wzorców typowych dla oszustw telefonicznych ({scam_patterns} wzorców)")
    elif scam_patterns > 1:
        explanations.append(f"Wykryto wzorce sugerujące potencjalne oszustwo ({scam_patterns} wzorców)")
    
    if risk_score is not None:
        if risk_score >= 0.7:
            explanations.append(f"Wysoki ogólny wskaźnik ryzyka ({risk_score:.2f}) - zalecane zablokowanie rozmowy")
        elif risk_score >= 0.35:
            explanations.append(f"Umiarkowany ogólny wskaźnik ryzyka ({risk_score:.2f}) - wymagana dodatkowa weryfikacja")
        else:
            explanations.append(f"Niski ogólny wskaźnik ryzyka ({risk_score:.2f}) - rozmowa wygląda na bezpieczną")
    
    if not explanations:
        explanations.append("Wszystkie wskaźniki mieszczą się w normie - rozmowa wygląda na bezpieczną")
    
    return explanations


def generate_detailed_explanations(
    voice_similarity: float,
    antispoof_score: float,
    liveness_score: float,
    scam_patterns: int,
    risk_score: float = None,
    noise_level: float = None,
    call_duration: int = None
) -> Dict[str, Any]:
    explanations = []
    detailed_reasons = []
    
    if voice_similarity < 0.3:
        explanations.append("Niska zgodność z głosem referencyjnym")
        detailed_reasons.append({
            "factor": "voice_similarity",
            "value": voice_similarity,
            "threshold": 0.3,
            "message": "Głos rozmówcy znacząco odbiega od wzorca głosowego w systemie"
        })
    elif voice_similarity < 0.5:
        explanations.append("Umiarkowana zgodność z głosem referencyjnym")
        detailed_reasons.append({
            "factor": "voice_similarity",
            "value": voice_similarity,
            "threshold": 0.5,
            "message": "Występują pewne różnice w porównaniu z wzorcem głosowym"
        })
    
    if antispoof_score > 0.7:
        explanations.append("Wysokie ryzyko syntetycznej mowy")
        detailed_reasons.append({
            "factor": "antispoof_score",
            "value": antispoof_score,
            "threshold": 0.7,
            "message": "Algorytm wykrył cechy charakterystyczne dla sztucznie generowanego głosu"
        })
    elif antispoof_score > 0.5:
        explanations.append("Umiarkowane ryzyko syntetycznej mowy")
        detailed_reasons.append({
            "factor": "antispoof_score",
            "value": antispoof_score,
            "threshold": 0.5,
            "message": "Wykryto pewne cechy mogące wskazywać na syntetyczny głos"
        })
    
    if liveness_score < 0.3:
        explanations.append("Bardzo niska żywotność rozmówcy")
        detailed_reasons.append({
            "factor": "liveness_score",
            "value": liveness_score,
            "threshold": 0.3,
            "message": "Brak wystarczających dowodów na to, że rozmówca jest żywą osobą"
        })
    elif liveness_score < 0.5:
        explanations.append("Niska żywotność rozmówcy")
        detailed_reasons.append({
            "factor": "liveness_score",
            "value": liveness_score,
            "threshold": 0.5,
            "message": "Niepewność co do tego, czy rozmówca jest żywą osobą"
        })
    
    if scam_patterns > 3:
        explanations.append("Wykryto wiele wzorców oszustw")
        detailed_reasons.append({
            "factor": "scam_patterns",
            "value": scam_patterns,
            "threshold": 3,
            "message": f"Zidentyfikowano {scam_patterns} charakterystycznych wzorców oszustw telefonicznych"
        })
    elif scam_patterns > 1:
        explanations.append("Wykryto wzorce sugerujące oszustwo")
        detailed_reasons.append({
            "factor": "scam_patterns",
            "value": scam_patterns,
            "threshold": 1,
            "message": f"Wykryto {scam_patterns} wzorców typowych dla oszustw telefonicznych"
        })
    
    if noise_level is not None and noise_level > 0.7:
        explanations.append("Wysoki poziom szumu w tle")
        detailed_reasons.append({
            "factor": "noise_level",
            "value": noise_level,
            "threshold": 0.7,
            "message": "Wysoki poziom szumu utrudnia dokładną analizę głosu"
        })
    
    if call_duration is not None and call_duration < 30:
        explanations.append("Bardzo krótka rozmowa")
        detailed_reasons.append({
            "factor": "call_duration",
            "value": call_duration,
            "threshold": 30,
            "message": "Krótki czas rozmowy ogranicza ilość danych do analizy"
        })
    
    if risk_score is not None:
        if risk_score >= 0.7:
            explanations.append("Wysoki ogólny poziom ryzyka")
            detailed_reasons.append({
                "factor": "risk_score",
                "value": risk_score,
                "threshold": 0.7,
                "message": "Łączny wynik ryzyka przekracza próg dla rozmów wysokiego ryzyka"
            })
        elif risk_score >= 0.35:
            explanations.append("Umiarkowany ogólny poziom ryzyka")
            detailed_reasons.append({
                "factor": "risk_score",
                "value": risk_score,
                "threshold": 0.35,
                "message": "Łączny wynik ryzyka wymaga dodatkowej weryfikacji"
            })
    
    if not explanations:
        explanations.append("Wszystkie wskaźniki mieszczą się w normie")
        detailed_reasons.append({
            "factor": "all",
            "value": "normal",
            "threshold": "normal",
            "message": "Wszystkie analizowane parametry są w bezpiecznym zakresie"
        })
    
    return {
        "explanations": explanations,
        "detailed_reasons": detailed_reasons,
        "summary": " | ".join(explanations[:3]) if explanations else "Brak uzasadnień"
    }


def analyze_combined_risk(
    voice_similarity: float,
    antispoof_score: float,
    liveness_score: float,
    scam_patterns: int,
    call_duration: int = None,
    noise_level: float = None
) -> Dict[str, Any]:
    voice_result = analyze_voice_similarity(voice_similarity, call_duration, noise_level)
    spoof_result = detect_spoofing(antispoof_score, voice_similarity, call_duration)
    liveness_result = evaluate_liveness(liveness_score, call_duration, noise_level)
    scam_result = analyze_scam_patterns(scam_patterns, call_duration)
    
    combined_score = (
        voice_result["score"] * 0.30 +
        spoof_result["score"] * 0.30 +
        liveness_result["score"] * 0.20 +
        scam_result["score"] * 0.20
    )
    
    combined_score = round(min(combined_score, 1.0), 2)
    
    explanation_result = generate_detailed_explanations(
        voice_similarity=voice_similarity,
        antispoof_score=antispoof_score,
        liveness_score=liveness_score,
        scam_patterns=scam_patterns,
        risk_score=combined_score,
        noise_level=noise_level,
        call_duration=call_duration
    )
    
    return {
        "combined_risk_score": combined_score,
        "voice_similarity": voice_result,
        "spoofing": spoof_result,
        "liveness": liveness_result,
        "scam_patterns": scam_result,
        "explanations": explanation_result["explanations"],
        "detailed_reasons": explanation_result["detailed_reasons"],
        "summary": explanation_result["summary"],
        "timestamp": None
    }


if __name__ == "__main__":
    test_cases = [
        {
            "voice_similarity": 0.35,
            "antispoof_score": 0.75,
            "liveness_score": 0.25,
            "scam_patterns": 4,
            "call_duration": 45,
            "noise_level": 0.82
        },
        {
            "voice_similarity": 0.85,
            "antispoof_score": 0.15,
            "liveness_score": 0.90,
            "scam_patterns": 0,
            "call_duration": 180,
            "noise_level": 0.20
        },
        {
            "voice_similarity": 0.55,
            "antispoof_score": 0.45,
            "liveness_score": 0.60,
            "scam_patterns": 2,
            "call_duration": 95,
            "noise_level": 0.35
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"PRZYPADEK TESTowy {i}")
        print(f"{'='*50}")
        
        result = analyze_combined_risk(**test)
        
        print(f"\nŁączne ryzyko: {result['combined_risk_score']}")
        print(f"\nUZASADNIENIA:")
        for exp in result["explanations"]:
            print(f"  • {exp}")
        
        print(f"\nSZCZEGÓŁOWE POWODY:")
        for reason in result["detailed_reasons"]:
            print(f"  • {reason['message']}")
        
        print(f"\nPODSUMOWANIE: {result['summary']}")

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import os


class AuditLogger:
    def __init__(self, log_file: str = "logs.json", max_logs: int = 1000):
        self.log_file = log_file
        self.max_logs = max_logs
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def _load_logs(self) -> List[Dict]:
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_logs(self, logs: List[Dict]):
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _generate_trace_id(self) -> str:
        return str(uuid.uuid4())[:8]
    
    def log_analysis(
        self,
        call_id: str,
        risk_score: float,
        decision: str,
        input_data: Dict[str, Any],
        explanations: List[str],
        policy_version: str = "1.0",
        additional_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": self._generate_trace_id(),
            "call_id": call_id,
            "policy_version": policy_version,
            "risk_score": risk_score,
            "decision": decision,
            "input_data": {
                "voice_similarity": input_data.get("voice_similarity"),
                "antispoof_score": input_data.get("antispoof_score"),
                "liveness_score": input_data.get("liveness_score"),
                "scam_patterns": input_data.get("scam_patterns"),
                "call_duration": input_data.get("call_duration"),
                "noise_level": input_data.get("noise_level")
            },
            "explanations": explanations
        }
        
        if additional_data:
            log_entry["additional_data"] = additional_data
        
        logs = self._load_logs()
        logs.append(log_entry)
        
        if len(logs) > self.max_logs:
            logs = logs[-self.max_logs:]
        
        self._save_logs(logs)
        
        return log_entry
    
    def get_all_logs(self, limit: Optional[int] = None) -> List[Dict]:
        logs = self._load_logs()
        if limit:
            return logs[-limit:]
        return logs
    
    def get_logs_by_call_id(self, call_id: str) -> List[Dict]:
        logs = self._load_logs()
        return [log for log in logs if log.get("call_id") == call_id]
    
    def get_logs_by_decision(self, decision: str) -> List[Dict]:
        logs = self._load_logs()
        return [log for log in logs if log.get("decision") == decision]
    
    def get_logs_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        logs = self._load_logs()
        result = []
        for log in logs:
            timestamp = log.get("timestamp", "")
            if start_date <= timestamp <= end_date:
                result.append(log)
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        logs = self._load_logs()
        
        if not logs:
            return {
                "total_analyses": 0,
                "decisions": {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
                "average_risk_score": 0,
                "min_risk_score": 0,
                "max_risk_score": 0
            }
        
        decisions = {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0}
        risk_scores = []
        
        for log in logs:
            decision = log.get("decision", "UNKNOWN")
            if decision in decisions:
                decisions[decision] += 1
            
            risk_score = log.get("risk_score")
            if risk_score is not None:
                risk_scores.append(risk_score)
        
        return {
            "total_analyses": len(logs),
            "decisions": decisions,
            "average_risk_score": round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0,
            "min_risk_score": min(risk_scores) if risk_scores else 0,
            "max_risk_score": max(risk_scores) if risk_scores else 0
        }
    
    def clear_logs(self):
        self._save_logs([])


audit_logger = AuditLogger()

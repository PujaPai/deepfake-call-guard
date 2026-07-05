const form = document.getElementById("callForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
        call_id: document.getElementById("call_id").value,
        user_name: document.getElementById("user_name").value,
        call_duration: Number(document.getElementById("call_duration").value),
        noise_level: Number(document.getElementById("noise_level").value),
        voice_similarity: Number(document.getElementById("voice_similarity").value),
        antispoof_score: Number(document.getElementById("antispoof_score").value),
        liveness_score: Number(document.getElementById("liveness_score").value),
        scam_patterns: Number(document.getElementById("scam_patterns").value),
    };

    const res = await fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    document.getElementById("risk_score").innerText = data.risk_score;
    document.getElementById("decision").innerText = data.decision;

    const decisionSpan = document.getElementById("decision");
    decisionSpan.className = data.decision.toLowerCase();

    const exp = document.getElementById("explanations");
    exp.innerHTML = "";
    if (data.explanations && data.explanations.length > 0) {
        data.explanations.forEach(e => {
            const li = document.createElement("li");
            li.innerText = e;
            exp.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.innerText = "All indicators are within normal ranges";
        exp.appendChild(li);
    }

    if (data.log_entry) {
        document.getElementById("logDetails").style.display = "block";
        document.getElementById("traceId").innerText = data.log_entry.trace_id;
        document.getElementById("timestamp").innerText = data.log_entry.timestamp;
    }

    document.getElementById("logs").textContent = JSON.stringify(data.log_entry, null, 2) + "\n\n" + document.getElementById("logs").textContent;

    refreshHistory();
    refreshStatistics();

    form.reset();
});

async function refreshHistory() {
    try {
        const res = await fetch("/logs?limit=50");
        const data = await res.json();
        
        const table = document.getElementById("historyTable");
        table.innerHTML = "";
        
        if (data.logs && data.logs.length > 0) {
            const logs = data.logs.reverse();
            logs.forEach(log => {
                const row = document.createElement("tr");
                const date = new Date(log.timestamp);
                const formattedDate = date.toLocaleString();
                
                row.innerHTML = `
                    <td>${formattedDate}</td>
                    <td>${log.call_id}</td>
                    <td>${log.risk_score}</td>
                    <td class="${log.decision.toLowerCase()}">${log.decision}</td>
                    <td style="font-size: 12px; color: #94a3b8;">${log.trace_id}</td>
                `;
                table.appendChild(row);
            });
        } else {
            const row = document.createElement("tr");
            row.innerHTML = `<td colspan="5" style="color: #94a3b8;">No history available</td>`;
            table.appendChild(row);
        }
        
        document.getElementById("historyCount").innerText = `(${data.logs ? data.logs.length : 0} records)`;
    } catch (error) {
        console.error("Error fetching history:", error);
    }
}

async function refreshStatistics() {
    try {
        const res = await fetch("/logs/statistics");
        const stats = await res.json();
        
        document.getElementById("totalAnalyses").innerText = stats.total_analyses || 0;
        document.getElementById("allowCount").innerText = stats.decisions?.ALLOW || 0;
        document.getElementById("reviewCount").innerText = stats.decisions?.REVIEW || 0;
        document.getElementById("blockCount").innerText = stats.decisions?.BLOCK || 0;
        document.getElementById("avgRisk").innerText = stats.average_risk_score || 0;
    } catch (error) {
        console.error("Error fetching statistics:", error);
    }
}

async function clearHistory() {
    if (confirm("Are you sure you want to clear all history?")) {
        try {
            await fetch("/logs/clear", { method: "DELETE" });
            refreshHistory();
            refreshStatistics();
        } catch (error) {
            console.error("Error clearing history:", error);
        }
    }
}

refreshHistory();
refreshStatistics();

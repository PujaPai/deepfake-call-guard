# DeepFake Call Guard — projekt referencyjny

> **Cel**: obrona przed oszustwami głosowymi (voice/deepfake scam) w rozmowach telefonicznych.
> System ocenia, czy próbka rozmowy bardziej przypomina **prawdziwego człowieka** czy **syntetyczny / podszyty głos**.
> **Uwaga**: to jest system **oceny ryzyka**, a nie nieomylna prawda absolutna. Decyzje wysokiego ryzyka powinny być potwierdzane dodatkowymi kontrolami (np. callback, challenge-response, MFA, biometria aktywna).

## 1. Proponowane rozwiązanie — architektura

### Warstwa wejściowa
- SIP/VoIP, call center, IVR, pliki WAV/FLAC/MP3, stream WebSocket.
- Buforowanie audio w krótkich oknach (np. 2–5 s).
- Normalizacja: mono, 16 kHz, VAD (wykrywanie mowy), odszumianie.

### Warstwa detekcji
Pipeline hybrydowy:
1. **ASR + analiza treści** — transkrypcja + analiza semantyczna scam-patterns.
2. **Speaker verification** — porównanie głosu z referencją znanego użytkownika.
3. **Anti-spoofing / synthetic speech detection** — model na cechach akustycznych.
4. **Conversational liveness** — sprawdzanie naturalności dialogu (opóźnienia, przerwania, odpowiedzi na losowe challenge).
5. **Prosody & artifact checks** — jitter, shimmer, F0, flatness, spectral rolloff, clipping, powtarzalność cech.
6. **Risk engine** — agregacja wielu sygnałów do jednego `risk_score`.

### Warstwa decyzji
- `ALLOW` — niski poziom ryzyka
- `REVIEW` — średnie ryzyko, analiza człowieka / callback
- `BLOCK` — wysoki poziom ryzyka

### Warstwa observability
- **Traces**: OpenTelemetry (ścieżka requestu przez pipeline)
- **Metrics**: Prometheus / OTel metrics (latency, recall, FP/FN, queue lag)
- **Logs**: strukturalne JSON logs (trace_id, call_id, model_version)
- **Dashboards**: Grafana
- **Distributed tracing backend**: Tempo / Jaeger
- **Log backend**: Loki / Elasticsearch

---

## 2. Wymagania funkcjonalne

1. System przyjmuje audio rozmowy lub stream audio.
2. System dzieli audio na segmenty mowy i ignoruje ciszę.
3. System wylicza cechy akustyczne i behawioralne.
4. System potrafi porównać głos z próbką referencyjną użytkownika.
5. System wykrywa wzorce charakterystyczne dla mowy syntetycznej / klonowanej.
6. System ocenia liveness rozmowy (challenge-response, reaktywność, turn-taking).
7. System nadaje `risk_score` 0–1.
8. System zwraca uzasadnienie decyzji (`explanations[]`).
9. System loguje każdy etap przetwarzania z korelacją po `trace_id`.
10. System wystawia metryki i health-check.
11. System zapisuje wersje modeli, progów i polityk decyzyjnych.
12. System wspiera ponowną analizę nagrania offline.
13. System zapisuje zdarzenia bezpieczeństwa do audytu.
14. System maskuje PII w logach i transkrypcjach.
15. System umożliwia A/B test progów i modeli.

## 3. Wymagania niefunkcjonalne

### Niezawodność
- odporność na brak modelu / błąd pojedynczego komponentu,
- fallback z degradacją jakości, ale bez utraty ścieżki audytowej,
- retry / circuit breaker dla usług zewnętrznych.

### Wydajność
- inferencja near-real-time dla krótkich okien,
- SLA np. P95 < 800 ms dla segmentu 3 s,
- backpressure dla kolejek.

### Skalowalność
- poziome skalowanie serwisów inferencyjnych,
- rozdzielenie procesu intake, inferencji, scoringu i archiwizacji.

### Bezpieczeństwo
- szyfrowanie danych at-rest i in-transit,
- RBAC,
- rotacja sekretów,
- brak surowych danych PII w logach,
- polityka retencji nagrań.

### Jakość modelu
- monitoring driftu danych,
- monitoring driftu predykcji,
- monitoring precision/recall/FPR/FNR,
- wersjonowanie modeli i datasetów.

### Utrzymywalność
- czytelny kod, testy, typed Python, linting, CI/CD,
- architektura pluginowa do podmiany modeli.

### Zgodność / audyt
- pełna ścieżka decyzji,
- reprodukowalność wyniku dla tych samych modeli/progów,
- audyt zmian konfiguracji.

---

## 4. Observability — co mierzyć

### Logi
Minimalne pola logów:
- `timestamp`
- `level`
- `message`
- `service.name`
- `trace_id`
- `span_id`
- `call_id`
- `segment_id`
- `tenant_id`
- `model_version`
- `policy_version`
- `risk_score`
- `decision`
- `latency_ms`

### Metryki
- `calls_total`
- `calls_failed_total`
- `segments_processed_total`
- `inference_latency_ms{model=...}`
- `pipeline_latency_ms`
- `risk_score_distribution`
- `review_rate`
- `block_rate`
- `allow_rate`
- `false_positive_rate`
- `false_negative_rate`
- `queue_lag_ms`

### Traces
Span’y:
- `audio.ingest`
- `audio.preprocess`
- `vad.run`
- `feature.extract`
- `speaker.verify`
- `antispoof.predict`
- `liveness.evaluate`
- `risk.aggregate`
- `decision.publish`

### Alerty
- wzrost `block_rate`
- wzrost `false_positive_rate`
- timeout usług inferencyjnych
- spadek jakości ASR
- brak logów/traces (telemetry gap)
- wzrost empty-audio / decode-failures

---

## 5. Technologie, które warto dorzucić

### Backend / orkiestracja
- **FastAPI** — REST / WebSocket
- **Pydantic v2** — walidacja danych
- **Celery / Dramatiq / Arq** — asynchroniczne joby
- **Kafka / Redpanda** — event streaming
- **Redis** — cache / rate limiting / krótkie stany rozmów
- **PostgreSQL** — metadane, policy, audyt
- **MinIO / S3** — przechowywanie nagrań i feature snapshots

### ML / audio
- **PyTorch** — modele
- **torchaudio** — audio I/O i przetwarzanie
- **librosa** — cechy akustyczne
- **numpy/scipy** — DSP
- **pyannote.audio** — diarization/VAD
- **SpeechBrain** — speaker verification
- **Whisper / faster-whisper** — ASR

### Observability / SRE
- **OpenTelemetry** — standard telemetry
- **OTel Collector** — kolektor sygnałów
- **Prometheus** — metrics
- **Grafana** — dashboardy
- **Tempo/Jaeger** — traces
- **Loki/ELK** — logi
- **Sentry** — błędy aplikacyjne

### MLOps
- **MLflow** — eksperymenty i registry modeli
- **DVC** — versie datasetów
- **Evidently** — drift / monitoring jakości
- **Feast** — feature store (opcjonalnie)

---

## 6. VS Code — sugerowane rozszerzenia

W projekcie jest `.vscode/extensions.json` z rekomendowanymi rozszerzeniami:
- `ms-python.python`
- `ms-python.vscode-pylance`
- `ms-python.debugpy`
- `charliermarsh.ruff`
- `ms-azuretools.vscode-docker`
- `tamasfe.even-better-toml`
- `redhat.vscode-yaml`

---

## 7. Jak czytać kod

Kod jest zbudowany pluginowo:
- `app/core/schemas.py` — modele danych
- `app/core/logging_config.py` — JSON logging + correlation IDs
- `app/core/telemetry.py` — OpenTelemetry i metryki
- `app/features/audio_features.py` — ekstrakcja cech akustycznych
- `app/detectors/*.py` — detektory
- `app/engine/risk_engine.py` — agregacja ryzyka
- `app/api/main.py` — API FastAPI

Każda funkcja ma komentarze wyjaśniające **co robi**, **po co istnieje**, **co zwraca** i **jak wpływa na decyzję systemu**.

---

## 8. Ważna uwaga praktyczna

Sam model „deepfake czy człowiek” nie wystarczy. Najlepszy efekt daje **system wielowarstwowy**:
- biometria głosu + anti-spoofing,
- challenge-response (np. powtórz losową frazę),
- callback na znany numer,
- analiza treści rozmowy pod scam patterns,
- polityka manual review dla wyników granicznych.

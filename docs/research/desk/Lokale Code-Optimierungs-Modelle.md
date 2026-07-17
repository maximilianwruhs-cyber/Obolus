# **Lokale SLMs für autonome, iterative Code-Optimierung: Modellselektion und Infrastruktur-Design**

Die Realisierung eines vollständig lokalen, autonomen Systems zur kontinuierlichen Code-Optimierung auf Consumer-Hardware erfordert eine präzise Balance zwischen Recheneffizienz, Latenz und funktionaler Spezialisierung. Bei mehreren hundert Iterationen pro Stunde erweisen sich herkömmliche Large Language Models (LLMs) aufgrund ihres hohen Rechenaufwands und der daraus resultierenden Latenzen als unpraktikabel. Stattdessen rücken hochspezialisierte Small Language Models (SLMs) in den Fokus, die durch gezieltes Vortraining und optimierte Inferenzarchitekturen komplexe Aufgaben mit minimalem Ressourcenaufwand bewältigen.  
Der iterative Optimierungskreislauf beruht auf der Interaktion zweier primärer Teilsysteme: dem Code-Mutations-Modul („Code Bencher“) und dem logischen Steuerungs- und Analyse-Modul („Black Boxer“). Während das Mutationsmodul syntaktisch präzise Modifikationen am Quellcode vornehmen muss, verarbeitet das Steuerungsmodul Fehlermeldungen, Testprotokolle und statische Analysen, um deterministische JSON-Strukturen für die nachfolgende Ausführung zu generieren. Im Folgenden wird eine detaillierte technische Analyse der am besten geeigneten Modellkandidaten und der notwendigen Inferenz-Infrastruktur dargelegt.

## **Kategorie 1: Code-Mutation und Patch-Generierung (Code Bencher)**

Die primäre Aufgabe des Mutationsmoduls besteht darin, gezielte Code-Modifikationen auf Basis von Testfehlern oder Optimierungsmetriken vorzunehmen. Da das vollständige Umschreiben großer Codedateien in lokalen Systemen ineffizient ist, enorme Latenzen verursacht und die Token-Generierung unnötig aufbläht, sind minimale, präzise Änderungen zwingend erforderlich.

### **Algorithmische Komplexität und Format-Alternativen**

Die Erzeugung von Standard-Patches stellt für SLMs unter 3 Milliarden Parametern eine erhebliche kognitive Hürde dar. Klassische Unified Diffs erfordern die Berechnung präziser Zeilennummern und Hunk-Header (z. B. @@ \-10,7 \+10,7 @@), was den mathematischen Aufmerksamkeitsfokus kleiner Modelle überfordert und häufig zu fehlerhaften Zeilenverschiebungen führt.  
Untersuchungen im Rahmen des *Diff-XYZ*\-Benchmarks zeigen, dass kleinere Open-Source-Modelle kaum von komplexen Unified-Diff-Formaten profitieren, sondern bei strukturierten Suchen-und-Ersetzen-Blöcken (Search/Replace Blocks) weitaus stabilere Ergebnisse liefern. Diese Edit-Blöcke, bekannt aus Werkzeugen wie *Aider*, definieren einen präzisen Code-Ausschnitt, der im Originaldokument gesucht werden soll, und stellen ihm den modifizierten Ziel-Ausschnitt gegenüber. Um die Robustheit im lokalen System zu maximieren, sollte das Steuerungsskript unvollständige Zeilennummern oder geringfügige Einrückungsunterschiede durch Algorithmen wie Fuzzy-Matching (z. B. via difflib) oder bi-direktionale Sliding-Window-Suchen kompensieren, anstatt sich auf die starre Syntax von Standard-Diff-Parsern zu verlassen.

| Modell-Repository-Pfad | Exakte Parameter | Kontext-Fenster | Quantisierungs-Verfügbarkeit | Lizenz-Typ | HumanEval Pass@1 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | 1,54 Milliarden | 32.768 Token | GGUF, AWQ, GPTQ | Apache 2.0 | 65,9% \- 68,9% |
| Qwen\[span\_37\](start\_span)\[span\_37\](end\_span)/Qwen2.5-Coder-3B-Instruct | 3,09 Milliarden | 32.768 Token | GGUF, AWQ, GPTQ | Qwen Research | 75,6% \- 76,2% |
| deepseek-ai/deepseek\[span\_47\](start\_span)\[span\_47\](end\_span)\[span\_49\](start\_span)\[span\_49\](end\_span)-coder-1.3b-instruct | 1,30 Milliarden | 16.000 Token | GGUF, AWQ, GPTQ | DeepSeek License | \~60,1% |
| ibm-granite/granite-3b-code-instruct-128k | 3,00 Milliarden | 128.000 Token | GGUF | Apache 2.0 | \~52,0% \- 58,0% |
| stability\[span\_66\](start\_span)\[span\_66\](end\_span)ai/stable-code-instruct-3b | 2,79 Milliarden | 16.384 Token | GGUF, GPTQ | Stability Non-Com. | \~32,4% |

\#\#\# Analyse der Modellkandidaten für die Code-Mutation

#### **1\. Qwen/Qwen2.5-Coder-1.5B-Instruct**

Dieses Modell basiert auf der dichten Transformer-Architektur von Qwen2.5 und wurde auf einer massiven Datenbasis von 5,5 Billionen Tokens vortrainiert, die einen extrem hohen Anteil an Quellcode und synthetischen Validierungsdaten enthält. Dank der Grouped-Query Attention (GQA) mit 12 Query-Heads und 2 KV-Heads arbeitet das Modell bei der Inferenz hochgradig speichereffizient, was die Latenz im lokalen Loop minimiert. GGUF-Quantisierungen wie Q4\_K\_M (ca. 986 MB) oder Q8\_0 (ca. 1,65 GB) ermöglichen eine Ausführung mit minimalem RAM-Footprint. Aufgrund des hervorragenden Befolgungsverhaltens von System-Prompts eignet sich dieses Modell optimal als **Out-of-the-box-Instruct-Variante** für Suchen-und-Ersetzen-Blöcke.

#### **2\. Qwen/Qwen2.5-Coder-3B-Instruct**

Mit 36 statt 28 Schichten bietet die 3B-Variante eine signifikant höhere logische Tiefe als das kleinere 1,5B-Modell und erzielt in Code-Generierungs-Benchmarks wie HumanEval herausragende Pass@1-Ergebnisse von bis zu 76,2%. In GGUF-Quantisierungen (Q4\_K\_M benötigt ca. 2,1 GB RAM) läuft das Modell flüssig auf Standard-Consumer-Hardware. Zu beachten ist jedoch die proprietäre *Qwen Research Lizenz*, die eine kommerzielle Nutzung im Gegensatz zur Apache-2.0-Lizenz des 1,5B-Modells einschränkt. Es wird empfohlen, dieses Modell als **direkt einsatzbereite Instruct-Variante** für komplexe Refactoring-Schleifen zu nutzen, bei denen das kleinere Modell an semantische Grenzen stößt.

#### **3\. deepseek-ai/deepseek-coder-1.3b-instruct**

DeepSeek-Coder wurde von Grund auf auf 2 Billionen Tokens (87 % Code, 13 % natürliche Sprache in Englisch und Chinesisch) trainiert. Neben einer stabilen Leistung bei kurzen Code-Mutationen bietet das Modell eine native Unterstützung für Fill-in-the-Middle-Aufgaben (FIM) über eine Kontextlänge von 16.000 Token. GGUF-Versionen sind über Repositories wie tensorblock/deepseek-coder-1.3b-instruct-GGUF leicht verfügbar. Während die Instruct-Variante direkt für Suchen-und-Ersetzen-Operationen eingesetzt werden kann, eignet sich die Base-Version (deepseek-ai/deepseek-coder-1.3b-base) aufgrund des spezialisierten Vortrainings exzellent als **Grundlage für ein eigenes, domänenspezifisches Fine-Tuning** auf ein proprietäres Patch-Format.

#### **4\. ibm-granite/granite-3b-code-instruct-128k**

Dieses Modell wurde speziell für Langkontext-Szenarien optimiert und doubelte das Kontextfenster schrittweise durch Anpassung der RoPE-Theta-Werte auf 128.000 Token. Es basiert auf einer klassischen Multi-Head-Attention-Architektur und wurde auf 116 Programmiersprachen trainiert. GGUF-Quantisierungen wie Q4\_K\_M (ca. 2,13 GB) ermöglichen den lokalen Betrieb auf Standard-Hardware. Aufgrund der weiten Kontextabdeckung eignet sich die **Instruct-Variante** hervorragend, wenn das Mutationsmodul zur Optimierung den Kontext ganzer Klassenstrukturen oder umfangreicher Testdateien erfassen muss.

#### **5\. stabilityai/stable-code-instruct-3b**

Dieses Modell basiert auf einer autoregressiven Decoder-Architektur und nutzt Rotary Position Embeddings (RoPE), die auf die ersten 25 % der Head-Embedding-Dimensionen angewendet werden, um den Durchsatz zu optimieren. Es wurde auf 18 Programmiersprachen trainiert und bietet eine solide FIM-Inferenz. Quantisierte GGUF-Varianten (ca. 1,71 GB für Q4\_K\_M) sind verfügbar. Für die kommerzielle Nutzung ist jedoch eine kostenpflichtige Stability AI Membership erforderlich. Die Base-Variante (stable-code-3b) bietet sich vor allem für **Spezial-SFT (Supervised Fine-Tuning)** an, wenn ein extrem schlanker Code-Generator mit modifiziertem Tokenizer benötigt wird.

## **Kategorie 2: Structural JSON & Logic Routing (Black Boxer)**

Das Analysemodul („Black Boxer“) agiert als deterministischer Router des Systems. Es wertet compilergenerierte Fehlermeldungen, Stack-Traces und Performance-Metriken aus und überführt diese in ein strikt strukturiertes JSON-Format, das vom Steuerungsskript ohne das Risiko von Syntaxfehlern geparst werden kann.

### **Funktion von Grammatiken und Constrained Decoding**

Die Ausgabe strukturierter Daten durch SLMs im Bereich von 1B bis 3B Parametern ist fehleranfällig, wenn ausschließlich auf Prompt-Engineering gesetzt wird. Kleinere Modelle neigen bei komplexen JSON-Vorgaben dazu, syntaktisch ungültige Zeichen zu generieren oder unerwünschte textuelle Erklärungen hinzuzufügen. Zur Gewährleistung absoluter Stabilität muss daher **Grammar-Constrained Decoding** eingesetzt werden.  
Inferenz-Engines wie llama.cpp (über GBNF-Grammatiken), vLLM (über XGrammar) oder Bibliotheken wie Outlines modifizieren die Wahrscheinlichkeitsverteilung der nächsten Tokens (Logits) in Echtzeit während des Dekodierungsprozesses. Alle Tokens, die im aktuellen Zustand der Generierung gegen das vordefinierte JSON-Schema verstoßen würden, werden maskiert (ihre Logit-Wahrscheinlichkeit wird auf negativ unendlich gesetzt). Das Modell ist dadurch mechanisch gezwungen, ausschließlich valide JSON-Pfade zu beschreiten, was die Fehlerquote bei der Syntaxanalyse auf null reduziert. Um semantische Halluzinationen innerhalb des erzwungenen Schemas zu verhindern, sollten im JSON-Schema selbsterklärende Schlüssel (Keys) verwendet werden, die dem Modell während der sequenziellen Generierung als logische Ankerpunkte dienen.

| Modell-Repository-Pfad | Exakte Parameter | Kontext-Fenster | Quantisierungs-Verfügbarkeit | Lizenz-Typ | Primäre Stärke im Loop |
| :---- | :---- | :---- | :---- | :---- | :---- |
| google/gemma-3-1b-it | 1,00 Milliarden | 32.768 Token | GGUF (inkl. QAT Q4\_0) | Gemma-Lizenz | Maximale Verarbeitungsgeschwindigkeit |
| meta-llama/Llama-3.2-3B-Instruct | 3,21 Milliarden | 128.000 Token | GGUF, AWQ, GPTQ | Llama 3.2 Community | Hohe Systemprompt-Treue |
| Qwen/Qwen2.5-1.5B-Instruct | 1,54 Milliarden | 32.768 Token | GGUF, AWQ, GPTQ | Apache 2.0 | Ausgewogene logische Zuordnung |
| microsoft/Phi-4-mini-instruct | 3,80 Milliarden | 128.000 Token | GGUF, AWQ, GPTQ | MIT-Lizenz | Überragende mathematische Logik |

### **Analyse der Modellkandidaten für die strukturierte Analyse**

#### **1\. google/gemma-3-1b-it**

Gemma-3-1B wurde auf einem breiten multilingualen Korpus von 2 Billionen Tokens trainiert und profitiert von einer modernen Inferenz-Architektur mit Interleaved Sliding Window Attention (ISWA), wodurch der Speicherbedarf des KV-Caches signifikant reduziert wird. Die Inferenzgeschwindigkeit auf reiner CPU-Hardware liegt bei optimierter Quantisierung (z. B. Q4\_0 QAT GGUF) bei hervorragenden 15 bis 25 Tokens pro Sekunde, während auf lokalen GPUs Raten von über 50 Tokens pro Sekunde erreicht werden. Da dieses ultrakompakte Modell Instruktionen präzise befolgt, eignet sich die **Instruct-Variante** perfekt für latenzkritische Routing-Entscheidungen im Millisekundenbereich unter direkter GBNF-Grammatik-Erzwingung.

#### **2\. meta-llama/Llama-3.2-3B-Instruct**

Dieses Modell nutzt eine optimierte Transformer-Decoder-Architektur mit GQA und wurde gezielt für Agentenanwendungen, logisches Schließen und Tool-Calling per SFT und RLHF ausgerichtet. GGUF-Varianten wie bartowski/Llama-3.2-3B-Instruct-GGUF laufen hocheffizient auf Standard-Laptops mit 8 GB RAM. Seine besondere Stärke liegt in der Einhaltung komplexer System-Prompts, wodurch es logische Zusammenhänge in Test-Fehlerprotokollen präzise analysieren und strukturiert abbilden kann. Die **Instruct-Variante** ist für komplexe, tief verschachtelte JSON-Schemata der Standard-Kandidat.

#### **3\. Qwen/Qwen2.5-1.5B-Instruct**

Dieses Modell zeichnet sich durch ein starkes mathematisches und logisches Grundverständnis aus, was es in seiner Gewichtsklasse zu einem der besten Modelle für strukturierte Extraktionsaufgaben macht. In empirischen Auswertungen zeigt es eine bemerkenswert geringe Fehlerquote beim Erreichen von Schema-Konformität. Die **Instruct-Variante** kann direkt out-of-the-box eingesetzt werden, um semantische Fehlerbeschreibungen in strukturierte Kategorien zu übersetzen, die von einem nachgelagerten Parser deterministisch verarbeitet werden.

#### **4\. microsoft/Phi-4-mini-instruct**

Phi-4-mini überschreitet mit 3,8 Milliarden Parametern knapp die nominelle 3B-Grenze, bietet dafür jedoch eine unerreichte Dichte an logischen Fähigkeiten. Trainiert auf 5 Billionen sorgfältig gefilterter und synthetischer Tokens, erzielt es im logisch anspruchsvollen ARC-Challenge-Benchmark spektakuläre 83,7% und übertrifft damit reguläre 7B- und 8B-Modelle deutlich. Es unterstützt ein Kontextfenster von 128.000 Token und verfügt über ein exzellentes Tool-Calling-Training. Die **Instruct-Variante** ist die erste Wahl, wenn das System hochkomplexe Traceback-Analysen durchführen muss, die ein tiefes, schrittweises logisches Schließen erfordern.

## **System-Integration und Optimierungsverfahren**

Für den produktiven Einsatz im geschlossenen Optimierungskreislauf müssen die Modelle dauerhaft im Arbeitsspeicher gehalten werden, um zeitintensive Ladezyklen zu vermeiden. Die Kommunikation erfolgt über lokale API-Endpunkte, die mithilfe von Inferenz-Engines wie llama.cpp bereitgestellt werden.  
  `┌────────────────────────────────────────────────────────┐`  
  `│                   Lokaler Test-Runner                  │`  
  `│            (Führt Unit-Tests & Benchmarks aus)         │`  
  `└───────────────────────────┬────────────────────────────┘`  
                              `│`  
                    `Test-Logs & Code-Kontext`  
                              `│`  
                              `▼`  
  `┌────────────────────────────────────────────────────────┐`  
  `│           Black Boxer: google/gemma-3-1b-it            │`  
  `│           (Erzwingt JSON via GBNF-Grammatik)           │`  
  `└───────────────────────────┬────────────────────────────┘`  
                              `│`  
                    `Strukturiertes Routing-JSON`  
                              `│`  
                              `▼`  
  `┌────────────────────────────────────────────────────────┐`  
  `│     Code Bencher: Qwen/Qwen2.5-Coder-3B-Instruct       │`  
  `│       (Erzeugt präzise SEARCH/REPLACE-Edits)           │`  
  `└───────────────────────────┬────────────────────────────┘`  
                              `│`  
                     `Code-Patch (SFT-Format)`  
                              `│`  
                              `▼`  
  `┌────────────────────────────────────────────────────────┐`  
  `│                 Lokaler Patch-Applier                  │`  
  `│             (Wendet Fuzzy-Matching-Patch an)           │`  
  `└────────────────────────────────────────────────────────┘`

### **Infrastruktur-Optimierungen zur Latenzminimierung**

1. **Prompt-Caching aktivieren:** Da sich der Systemprompt und große Teile des Code-Kontexts zwischen den Iterationen kaum ändern, muss das Prompt-Caching des Inferenz-Servers zwingend aktiviert werden (--cache-prompt in llama.cpp). Dies eliminiert die zeitintensive Prefill-Phase bei wiederholten Aufrufen und reduziert die Time-to-First-Token (TTFT) drastisch.  
2. **Flash Attention und GQA:** Der Einsatz von Grouped-Query Attention (GQA) minimiert den Speicherbedarf des KV-Caches im RAM/VRAM erheblich. In Verbindung mit Flash Attention wird die quadratische Berechnungskomplexität des Aufmerksamkeitsmechanismus auf einen nahezu linearen Verlauf reduziert, was die Generierungsgeschwindigkeit bei großen Kontexten stabilisiert.  
3. **Optimierte Quantisierungen (QAT):** Bei ultrakompakten Modellen wie google/gemma-3-1b-it sollten Quantized Activation Training (QAT) GGUF-Versionen bevorzugt werden. Diese minimieren den Qualitätsverlust bei der Reduktion auf 4-Bit-Präzision und bieten eine überlegene logische Zuverlässigkeit im Vergleich zu herkömmlichen Post-Training-Quantisierungen (PTQ).

### **Implementierungsbeispiel: Deterministische Steuerungsschleife**

Das nachfolgende Python-Skript demonstriert die Einbindung der lokalen Endpunkte. Es erzwingt beim Analyse-Modul („Black Boxer“) über die API-Schnittstelle die strikte Einhaltung des JSON-Schemas und übergibt die strukturierte Ausgabe direkt an den „Code Bencher“, um eine gezielte Suchen-und-Ersetzen-Mutation zu generieren.  
`import json`  
`import requests`

`# Definition der lokalen API-Endpunkte`  
`API_BLACK_BOX = "http://localhost:8081/v1/chat/completions"`  
`API_CODE_BENCHER = "http://localhost:8080/v1/chat/completions"`

`# Definition des Ziel-JSON-Schemas für das logische Routing`  
`routing_schema = {`  
    `"type": "object",`  
    `"properties": {`  
        `"status": {"type": "string", "enum": ["success", "failed", "error"]},`  
        `"error_type": {"type": "string"},`  
        `"root_cause_analysis": {"type": "string"},`  
        `"suggested_fix_strategy": {"type": "string"},`  
        `"target_file": {"type": "string"}`  
    `},`  
    `"required": ["status", "error_type", "root_cause_analysis", "suggested_fix_strategy", "target_file"],`  
    `"additionalProperties": False`  
`}`

`def get_structured_analysis(test_logs, code_context):`  
    `"""`  
    `Analysiert Testfehler und erzwingt ein schema-konformes JSON`  
    `mittels Grammar-Constrained Decoding.`  
    `"""`  
    `prompt = f"Fehlerprotokoll:\n{test_logs}\n\nCode-Kontext:\n{code_context}"`  
      
    `payload = {`  
        `"model": "gemma-3-1b-it",`  
        `"messages": [`  
            `{`  
                `"role": "system",`  
                `"content": "Du bist ein präzises logisches Routing-System. Analysiere den Fehler und antworte ausschließlich im vorgegebenen JSON-Format."`  
            `},`  
            `{"role": "user", "content": prompt}`  
        `],`  
        `"response_format": {`  
            `"type": "json_schema",`  
            `"json_schema": {`  
                `"name": "routing_response",`  
                `"schema": routing_schema`  
            `}`  
        `},`  
        `"temperature": 0.0  # Maximale Determinierung`  
    `}`  
      
    `response = requests.post(API_BLACK_BOX, json=payload)`  
    `response.raise_for_status()`  
    `return json.loads(response.json()["choices"][0]["message"]["content"])`

`def generate_code_mutation(original_code, analysis):`  
    `"""`  
    `Erzeugt eine minimale Code-Mutation mittels des SEARCH/REPLACE-Blockformats.`  
    `"""`  
    `prompt = f"Code:\n{original_code}\n\nAnalyse:\n{json.dumps(analysis)}"`  
      
    `payload = {`  
        `"model": "qwen2.5-coder-3b-instruct",`  
        `"messages": [`  
            `{`  
                `"role": "system",`  
                `"content": (`  
                    `"Du bist ein Code-Mutations-Modul. Nenne ausschließlich Code-Modifikationen "`  
                    `"im SEARCH/REPLACE Blockformat. Erkläre nichts außerhalb der Blöcke.\n\n"`  
                    `"Format:\n"`  
                    `"<<<<<<< SEARCH\n[Originaler Code]\n=======\n[Modifizierter Code]\n>>>>>>> REPLACE"`  
                `)`  
            `},`  
            `{"role": "user", "content": prompt}`  
        `],`  
        `"temperature": 0.2`  
    `}`  
      
    `response = requests.post(API_CODE_BENCHER, json=payload)`  
    `response.raise_for_status()`  
    `return response.json()["choices"][0]["message"]["content"]`

## **Strategische Empfehlungen für den Produktivbetrieb**

Für den Aufbau eines robusten, autonomen Optimierungssystems wird eine asymmetrische Multi-Modell-Architektur empfohlen.  
Für den **Black Boxer** (Logikanalyse und Routing) liefert das ultrakompakte google/gemma-3-1b-it in Kombination mit einer erzwungenen GBNF-Grammatik das beste Verhältnis aus Inferenzgeschwindigkeit und struktureller Präzision. Seine niedrige Latenz stellt sicher, dass die logische Vorverarbeitung komplexer Test-Logs den Flaschenhals des Gesamtsystems nicht belastet.  
Für den **Code Bencher** (Code-Mutation) ist Qwen/Qwen2.5-Coder-3B-Instruct der leistungsfähigste lokale Kandidat. Seine überlegene Leistung in Code-Benchmarks prädestiniert das Modell für anspruchsvolle Refactoring-Aufgaben. Sollte das System in einer rein kommerziell lizenzierten Umgebung betrieben werden, bei der die restriktive Lizenz der Qwen-3B-Variante ein rechtliches Risiko darstellt, empfiehlt sich der Ausweich auf Qwen/Qwen2.5-Coder-1.5B-Instru\[span\_133\](start\_span)\[span\_133\](end\_span)ct oder ibm-granite/granite-3b-code-instruct-128k, da beide unter der permissiven Apache-2.0-Lizenz stehen und eine hervorragende Inferenzstabilität aufweisen.

#### **Quellenangaben**

1\. Best Sub-3B GGUF Models for Mid-Range CPUs \+ 16GB RAM (2025), https://ggufloader.github.io/2025-07-07-top-10-gguf-models-i5-16gb.html 2\. Small LLM Performance Benchmark \- Research Report \- AscentCore, https://ascentcore.com/2026/04/01/small-llm-performance-benchmark/ 3\. Diff-XYZ: A Benchmark for Evaluating Diff Understanding \- arXiv, https://arxiv.org/pdf/2510.12487 4\. Daily Papers \- Hugging Face, https://huggingface.co/papers?q=source-code%20rescue 5\. Reliable JSON From Local LLMs: Structured Output Guide \- LLM Configurator, https://llmconfigurator.com/en/guides/llm-json-structured-output 6\. Structured outputs | LLM Inference Handbook \- BentoML, https://bentoml.com/llm/model-interaction/structured-outputs 7\. GPT code editing benchmarks | aider, https://aider.chat/docs/benchmarks.html 8\. Agentic Program Repair from Test Failures at Scale: A Neuro-symbolic approach with static analysis and test execution feedback \- arXiv, https://arxiv.org/html/2507.18755v1 9\. Edit formats \- Aider, https://aider.chat/docs/more/edit-formats.html 10\. GitHub \- dceluis/ln-diff: Line-numbered patch format. Non-sequential, llm and stream-friendly, https://github.com/dceluis/ln-diff 11\. Context Over Line Numbers: A Robust Way to Apply LLM Code Diffs | by Suraj Potnuru, https://medium.com/@surajpotnuru/context-over-line-numbers-a-robust-way-to-apply-llm-code-diffs-eb239e56283f 12\. Code Surgery: How AI Assistants Make Precise Edits to Your Files \- Fabian Hertwig's Blog, https://fabianhertwig.com/blog/coding-assistants-file-edits/ 13\. stable-code:3b-instruct-q4\_K\_M \- Ollama, https://ollama.com/library/stable-code:3b-instruct-q4\_K\_M 14\. QuantFactory/Qwen2.5-Coder-1.5B-Instruct-GGUF \- Hugging Face, https://huggingface.co/QuantFactory/Qwen2.5-Coder-1.5B-Instruct-GGUF 15\. Qwen2.5-Coder Technical Report \- arXiv, https://arxiv.org/html/2409.12186v3 16\. unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF \- Hugging Face, https://huggingface.co/unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF 17\. More Than a Score: Probing the Impact of Prompt Specificity on LLM Code Generation \- ACL Anthology, https://aclanthology.org/2025.ijcnlp-long.128.pdf 18\. Qwen/Qwen2.5-Coder-3B-Instruct-GGUF \- Hugging Face, https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF 19\. Qwen/Qwen2.5-Coder-3B-Instruct Free Chat Online \- Skywork, https://skywork.ai/blog/models/qwen-qwen2-5-coder-3b-instruct-free-chat-online/ 20\. TheBloke/deepseek-coder-1.3b-instruct-GGUF \- Hugging Face, https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF 21\. deepseek-ai/deepseek-coder-1.3b-base Free Chat Online \- Skywork, https://skywork.ai/blog/models/deepseek-ai-deepseek-coder-1-3b-base-free-chat-online-skywork-ai/ 22\. Qwen2.5-Coder Series: Powerful, Diverse, Practical. | Qwen, https://qwenlm.github.io/blog/qwen2.5-coder-family/ 23\. tensorblock/deepseek-coder-1.3b-instruct-GGUF \- Hugging Face, https://huggingface.co/tensorblock/deepseek-coder-1.3b-instruct-GGUF 24\. ModelScope模型库-deepseek-coder-1.3b-base, https://modelscope.cn/models/deepseek-ai/deepseek-coder-1.3b-base 25\. QuantFactory/granite-3b-code-base-128k-GGUF \- Hugging Face, https://huggingface.co/QuantFactory/granite-3b-code-base-128k-GGUF 26\. New Coding Model from IBM (IBM Granite) : r/LocalLLaMA \- Reddit, https://www.reddit.com/r/LocalLLaMA/comments/1cmugga/new\_coding\_model\_from\_ibm\_ibm\_granite/ 27\. RichardErkhov/ibm-granite\_-\_granite-3b-code-instruct-128k-gguf \- Hugging Face, https://huggingface.co/RichardErkhov/ibm-granite\_-\_granite-3b-code-instruct-128k-gguf 28\. Introducing Stable Code Instruct 3B \- Stability AI, https://stability.ai/news-updates/introducing-stable-code-instruct-3b 29\. brittlewis12/stable-code-3b-GGUF \- Hugging Face, https://huggingface.co/brittlewis12/stable-code-3b-GGUF 30\. TheBloke/stable-code-3b-GGUF \- Hugging Face, https://huggingface.co/TheBloke/stable-code-3b-GGUF 31\. Reliable JSON from Any LLM: Pydantic \+ Zod (2026) | TECHSY, https://techsy.io/en/blog/llm-structured-outputs-guide 32\. Taming LLMs: How to Get Structured Output Every Time (Even for Big Responses), https://dev.to/shrsv/taming-llms-how-to-get-structured-output-every-time-even-for-big-responses-445c 33\. Using Grammar | node-llama-cpp, https://node-llama-cpp.withcat.ai/guide/grammar 34\. google/gemma-3-4b-it \- Hugging Face, https://huggingface.co/google/gemma-3-4b-it 35\. Google\_gemma-3-1b-It-GGUF Free Chat Online \- skywork.ai, Click to Use\!, https://skywork.ai/blog/models/google\_gemma-3-1b-it-gguf-free-chat-online-skywork-ai/ 36\. Day 13: Small Language Models (SLMs) — Phi, Gemma, and On-Device AI, https://learncsdesigns.medium.com/day-13-small-language-models-slms-phi-gemma-and-on-device-ai-1794d9107b13 37\. meta-llama/Llama-3.2-3B-Instruct \- Hugging Face, https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct 38\. unsloth/Llama-3.2-3B-Instruct-GGUF \- Hugging Face, https://huggingface.co/unsloth/Llama-3.2-3B-Instruct-GGUF 39\. bartowski/Llama-3.2-3B-Instruct-GGUF \- Hugging Face, https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF 40\. Llama-3.2-3B-Instruct-Q8\_0-GGUF vs SmolLM2-360M-Instruct-GGUF \- AIModels.fyi, https://www.aimodels.fyi/models/compare/llama-3.2-3b-instruct-q8-0-gguf-hugging-quants-vs-smollm2-360m-instruct-gguf-huggingfacetb 41\. I fine-tuned Llama 3.2 3B for transcript analysis and it outperformed bigger models with ease, https://www.reddit.com/r/LocalLLaMA/comments/1n5w9yy/i\_finetuned\_llama\_32\_3b\_for\_transcript\_analysis/ 42\. Qwen2.5\_Coder\_(1.5B)-Tool\_Calling.ipynb \- Colab, https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen2.5\_Coder\_(1.5B)-Tool\_Calling.ipynb 43\. microsoft/Phi-4-mini-instruct \- Hugging Face, https://huggingface.co/microsoft/Phi-4-mini-instruct 44\. Best Small Language Models on Hugging Face Right Now\! \- KDnuggets, https://www.kdnuggets.com/best-small-language-models-on-hugging-face-right-now 45\. llama\_cpp\_ex \- Hex.pm, https://hex.pm/packages/llama\_cpp\_ex 46\. Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF \- Hugging Face, https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF 47\. QuantFactory/stable-code-3b-GGUF \- Hugging Face, https://huggingface.co/QuantFactory/stable-code-3b-GGUF 48\. Gemma 3 1B qat q4\_0 gguf without imatrix and (hopefully) correct metadata \- Reddit, https://www.reddit.com/r/LocalLLaMA/comments/1qbm7f4/gemma\_3\_1b\_qat\_q4\_0\_gguf\_without\_imatrix\_and/ 49\. Gemma 3 Release \- a google Collection \- Hugging Face, https://huggingface.co/collections/google/gemma-3-release 50\. dottxt-ai/outlines: Structured Outputs \- GitHub, https://github.com/dottxt-ai/outlines
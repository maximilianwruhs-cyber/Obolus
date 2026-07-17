# **Token-Kuration und Datenarchitektur für ressourceneffiziente Low-Parameter-Sprachmodelle**

## **Einführung in die token-effiziente Modellprägung**

In der Evolution der Transformer-basierten Sprachmodelle vollzieht sich ein grundlegender Paradigmenwechsel. Während frühe Architekturen darauf ausgelegt waren, unstrukturiertes Web-Rauschen durch eine massive Erhöhung der Parameterzahlen und Rechenleistungen zu kompensieren, erfordern aktuelle Sprachmodelle mit geringer Parameterzahl – typischerweise unter drei Milliarden Parametern – eine hochgradig kontrollierte Token-Kuration1. Solche Low-Parameter-Modelle besitzen nicht die kapazitativen Redundanzen, um irrelevante Web-Strukturen, Navigationsleisten, SEO-Spam oder repetitive Phrasen in ihren Gewichtungen zu kodieren3. Jeder während der Pre-Training-Phase verarbeitete Token muss einen maximalen Beitrag zur semantischen, logischen oder syntaktischen Modellbildung leisten2.  
Die Definition von Datenqualität wurde hierfür in einem vierstufigen Qualitätsrahmen operationalisiert:

1. **Informationsdichte:** Der semantische Gehalt eines Dokuments muss reich an verifizierbaren Fakten, konzeptuellen Rahmenwerken oder struktureller Logik sein, statt oberflächliche Repetitionen aufzuweisen3.  
2. **Pädagogischer Wert:** Der Textkörper muss didaktisch wertvolle Erklärungen liefern, akademische oder praktische Problemstellungen lösen oder reproduzierbare Ausführungsmuster (analog zu Lehrbüchern) aufzeigen4.  
3. **Syntaktische Sauberkeit:** Daten müssen frei von strukturellem Web-Rauschen sein, darunter HTML-Überreste, unvollständig geparste Markdown-Steuerzeichen, Log-Dateien oder Cookie-Banner4.  
4. **Reasoning-Signal:** Der Text muss eine klare kausale Argumentationskette, mathematische Beweisführungen oder deterministische Code-Ausführungspfade demonstrieren3.

Um diese Kriterien auf Milliarden von Web-Dokumenten anzuwenden, greifen moderne Curation-Pipelines auf automatisierte heuristische Filter, globale Fuzzy-Deduplizierungsverfahren und modellbasierte Qualitätsklassifikatoren zurück4. Das übergeordnete Ziel besteht darin, Rohdatenströme so zu transformieren, dass sie durch Deduplizierung, lehrbuchartige Reformatierung und Code-Strukturierung als hochgradig verdichtete Lerneinheiten vorliegen3.

## **Systemischer Vergleich führender Datensätze**

Um die Verteilung verschiedener Token-Quellen im modernen Open-Source-Ökosystem zu verstehen, ist ein direkter Vergleich ihrer strukturellen Eigenschaften erforderlich. Die folgende Matrix vergleicht die etabliertesten Datensätze anhand des vierstufigen Qualitätsrahmens.

| Datensatz | Informationsdichte | Pädagogischer Wert | Syntaktische Sauberkeit | Reasoning-Signal | Hauptanwendungsbereich |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **FineWeb** \[cite: 4, 6\] | Moderat; enthält noch signifikantes Web-Rauschen4. | Gering; ungerichtet extrahierte Webseiten4. | Hoch; durch hochentwickelte Trafilatura-Extraktion4. | Moderat; abhängig vom spezifischen Quell-Domain-Muster4. | Allgemeines Weltwissen und linguistische Diversität4. |
| **FineWeb-Edu** \[cite: 1\] | Sehr hoch; filtert gezielt Fakten und Theorien1. | Extrem hoch; optimiert auf Schul- und Hochschulniveau4. | Hoch; erbt die robuste syntaktische Basis von FineWeb4. | Hoch; fördert kausales und strukturelles Denken1. | Wissensintensive und schlussfolgernde Benchmarks1. |
| **DCLM-Baseline** \[cite: 3, 8\] | Hoch; stark gefilterter Web-Korpus3. | Hoch; konkurrenzfähig mit FineWeb-Edu3. | Sehr hoch; durch optimierte statistische Reinigung8. | Moderat; Fokus liegt auf allgemeinsprachlicher Abdeckung3. | Allgemeines Sprachverständnis und Zero-Shot-Evaluierung3. |
| **The Stack v2** \[cite: 9, 10\] | Extrem hoch; konzentrierter Quellcode aus Software Heritage9. | Sehr hoch; enthält funktionale Programmierkonzepte10. | Sehr hoch; filtert Dokumentation und Markup-Strukturen9. | Extrem hoch; bildet deterministische Logikpfade ab3. | Code-Generierung, Logik-Training und Algorithmenverständnis3. |
| **Cosmopedia v2** \[cite: 13, 14\] | Extrem hoch; synthetisch generiert ohne Web-Fluff13. | Extrem hoch; gezielte Abdeckung des gesamten Weltwissens13. | Perfekt; direkte Generierung durch Instruktionsmodelle13. | Sehr hoch; strukturierte Erklärungen und Code-Beispiele13. | Token-effizientes Pre-Training für Kleinstmodelle13. |

## **Eingehende Korpus-Analysen und Kuration-Spezifikationen**

### **\[Dataset Profile: FineWeb-Edu\]**

* **Estimated Quality Score (1-5):** 4.51  
* **Primary Domain:** Academic / General Knowledge4  
* **Parameter Capacity Target:** Optimal geeignet für ressourcenbeschränkte Modelle von \<1B bis \<3B Parametern1.

Der FineWeb-Edu-Datensatz ist das Ergebnis einer rigorosen, qualitätsgesteuerten Filterung des 15-Billionen-Token-starken FineWeb-Korpus1. Durch den Einsatz eines spezialisierten Klassifikators wurde das Web-Rauschen um zweiundneunzig Prozent reduziert, was eine verbleibende Basis von 1,3 Billionen hochgradig informativen Token hinterlässt1.  
Die Untersuchung dieses Datensatzes anhand des vierstufigen Qualitätsrahmens offenbart eine außergewöhnliche Konzentration an didaktisch aufbereiteten Konzepten4. Die Informationsdichte ist durch das systematische Aussortieren von Marketing-Inhalten, Produktbewertungen und Foren-Interaktionen maximiert4. Der pädagogische Wert ist extrem hoch, da die verbleibenden Webseiten primär strukturierte Lehrinhalte vermitteln1. Syntaktisch glänzt der Datensatz durch die Verwendung des Trafilatura-Parsers, welcher im Gegensatz zu standardmäßigen WET-Dateien strukturelle Formatierungen beibehält4. Das Reasoning-Signal ist auf die Vermittlung logischer Konzepte ausgelegt, obgleich es im Bereich der harten mathematischen Beweisführung Limitierungen aufweist4.

### **\[Refinement Strategy\]**

Die Kuration erfordert eine Kaskade aus heuristischen Filtern, Sprachfiltern und einem hochentwickelten neuronalen Klassifikator:

* **Sprachfilterung:** Einsatz des fastText-Bibliotheksmodells zur Identifikation der Zielsprache Englisch mit einer Konfidenzschwelle von ![][image1]4.  
* **Gopher-Repetitionsfilter:** Eliminierung von Dokumenten mit mehr als dreißig Prozent duplizierten Zeilen oder wenn die fünf am häufigsten auftretenden 5-Gramme mehr als zwanzig Prozent des gesamten Textes abdecken4.  
* **Qualitätsheuristiken:** Aussortieren von Webseiten, deren durchschnittliche Wortlänge außerhalb des Intervalls ![][image2] liegt oder deren Symbol-zu-Wort-Verhältnis ![][image3] überschreitet3.  
* **MinHash-Deduplizierung:** Durchführung einer fuzzy-basierten Deduplizierung mittels datatrove mit 5-Grammen und 112 Hash-Funktionen, aufgeteilt auf 14 Buckets mit je 8 Hashes, um Dokumente mit einer Jaccard-Ähnlichkeit von ![][image4] effektiv zu entfernen19.  
* **Modellbasierte Filterung:** Klassifikation der verbleibenden Dokumente über ein Snowflake/snowflake-arctic-embed-m-Modell mit angehängtem Regressionskopf4. Dokumente mit einem prädizierten Score von ![][image5] (auf einer Skala von 0–5) werden vollständig verworfen1.

### **\[Synthetic Text Exemplar\]**

Das folgende synthetische Textbeispiel demonstriert die strukturelle Verdichtung komplexer mathematischer Sachverhalte zur Erzielung einer maximalen Token-Effizienz:  
Die mathematische Formulierung der Principal Component Analysis (PCA) dient der dimensionalen Reduktion eines hochdimensionalen Datenraums unter maximalem Erhalt der Varianz. Gegeben sei eine zentrierte Datenmatrix ![][image6], deren empirischer Mittelwert pro Merkmal auf null normiert ist. Die empirische Kovarianzmatrix ![][image7] berechnet sich über die Formel:  
![][image8]  
Die Kovarianzmatrix ![][image9] ist per Definition symmetrisch und positiv semidefinit. Durch die Spektralzerlegung (Eigenwertzerlegung) dieser Matrix bestimmen wir die orthogonalen Richtungen maximaler Varianz:  
![][image10]  
Hierbei repräsentiert ![][image11] die orthogonale Matrix der Eigenvektoren (Hauptkomponenten), während ![][image12] eine Diagonalmatrix darstellt, welche die entsprechenden Eigenwerte in absteigender Reihenfolge ![][image13] enthält. Jeder Eigenwert ![][image14] entspricht der durch die Hauptkomponente ![][image15] erklärten Varianz. Um den Datenraum auf ![][image16] Dimensionen zu projizieren, konstruiert man die reduzierte Projektionsmatrix ![][image17] aus den ersten ![][image18] Spalten von ![][image19]. Die Transformation der ursprünglichen Datenpunkte in den niedrigdimensionalen Raum erfolgt durch die lineare Projektion:  
![][image20]  
Dieser Formalismus stellt sicher, dass die rekonstruierten Datenpunkte den minimalen mittleren quadratischen Fehler bezüglich der Originaldaten aufweisen. Durch diese mathematische Strukturierung wird redundante Prosa vollständig eliminiert und die informationelle Dichte maximiert.

### **\[Dataset Profile: The Stack v2 (Code-Domain)\]**

* **Estimated Quality Score (1-5):** 4.23  
* **Primary Domain:** Code / Logic3  
* **Parameter Capacity Target:** Optimiert für logikfokussierte Modelle von \<3B Parametern (z. B. StarCoder2-3B)9.

The Stack v2 basiert auf dem digitalen Archiv von Software Heritage (SWH) und deckt Quellcode in über 600 Programmiersprachen ab9. Im Kontext von Low-Parameter-Modellen fungiert Programmiercode nicht primär als Werkzeug zur Synthese von Skripten, sondern als logisches Strukturtraining, das die Fähigkeit zur sequenziellen Pfadverfolgung schärft3.  
Hinsichtlich der Informationsdichte weist Quellcode eine extrem geringe Entropie auf, da syntaktische Fehler die Ausführung verhindern22. Der pädagogische Wert ist hoch, weist jedoch Schwachstellen auf: Ungefilterte Repositories enthalten oft veraltete, unsichere oder redundante Codebasen11. Analysen zeigen, dass siebzehn Prozent der im Datensatz enthaltenen Codeversionen veraltet sind, wobei ein signifikanter Teil bekannte Sicherheitslücken (CVEs) enthält11. Die syntaktische Sauberkeit wird durch Lizenzfilterungen und das Entfernen von Boilerplate-Code (wie leeren Klassen oder Autorengenerierten Headern) sichergestellt10. Das Reasoning-Signal ist bedingt durch die inhärente logische Konsistenz von Compilern und Interpretern auf einem maximalen Niveau3.

### **\[Refinement Strategy\]**

Die Transformation von Rohcode in pre-training-taugliche Strukturen erfordert tiefe syntaktische Eingriffe:

* **Lizenz- und Opt-Out-Filterung:** Ausschluss aller Repositories, die keine permissiven Lizenzen (z. B. MIT, Apache 2.0, BSD) aufweisen oder vor dem Kuration-Cutoff aus Datenschutzgründen entfernt wurden10.  
* **Parserbasierte Syntaxvalidierung:** Durchlauf eines leichtgewichtigen Abstract-Syntax-Tree-Parsers (AST), um fehlerhafte Quellcodedateien, die Compiler- oder Linter-Fehler aufweisen, frühzeitig zu eliminieren22.  
* **In-Dokument-Deduplizierung:** Entfernung von duplizierten Absätzen und sich wiederholenden Strukturblöcken innerhalb einzelner Dateien mittels zeilenbasierter MD5-Hashing-Kompression3.  
* **Verallgemeinerte PII-Reduzierung:** Regex-basierte Anonymisierung von E-Mail-Adressen, IP-Adressen, privaten SSH-Schlüsseln und geheimen API-Tokens zur Wahrung der Datensicherheit6.

### **\[Synthetic Text Exemplar\]**

Das folgende syntaktische Textbeispiel demonstriert die hochgradig strukturierte Code-Ausrichtung, implementiert als syntaktisch valider und vollständig kommentierter Python-Algorithmus zur Berechnung von MinHash-Signaturen:

Python  
import hashlib

def generate\_minhash\_signature(tokens: list\[str\], num\_permutations: int \= 128\) \-\> list\[int\]:  
    """  
    Berechnet eine dichte MinHash-Signatur fuer ein gegebenes Token-Dokument.  
    Diese mathematische Abbildung transformiert variable Textstrukturen  
    in einen niedrigdimensionalen Vektor kompakter Hash-Sollwerte.  
    """  
    \# Initialisierung der Signatur mit unendlichen Distanzwerten  
    signature \= \[float('inf')\] \* num\_permutations  
      
    \# Iteration ueber jedes Token im bereinigten Eingabedokument  
    for token in tokens:  
        \# Kodierung des Tokens in ein Byte-Format fuer kryptografisches Hashing  
        token\_bytes \= token.encode('utf-8')  
          
        \# Berechnung des primären MD5-Hashwerts als Basis-Zustandsvektor  
        base\_hash \= hashlib.md5(token\_bytes).hexdigest()  
        base\_val \= int(base\_hash, 16\)  
          
        \# Simulation von N orthogonalen Permutationen mittels linearer Kongruenz  
        for i in range(num\_permutations):  
            \# Erzeugung eines permutationsspezifischen unikalen Hash-Wertes.  
            \# Koeffizienten simulieren unkorrelierte Zufallsprojektionen.  
            permuted\_hash \= (base\_val ^ (i \* 0x45d9f3b)) & 0xffffffff  
              
            \# Suche nach dem globalen Minimum gemaess der MinHash-Definition  
            if permuted\_hash \< signature\[i\]:  
                signature\[i\] \= permuted\_hash  
                  
    return signature

### **\[Dataset Profile: Cosmopedia v2 (Synthetischer Korpus)\]**

* **Estimated Quality Score (1-5):** 4.83  
* **Primary Domain:** Academic / General Knowledge13  
* **Parameter Capacity Target:** Perfekt optimiert für hochgradig kompakte Modelle von \<1.5B Parametern (z. B. Phi-1.5 oder SmolLM)15.

Der synthetische Korpus Cosmopedia v2 wurde entwickelt, um das gesamte in traditionellen Web-Datensätzen enthaltene Weltwissen mithilfe mächtiger Instruktionsmodelle (Mixtral-8x7B) in ein strukturiertes Lehrbuchformat zu übersetzen13. Dadurch wird das bei realen Webtexten unvermeidbare informationelle Rauschen eliminiert13.  
In puncto Informationsdichte erreicht Cosmopedia v2 die höchste Punktzahl, da die erzeugten Lehrbücher, Blogbeiträge und Schritt-für-Schritt-Anleitungen keinen unstrukturierten Fluff enthalten13. Der pädagogische Wert ist exzellent; die Texte sind gezielt darauf ausgerichtet, komplexe wissenschaftliche, mathematische oder gesellschaftliche Konzepte didaktisch sauber zu erklären13. Syntaktisch weist der Datensatz keinerlei Web-Rauschen, kaputte HTML-Fragmente oder unvollständige Sätze auf, da die Token-Generierung direkt über saubere Formatvorlagen gesteuert wurde13. Das Reasoning-Signal ist durch die strukturierte, logisch aufeinander aufbauende Natur der synthetischen Prompts außergewöhnlich stark ausgeprägt13.

### **\[Refinement Strategy\]**

Da es sich um einen künstlich generierten Datensatz handelt, unterscheidet sich die Bereinigungsstrategie grundlegend von Web-Scraping-Pipelines:

* **Dekontaminations-Sweeps:** Abgleich aller synthetischen Dokumente gegen die Validierungs- und Test-Sets gängiger Benchmarks (MMLU, ARC, HellaSwag) mittels eines 10-Gramm-Überlappungs-Scans13. Bei einer Übereinstimmung von mehr als fünfzig Prozent (ermittelt via SequenceMatcher) wird das gesamte Dokument rigoros entfernt, um Data Leakage zu verhindern13.  
* **Stilistische Diversifizierung:** Steuerung der Textgenerierung über fünf vordefinierte Stilebenen (Akademisch, Instruktionell, Narrativ, Praktisch und Elementar), um ein breites Spektrum an linguistischer Varianz aufzubauen24.  
* **Syntaktische Formatierungskontrolle:** Erzwingen von Markdown-Konstrukturen, mathematischen LaTeX-Umgebungen und expliziten Code-Blöcken direkt über das Prompt-Design, um eine einheitliche Syntax zu garantieren24.

### **\[Synthetic Text Exemplar\]**

Das folgende synthetische Textbeispiel repräsentiert eine hochgradig token-effiziente Lehrbucheinheit im Stil von Cosmopedia zur Vermittlung komplexer Molekularbiologie:  
Die eukaryotische Transkription beschreibt den biochemischen Prozess, durch welchen genetische Information von einer doppelsträngigen DNA-Vorlage in eine einzelsträngige Messenger-RNA (mRNA) übersetzt wird. Dieser enzymatisch gesteuerte Vorgang vollzieht sich im Zellkern und unterteilt sich in drei diskrete Phasen: Initiation, Elongation und Termination.  
Während der Initiation erkennt das Enzym RNA-Polymerase II spezifische DNA-Sequenzen, sogenannte Promotoren, die dem Zielgen vorgeschaltet sind. Der bekannteste Promotor ist die TATA-Box, welche etwa 25 Basenpaare stromaufwärts der Transkriptionsstartstelle liegt. Transkriptionsfaktoren binden an diese Sequenzen und rekrutieren die RNA-Polymerase, wodurch der Transkriptionsinitiationskomplex entsteht. Das Enzym entwindet die DNA-Doppelhelix und legt einen einzelsträngigen Matrizenstrang frei.  
In der Elongationsphase bewegt sich die RNA-Polymerase entlang des Matrizenstrangs in 3'-zu-5'-Richtung. Sie synthetisiert komplementär dazu einen RNA-Strang in 5'-zu-3'-Richtung, indem sie freie Ribonukleosidtriphosphate (NTPs) kovalent miteinander verknüpft. Dabei wird das Nukleotid Adenin mit Uracil gepaart, während Cytosin mit Guanin bindet.  
Die Termination erfolgt, sobald das Enzym eine spezifische Terminationssequenz (das Polyadenylierungssignal AAUAAA) erreicht. Spezifische Proteine schneiden die naszierende RNA-Kette ab, woraufhin sich die RNA-Polymerase vom DNA-Template löst. Die entstandene Pre-mRNA durchläuft anschließend das Spleißen, bei dem nicht-kodierende Introns entfernt und kodierende Exons miteinander verknüpft werden, um die translationstaugliche reife mRNA zu bilden.

## **Systemische Integration, Zielmischungen und verhaltensorientierte Risiken**

Die Kuration einzelner Datensätze stellt nur den ersten Schritt dar. Für ein erfolgreiches Pre-Training von Low-Parameter-Modellen müssen diese verschiedenen Domänen in einem präzise kalibrierten Token-Gemisch zusammengeführt werden3. Am Ende dieses Prozesses steht häufig eine so genannte Annealing-Phase (Feinschliff-Phase), in welcher das Modell in den letzten zehn Prozent des Trainingsprozesses auf eine extrem gefilterte Auswahl fehlerfreier und hochqualitativer Token hin optimiert wird3.

  \[Pre-Training Start\] (Trillionen Token Mix)  
         │  
         ├──► 65% FineWeb-Edu (Wissensbasis) \[cite: 1, 3, 16\]  
         ├──► 20% StarCoder2 (Logik- & Strukturtraining)  
         ├──► 10% Cosmopedia v2 (Faktenkonsolidierung)  
         └──► 5% FineMath (Formale Abstraktion) \[cite: 3, 22\]  
         │  
         ▼  
  \[\~90% Trainingsfortschritt\]  
         │  
         ▼  (Uebergang zur Annealing-Phase)  
 ┌────────────────────────────────────────────────────────┐  
 │ Annealing-Mischung:                                    │  
 │ Exklusive Fokussierung auf hochreine, synthetische     │  
 │ Lehrbuecher, fehlerfreien Code und formale Beweise.    │  
 └─────────────────────────┬──────────────────────────────┘  
                           │  
                           ▼  
                  \[Finalisierte Gewichte\]

Dieses strategische Mischungsverhältnis minimiert das Risiko, dass ein Modell zwar hervorragende akademische Leistungen erbringt, jedoch elementare Alltagskompetenzen vermissen lässt4. Zwei wesentliche systemische Schwachstellen müssen beim Design solcher hochgradig kuratierten Pre-Training-Mischungen besonders berücksichtigt werden:

### **1\. Das "Stil-über-Substanz"-Dilemma (Wikipedia-Reformatierung)**

Sogenannte modellbasierte Qualitätsfilter (wie der FineWeb-Edu-Klassifikator) weisen eine signifikante Schwachstelle auf: Sie neigen dazu, formale, akademisch wirkende Präsentationsstile über den tatsächlichen sachlichen Gehalt eines Dokuments zu stellen25. Durchgeführte Untersuchungen zeigen, dass eine einfache Reformatierung von minderwertigen, ungenauen oder gar falschen Webtexten in ein strukturiertes Wikipedia-Lehrbuchformat ausreicht, um die Entscheidung des Klassifikators umzukehren25.  
Bei einem standardmäßig gewählten Filter-Schwellenwert von drei lässt der FineWeb-Edu-Klassifikator signifikante Mengen an minderwertigen Daten passieren, sobald diese in einen enzyklopädischen Schreibstil überführt wurden25. Auch andere Modelle wie der NemoCurator Mixtral Edu Klassifikator weisen diese Anfälligkeit auf, indem sie über sieben Prozent stilistisch aufbereiteter, aber inhaltlich wertloser Dokumente fälschlicherweise akzeptieren25. Dies erfordert eine Kombination aus Stilfiltern und expliziten Faktencheck-Filtern, um eine Kontamination der Modellgewichtungen zu verhindern.

### **2\. Der "Commonsense-Depletion"-Effekt (Verlust des gesunden Menschenverstands)**

Eine zu aggressive Selektion pädagogisch wertvoller Token führt zu einer schlechteren Leistung bei Aufgaben, die allgemeines Weltwissen und physisches Alltagsverständnis erfordern1. Wenn der Schwellenwert für den Einlass von Dokumenten restriktiv über drei angehoben wird, steigen zwar die Ergebnisse bei wissensintensiven Benchmarks wie MMLU und ARC sprunghaft an1. Gleichzeitig sinkt jedoch die Leistung bei Benchmarks wie HellaSwag und PIQA dramatisch ab1.  
Dieses Verhalten rührt daher, dass physische Interaktionen und implizite Alltagserfahrungen selten in wissenschaftlichen Lehrbüchern dokumentiert sind, sondern sich primär in informellen Forendiskussionen, narrativen Webtexten und alltäglichen Beschreibungen finden4. Wird dieser informelle Web-Sektor durch zu restriktives Filtern vollständig eliminiert, verliert das Modell seine basale Verankerung in der physikalischen Alltagswelt4.

## **Synthese und strategische Handlungsempfehlungen**

Für den praktischen Entwurf einer Token-Kurations-Pipeline zur Ausbildung leistungsstarker Low-Parameter-Modelle lassen sich die folgenden Empfehlungen ableiten:

* **Hybrides Filterdesign:** Das ausschließliche Vertrauen auf neuronale Qualitätsklassifikatoren ist aufgrund des "Stil-über-Substanz"-Dilemmas riskant25. Eine robuste Pipeline muss statistische Heuristiken (wie Wortverteilungen und Symbol-zu-Wort-Verhältnisse) untrennbar mit modellbasierten Bewertungen verknüpfen3.  
* **Dynamische Mischungs-Muster:** Der Pre-Training-Korpus sollte nicht homogen gefiltert werden. Stattdessen ist eine geschichtete Mischung ratsam, bei der ein hoher Anteil an hochreinem Lehrbuch- und Code-Material (etwa 70 bis 80 Prozent) mit einem bewusst unschärfer gefilterten Anteil an allgemeinem Web-Text (etwa 20 bis 30 Prozent) kombiniert wird, um das allgemeine commonsense-Verständnis abzusichern1.  
* **Gezieltes Annealing zum Trainingsende:** Das Modell sollte in der initialen Trainingsphase mit einer breiten Vielfalt konfrontiert werden, um ein robustes Sprachverständnis aufzubauen3. In den finalen Trainingsschritten (den letzten 10 Prozent der verarbeiteten Token) sollte die Datenzufuhr rigoros auf fehlerfreie, synthetisch generierte Lehrbücher und syntaktisch perfekten Programmcode verengt werden3. Dieses Vorgehen führt zu einer erheblichen Performanzsteigerung auf akademischen Benchmarks, ohne die linguistische Flexibilität zu beeinträchtigen.

#### **Referenzen**

1. FineWeb: decanting the web for the finest text data at scale \- a Hugging Face Space by HuggingFaceFW, [https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1](https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1)  
2. (PDF) Textbooks Are All You Need \- ResearchGate, [https://www.researchgate.net/publication/371729045\_Textbooks\_Are\_All\_You\_Need](https://www.researchgate.net/publication/371729045_Textbooks_Are_All_You_Need)  
3. ai-basics/04-data.md at main \- GitHub, [https://github.com/bidyashish/ai-basics/blob/main/04-data.md](https://github.com/bidyashish/ai-basics/blob/main/04-data.md)  
4. FineWeb: HuggingFace's 15-trillion-token web corpus \- ZeroEntropy, [https://zeroentropy.dev/concepts/fineweb/](https://zeroentropy.dev/concepts/fineweb/)  
5. utils/prompt.txt · HuggingFaceFW/fineweb-edu-classifier at main, [https://huggingface.co/HuggingFaceFW/fineweb-edu-classifier/blob/main/utils/prompt.txt](https://huggingface.co/HuggingFaceFW/fineweb-edu-classifier/blob/main/utils/prompt.txt)  
6. A FineWeb Datasheet, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/370df50ccfdf8bde18f8f9c2d9151bda-Supplemental-Datasets\_and\_Benchmarks\_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/370df50ccfdf8bde18f8f9c2d9151bda-Supplemental-Datasets_and_Benchmarks_Track.pdf)  
7. fineweb-edu-score-2 \- ModelScope, [https://modelscope.cn/datasets/HuggingFaceFW/fineweb-edu-score-2](https://modelscope.cn/datasets/HuggingFaceFW/fineweb-edu-score-2)  
8. 1 Introduction \- arXiv, [https://arxiv.org/html/2502.10361v1](https://arxiv.org/html/2502.10361v1)  
9. StarCoder2 and The Stack v2: The Next Generation \- arXiv, [https://arxiv.org/pdf/2402.19173](https://arxiv.org/pdf/2402.19173)  
10. bigcode/the-stack-v2 · Datasets at Hugging Face, [https://huggingface.co/datasets/bigcode/the-stack-v2](https://huggingface.co/datasets/bigcode/the-stack-v2)  
11. Cracks in The Stack: Hidden Vulnerabilities and Licensing Risks in LLM Pre-Training Datasets \- Audris Mockus, [https://mockus.org/papers/CuratingLLM.pdf](https://mockus.org/papers/CuratingLLM.pdf)  
12. \\emojidizzyStarCoder 2 and The Stack v2: The Next Generation \- arXiv, [https://arxiv.org/html/2402.19173v1](https://arxiv.org/html/2402.19173v1)  
13. HuggingFaceTB/cosmopedia · Datasets at Hugging Face, [https://huggingface.co/datasets/HuggingFaceTB/cosmopedia](https://huggingface.co/datasets/HuggingFaceTB/cosmopedia)  
14. Build Prompt — LLM Research Kit: one self-contained ... \- GitHub Gist, [https://gist.github.com/vukrosic/8a273d6d07b1e40ab752ab969dc474d1](https://gist.github.com/vukrosic/8a273d6d07b1e40ab752ab969dc474d1)  
15. Phi-1.5: Specifications and GPU VRAM Requirements \- ApX Machine Learning, [https://apxml.com/models/phi-1-5](https://apxml.com/models/phi-1-5)  
16. SmolLM2: When Smol Goes Big — Data-Centric Training of a Small Language Model \- arXiv, [https://arxiv.org/html/2502.02737v1](https://arxiv.org/html/2502.02737v1)  
17. Improving Romanian LLM Pretraining Data using Diversity and Quality Filtering \- arXiv, [https://arxiv.org/html/2511.01090v1](https://arxiv.org/html/2511.01090v1)  
18. llm-foundry/data/cc/process\_cc\_dump\_with\_quality\_filters ... \- GitHub, [https://github.com/Polygl0t/llm-foundry/blob/main/data/cc/process\_cc\_dump\_with\_quality\_filters.py](https://github.com/Polygl0t/llm-foundry/blob/main/data/cc/process_cc_dump_with_quality_filters.py)  
19. ArabicWeb24: Creating a high quality Arabic Web-only pre-training dataset \- LightOn AI, [https://lighton.ai/lighton-blogs/arabicweb24](https://lighton.ai/lighton-blogs/arabicweb24)  
20. nvidia/nemocurator-fineweb-mixtral-edu-classifier \- Hugging Face, [https://huggingface.co/nvidia/nemocurator-fineweb-mixtral-edu-classifier](https://huggingface.co/nvidia/nemocurator-fineweb-mixtral-edu-classifier)  
21. README.md · HuggingFaceFW/fineweb-edu-classifier at 215da67c4a971c69275c72e57f639cc7b2ce23b1, [https://huggingface.co/HuggingFaceFW/fineweb-edu-classifier/blob/215da67c4a971c69275c72e57f639cc7b2ce23b1/README.md](https://huggingface.co/HuggingFaceFW/fineweb-edu-classifier/blob/215da67c4a971c69275c72e57f639cc7b2ce23b1/README.md)  
22. Papers Explained 571: Olmo 3 \- Ritvik Rastogi, [https://ritvik19.medium.com/papers-explained-571-olmo-3-1ee7134a4e67](https://ritvik19.medium.com/papers-explained-571-olmo-3-1ee7134a4e67)  
23. Primers • Overview of Large Language Models \- aman.ai, [https://aman.ai/primers/ai/LLM/](https://aman.ai/primers/ai/LLM/)  
24. What Datasets Are Available for Chinese Large Models? Here's Our Complete Comparative Analysis | by OpenCSG | Medium, [https://medium.com/@OpenCSG/what-datasets-are-available-for-chinese-large-models-heres-our-complete-comparative-analysis-0c0ad2bff74f](https://medium.com/@OpenCSG/what-datasets-are-available-for-chinese-large-models-heres-our-complete-comparative-analysis-0c0ad2bff74f)  
25. Is a Document Educational or Just Wikipedia-Style? – Pitfalls of Classifier-Based Quality Filtering \- arXiv, [https://arxiv.org/pdf/2605.23721](https://arxiv.org/pdf/2605.23721)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHUAAAAaCAYAAACJphMzAAAFX0lEQVR4Xu2Zd6gkRRCHf+acA+YzJxQxYUA9UTGLCRMqJtADFRX/MONhzogK5oABc8Qc14Q5gDkh5oAZFbPWR03v9tbb2Zu3u7dPdD74wZvqnp2e6eqq6n5STU1NTc1/gOVMd0TjgLjetHo01kxe5jK9YVo2NgyIhUyvmOaPDWPAVKaJppdMT5ruNi2dd5gEq5keML1oes60WXuzJpi2MM1tmsm0tulW01p5p2FwlenoaBww+5nuj8Yx4EzTy6aZi2sm4TPTPM0e5Wxi+sq0UXG9q+lb07TNHtLjpr+D7gp9KoNHsBq+k//Ql/LV97rpLdPHpvNMc6YbCpY3/axqL9UPM5q+kY9zrCBi/GbaJbNNIZ/UEzNbJ/huX5sOy2zPyr/14pmtYXpT/r2fkDvzlFl7T9wmfxA5Mmcl+eQ9HeznyHPeMMCpbonGEg41XaT2D9Yv+8u/zYrB3pA7fzeYdO5dILNtZzpB7hiJh0yLZtd9g0ewGj6JDQV4EANbIbPhUQdk16NlNF64s+kHeV6rAnnoPtPlpiVCWy9cIn//ccF+u+kv0wzBnsOkfx6NHXhQA55UkjiDvjI2yJP2r6Y/TPMVtgXl/csq0zXknkdB8YzpGNM0hXAQ8ssX8gLrannO/NC0Fzd3YDF1f14Z4+Xj6HdyyW08PxZsNxb2sqgwq7ydXLyv/HdeNV2sVm5OUEQdZLpHXkhRiPVVgB4hf/gescHYW95GSEtsXthmy2wJVgnhetPiel55BDheHm4Y6MNFHzydF4dT5Hkr5u7E76Y9o7EiG5geUe+Ty728b3LqBOkHOymqE0vJ26lXji1s05ue18htIJHlLLUiGOH5U7WH7VHBR+bhC2e2qU3by5P8pWqvwlhRf6o9JyQo2WP+PV2+OhPnyp+3fmbbqbCtl9lyuJ982Q9Un4+aLpOv/qo01NukkoNpxyFnyewHF3acLUHhmaekFJ3OzmyVobr8Rb5y7s30lOl807qtrk0YFCV5hCqRgTABTGwSIecjtXIPA6Vf/qI4UHzRnHdNJ0VjjxBFqPhPjg0llIXfGwr7ksGeoD/tpJwctjTYzwj2HOoH+rwdG6rAC3Iz3lsVYn+nSV1Z/lvXxIYAez76EYoS2xa2DTNbDpNKiO4XJuAKeXRap72plAvlY4urm/SBvaxQooagFnkh2Cn88m/OoQOF4I7NHg5F2I/BVgniOA8g/FVld3UOv+RDfouk3w08dLSTyuon9/cKxQwfsaHWIUBVJsjHtmqwUwjGVRhhzxm3PbvJfy/tcScW10elDvIIiu2dzFaZ1+QTVFagdKJbodSQe1ceWoEjr+mKv1P47TSpZR+cvLRPNFaA1UVNwInNxqGtKhQrrDjCZoJViKPlKYFjU/rQluDQ4Se13h2YvNxJtpGv+nzLtqa8T9UU0WQR+Y2ccIyGdF+nLQYJ/3t5CMbbAM88tdlDukAjnWKHwrZlZkukomGV2NCFcfKK/TG1KvF+IGVw7jt7cX24/ERpjmYP6Sb5OA/MbLwj9QTVP5Bn35Mf3iQokFjRWxXXPIOCjhUeF0cpbDs4CkxHg3gSK3brvNMkeF/lhw8cdN8s38pQvp8m90IqaO4jMvBcKutD5KuYMWCjYIs5mRzE6q9yDkqFyglUQ37mOigY/3HyAot95J0amWOPlNca44OdbRTFFnvxD+QrNaYutn7XymsHDnY48OBwf6hQGfdyTEjITS+UJjq34bV5qAIm6bpgK4Pt1iAn838Fq5HVNawD/bL9a82A4Ygvr9gmB/y3gn1zzZCgCOAEaZnYMCA4zGDzTWFWM0QIw/Ecc1CQR/nnQE1NTU1Nzb+RfwBIlDhpOqAHvwAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAZCAYAAACclhZ6AAACn0lEQVR4Xu2XS6hNYRTHVx4zGchrQN0JyWNgilKU10AyQXlcYoAkiTJyU8pIqdstKWVATAwomahV8spjojzKKwMyIEKe4b/u+vZpnX/fV3urezqD86t/fev37bPPXvvsx3dEevToKBeR28hZnugS9osf33OeyKEswGzkCvIAeYycRia0bdGcPhaBdchd5DpyC1nRPj2MssihVE8WPwvzUz0VeY88QsZUG9VkLDILOY58pLmK1chXZGaq7Xs/I4tbWzhKdRaluh/5i5wJzn4lc/bFdZknfhLsTL9GvrRPt7CTdJLceeQGOaU6i1K9DPmDDAZ3VbyZVcE1wT6fa2aO+H73kB9IfkpwGsZFlAWYhIxK49HIO+QDMr61RTNKzWwUP+gt5Pclvzw4DeMiyiJg98gR5CeyhuaaUGrmgPhBbyC/O/ltwWkYF1EWCTs7T5EfyC6aa0qpmcPiB72e/M7k9wanYVxEWRB9yFvknPjT6X8oNTMgHW7GsEvNdn6QJ2pizdjjlyldZnYlmN8enIZxEaV6uvgTLdIvvvP75OtizXxjKd6E7Xcr+eoBEF+eGsZFlOon4jtaG9yO5B4G1wRr5jtL8Req7deWLJGjydsLu0LDuIhSbc38RhYGd0x85yeCm4Zslnr3kTVjD5Ic9tI8Re4ScpOcUp1Fqbabz9ZkM1Jtl90b5CUysdoIXBZv8FBwJa4hvyTfuK0qPiFzU71A/FWwqLWFo1RnURZgk3hDr8TXaUPia7aINWHrLVt157DGn4mfCGvaYtub44WkPc3s++6I/yJL26eHURY5lEUDxiEXWI4QyiKHsmjASvHLshMoixzKoia2ZrMbNd5HI4myyKEsarJE/E9Vp1AWOewGvif+H6IbsVWCHd8LnujR7fwD1+aen0YAgfUAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACUAAAAZCAYAAAC2JufVAAABmElEQVR4Xu2VPShGURzG/waLhXyVkow+IpQy8S6K1SCLrBaLj1AWFiajmESMMigMxKCUgUFJkUKJRAafSTz/zrk693HP+xpeZbi/+g33+Z/uebr3vecViYn5O2rgFtyB+7APZoRWpCYLFnIYQSkHUZTAe9hpr3PhERz5XpEcXd8GD2E/zQIyYRmchA80i2QKHlPWDZ9gNuXMIryAG/BToktVwTu4K2btY3j8E31FN3CJ8oSYTdop99Eg/lIu6/KLUsVibjZLea3Nxyn3kdZS9WJuNkN5pc3nKfeR1lJNYm42TXm5zZcp95HWUgn5h6V8r6/C5guU+whKDfCA0FL6VSelSMzN5igPfugTlPsISg3ygNBSLxxGcQ1XKGsWs0kH5T6CUkM8ILTUK4dR6OF5QlkvfIY5TqZfZKtz7RKUGuYBoaXeOIxCzyo9+rvsdQG8lPAGesjeitm42skDGsXMRnlAbMJ3MX87KamD23APHsCe0NSwBs9gnpON2Uyfqpb6gOdw1VmTD0/hlV2j6kPQrMVZFxMTE8N8AduKadpUdeu2AAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADoAAAAZCAYAAABggz2wAAACrklEQVR4Xu2XS6hNURzGP+93uXlLuYRuSpQJUh4jEpkQMTJBLjJBMTjkkUQmFJkwERLKI+/jWTKglIQBJSaUZCTh+/rvfa39P/tsex8nA/avfoP7rdXZa6291tr/C5SUlPyvdKEV+pjep5fouLBDHdTnCW3xDY5VdB4dSPvQafQsnRp2+hvsgw24b/S3BvaeDurokc4c+iPD1VG/uyltF2n3qD2VWfQYneQbGmQE/UqXBlkn2ER3Blkamsg3+oG+o28jP9I3tH/Ur0qfR2336EraOWrLZDw9Ti/QmcmmwqyBrfAEl1fpM5d59tL5LtMiaVwzguwGbQ3+LkwrPURv0QWwhxTlKGyiI11+nn6nvVwesg127kLW0h0uu44/nGjMELqHPqDLaddkcyY6K5roMJefjvLRLs9iLL2D2udfo+vpZfoIdtm1JXoURGdiK30IOwc9ks2paDdoQkNdfjLKJ7o8i5t0rg/JFbofv86l3rjO9PCOHg3SGzbQ17RnsqmGKpoz0dmwS0ifKo/ulPDyGQX77QNBVhitqA7/EeTbdvW27qkoH+PyepyDbc08aDH02y98w+/Qai2Cfa/0TSyyJQ7DHqpVDtFlpDzrMorpB/tEHfQNsELhM13scl10X1xWl250BewSqtABidZ8qDjQhCa7XBWSvn150GT0GxWXiwqsbUuQ6WgpexlkqWiV18EGswFWVjWK3r4++suCTAuoImBXkOkmXYLasyw2wga+yTeQhbDdEZ7dKbD+u4OshumwC0RvUgNqBtruqnPjSmYzrDIKa9h22ODOBFmMblS1adE9OlaqhuLCQs+4DStGtOXropVppDDIQr+5nT6FfedU2fgzq1v1E+ztebQbtANUrKcxmJ6gr2BloIoUX2iU/PPof7hqTq/CbriSkpKSpvETz8qTMFITAjUAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAZCAYAAAB3oa15AAACJklEQVR4Xu2Wu2sUURTGv5ioMaIipvDRpFHsFCsFRVAMgoWdaG8lvt9/g4WFSFCw80EgWgSCGKKFpoioiUYsDAR8IIKGoKJiIYl+H2dGzx5m3NmJWs0PfrD7zd3dc+7ce2eBioqKf8Vieok+oU/pLbqmZkQ+7fQKfUgf0Yt0Qc2I/8Bdujd53UwH6Ve66teIbDT2Aaz5puT9VXrbDyrLHLqHzo0XAh30B33pspNJdtZlWeyCjVvustVJts1lDTGPHoDd0kOwmfkTS+gn+sxlp2FFnHFZFj10MmS6C1O0K+R1aaNH6WN6BNZIURbRVvf+OqyBTS7LYpy+iCFsQoZimIcKPw4r/DAaKzyLHfQ76s++0D4ZiyGZoK9jGEkLH4EtGT+DZdhMR+kXepnOrr2cyTR9HkPyjn6IYYpmOJ1xFV5vkzaKvv8O7DhdFq55tLe0zBpuYAN9CzspZjrreWyBFXczXgjkLaH39E0MPVo+J2APnoOYWSPz6U7U7p0OWANaIgtdHlHxr2II28T3Y5iFfjxtREdmmQ18AVbsOZetTDKpYzaPbvo5ZNo7+py+tzC6I8dQ7iRKGzjlsu1Jpk2d0kJ306UuSx9kK1y2Lsk6XVYYFa4GhlH8WbAWtum2wjamluMA/UY3unH7YYXdcNks/P4roddqso/2uzGlUBH76D0Ua2I97Ed1duvB1AtrzKON/RF2eHi0xK7BlrE8D1sRFRUVFRV/l58txm6uzc/GmgAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFcAAAAaCAYAAADCDsDeAAADZUlEQVR4Xu2YWahNURjHP1xzlAeEJLlkViihTJEyz6QQES+m8GCqWzyIKFKGTPFgFqEMcSUylOTJ8EApMmVMROH/v9/a53x7Pdy79znH7cT61a+z91rr7nv3Ot/6vrWuSCAQ+H9YCj/BeX5HIH9qwvewk98RiFMKW/uNYJDfYOgFX/mNhaaG3/CX6AvPwrfwBLwEX8Mz8AF8CnfDrtEPONrDvfA4nAnXwOuwmxlTF+6ALU3bAjjK3JMucBfcCMvhkXh31bSFT+BX+Nv5DHZw/ftM+w/4GNZzfdXBUfc5EU4z7Zyc/u5zsmlfJzppP+EA17YdrsiMUBrCPbAZnAOnxrsr2p/DNu7+jugXkBP8ZjmB72Ad095IdLL5YNueC7VgiTMpjFrClx9v2nvDhe6aY2q76yZwArzi7skNONrcRzQWXRGL/A6wCZ5y18y3H2DHbHd6LotO8Ax33wBegEMyI9LRGe6HN0Vf8Kro7+ALtTPjKoPLmzBqx5l2RtR6d71Z4kt8Gyxz14zAj6KRyom3TIHLRNMLg8jCv3mxu+4hmm+5YnNetfx2Obl3RR9yDg6PjUgOtyy3YD+/IyVRWvAntztc4q7PS7wW3IeD3fVs0WeMgEMzI/Rdub0iTeFOWD/bXRFUY931BnhM9J2iNJEahj8LBSf4NhwT707MMHhRsks1H6IiYieXX/xB0RXGl44ijPAdmMaiCBsoulpWZkZoEVxu7gkjv8zc9xH9UraIPp+rjsUxL/hLObmn/Y4UsDq38Btz5LD75OSyqDwU3S2wADNl5Jqyqh0WHL7MN/hdNF+lhbmNy7RQ2Mll5LLyMyWslvxTTrXB5cTiMwtuFY3etbERyeDyeiNawCoz2upVhZ9zWZS4qrhXZeSy6BY1LAasmHPdfSn8BV9K+rzJ7Rp3A4WCOZXYnMtcOx/2FN0ZFC2cWG7E/Q0ydwqM3uleexIOiB4XC4EfuREnYXPR9MB9bdHBJcw/nmnAh1sXTu49vyMBrUT3iTlvWwxRzuUpbJJpZ1rhMZfpjO/AKC4KGAUvJHusZeWNjoqEJ58vpp9jD5n+JPAAUQ5XiZ73uYdM838J/m+BJyRu3rkd47MeiaavCD6bEcwC+hmONH3/PCWiS5aFkntNTtA1Z9ITWiAQCAQCgUAgkIQ/nGulsfQib8kAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFIAAAAaCAYAAAAkJwuaAAADXklEQVR4Xu2YWaiNURTHl3mIzMosHox5ERkKyexRPCiZhRBKmWdlyJQhRC6lXMlMZOgaSxQPxuIBCQ+mJw8y/P+t9d2zLefcew7nuEf3+9Wvu89e5zvnfOvbe+29r0hMTMy/ozm8CV/7QAYMgs/gIR8ob8yBhb4zQ07Cab6zvHFaEkmoCnsHsYjusIbvNCrCT7CDDyTjLfwBP8Mn5lP43GLfLU5b2DW5Zgt8DG/Bo/AVvAbPw3fwApwJq0QXGBXgIrge7hJNQvsgvgD2C173hIuD16QO3A5Xw8OiOUiL8aJJ+gBbuhipJ/plfE+yJ5orhsKx1mYyI9rC3XCY9dcMYivhDmvz+jdBLIIJYgK7wjUuRq7CkdZeJ5rMtDkimqjrsJKLRRyDo31nmnCKVDbZTochcJK1/c0csL/94WxrN4BfYBd7zfror4vgaN0rOoJDhsP3QT/r49REuHTqwpeiyVzmYhFM4kLfmQJOuemwCN4QfcqX4EVJ/fmewZI6kftFv6M23GN9A0VnVZSE46L1kfcWwnq3FW6AnVyMI5TXEX4Ok8r3+88okT7wG/wKe7gYaSb6xEqjsWjyWKsy+gEOJqakRBKOyHnW5m++Z+0m8KNoojjdI9rAnZKYGZtFS0XEfOsjnBGsx+3gmOJ3pAmfCEcl9061XCwd+BSviCbhbxkgyRPZTbQ2ToG35deHxdrJkcY6WGBGU52r9jb7G8FRvRFWt9cNRcsca+Nc0RnFa8I6nBZ8UvxxTGZGtcHgU+QXZwMmcqK1+Zs4yu+LLiDcVSwXndp5C6fkOdGkZgq3HdyXZYMwkRyRnJYFoovKQevPW1gD70jyad0ZzvCdDhb+u6KjJ5Vri99dMjyehYkkfMgc9aPgZOvLO7ivegSb+oDBm5rlOx28UY6kbMBVe4K1o0Syvp0VPYlwCxQuFHlBK9ETDUddKriFGeE7Hbwx7r2yAUceDwskXGz6ii6KjeApWC2IlSlc9R7AcaL/MQltDXuJ/veDCxBPBKWxAi71nX8ATy7RtqMwDIhuqDuKJnWf/L6xLhM4grh3DM/UqUx2hPTwppbAM6I1l0fMTBeuTfCh6CzgaORKfUK0bpL6QewFvCx5ksxcwGnOkxATyhstMlcl3hITExMTExMTE/Mf8hMysatMfMyKYQAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAABECAYAAAA89WlXAAADJUlEQVR4Xu3dT4hVVRwH8GP2RyGxRRBkiIPSItDATaDRtgiSaOVKN4FtWhiuwlpKLVsJBUq0EoSiIox2bQozEFwpoouoASkUVCwE7ffjvDdz33FkZl4z3Dv0+cCXOfd37vy4M6vDee/eWwoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADA/9G2tgAAQP92Rv6K/BS51cwBADAwFmwAAANnwQYAMHAWbAAAA2fBBgAwcHfaAgAAw/J3WwAAYFjuRh5ri1PY2Bl/3xnPdMYAACzR05HLkT8i9yM3Iq9NnLF8b3bG73fGj3TGAAD0KBeBaXNkb3cCAGAt+zzyc+TRpn468k9kXVPvQ36kebvUnbjM86P6+PhiZMOolj7ujBdyqcz3u1pqvxOj44X6AQD0alOpi5RjTf2JyGzk2abel3yVVV7nn51aLrbe6RyP5euuFjPu9/joOP8PD+sHANC7o6UuXn5r6i9HXmhqfXqj1OvM3a9vm7n0TOS7Us/5sJlbSPY7W2q/V5s5AIBByS/l/1jqQmcpvoycXyRH5s5eOXmdV0r9CHdfMzeN7Jd/c/YDABi8rZHrZVg7agvJheBXbfE/yAXbSvYDAFg1H0U+a2oHInuaWl9yN+xk5GCpi6wPJqeXbdzvk7L0nUUAgN4cipwpD94p+kVkV1NLeQfpuUXy3tzZK+PTyNuj8b1Sn982rbzzddxvR6n9VuLBvQAAq2J35KXIc51sj/xShvHKqLxL9VRTe71MvyuW/XJXrSv7/drUAAAG4alSH2WRO0y5AGqTX/Dv0/4yfy2vdOo3R7XfS90FXKo8P38vn8E27vdumb4fAAAAAAAAAAAAa9MPkQulPvctbyr4JvLixBkAAPQm31O6vtRXYV3r1D3AFgBgQN4q9c7MvaPjmcjh+WkAAPp2vNTHaYwf1psvoN8yPw0AQN8uR77uHF8a/WxfjwUAQE9my+SOWr7XMxdrT3ZqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMCQ/QuIhINCjaxFHQAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAZCAYAAADuWXTMAAAA40lEQVR4Xu2SqwoCURCGBzQatHp/AJvFC/gCRptJsRjEB1DB5KNYDILFLiaxiihoMZkEs3j5Z+ccWYZdvCSDH3xl/p05u3uG6M9XHOEdnuHGuIV7k91MziZMz5O6CU4wqTImAnskzxRV5jAiCecwoDLLGFZ1kQnDA8mAvsos3NjRRUsJXuEF5lTGxGBZF90MSE7fwZDKXhKEC5IBTZW9RRdOSQZ9BH/TkrxfOQNbumjJwjWM6sDQgG1dZFIkm8XT/ZjBii7yHa9gDcaVaViAQ5KfmHc6XExI7ta9w356re+f3+YBG9UyZxfKwaYAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA3CAYAAACxQxY4AAACUklEQVR4Xu3cP8hNcRgH8B9RKAuDIoNilU0pg5RSYjBgMQmDFCnKZjPJpBj8G6SUt2SjjJRBWaQwSRYGERGeX+fe1+8+Hd7lvXrv2+dT3+55nt+53Xu3p/M795QCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMKf9GuRd5EXkZeTDoPeqOW+uWpgb4UnkcG4CAEyq5aUbzOqAltUhbnVTP4+sa+qhR5FVuTlL9kau52bphrIDuTlQf8v33AQAmGSbSzfgbEv9y5EtTT0V2drU1aIyOtTNtk2Rh7kZzudG40HpH0ABACZa3VqsQ87tvNA4Hjnb1Bsi15q6z93Isxlyavrsft/K6NbnpeY4O1a6q4ZfB68AAPPKx8jP3GzsKt1Vt6FbkRVNPS51kBxexdseOdOsZRcHr/ci+9oFAID54EqqD5bRLdFlpftjQrWm6Y9bHdj2R85F1qe11tHIjsFxHSQ/RZb8WQYAmGxHSnc/WutmZGPqfYksiFxI/b+5E3k6Q05On92vDmynI4fyQnI/srSp6/t2NzUAwMTaWbrBKatbpCtTrw5BJ8rolbdxq595NTd7PE51fd+N1AMAmDhvIj9Kd+/a8Jlsw7xuzhuqQ9Hi3Byzz5E9udlYG3lfuu/8dtCr97n963cAAPAf1X+Q1iGybtX23bPW93BdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgHniNz+KWMoZf35oAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKUAAAAaCAYAAADWt5x6AAAEy0lEQVR4Xu2bachtYxTH/8ZMhXspU6aMkaEQmbaxzOHKVGSeCpGQoZN8MHwxZijJDXGvK1xDlIgP5jnxAZlClFkh0/q19uY5yz7De89+z/De51f/8qxn37O3ff7PetZ6zr1SJpPJZDKZzLSyi+ld04umPcJcZjxYWf79vGE6L8zNSPY2XRqDmbGkMLVCbFpZwrRkDA6BbMrJodCApnzN9Ivpb9Mfpo9Nu6UXGA/J59G3plPap4dCNuXkUGhAU8LhcsPdFScSXjIdHYNDJJtycijUgCm3kZvy6ThRMsd0dQwOmWzKyaFQA6aka8KUH8QJY1XTk6Zl48SQyaacHAo1YEqgVvxN/29ibpFn0n5Z3fS66c0pqOAP9qDOlOfLFwxHReuXsd3l/y8HluNB4b6Pmj40HVDGVivHV1UXzRDWlfcPvM/Lk/hC0wvJuBeFGjLlq/JsuVYS28t0UTIeJdGUh5kuMa0if+4zy/iu8oatiXJjHdOD8oXK4plXxmeZvpLX2TMFTlWeMM02XWf6Opl7Sv6Ol09i3SjUkCnny2+8UzlewXS3aal/rxgt0ZR3yp/xePlzp9mchu3UZLyR6bhk3C9nm3aWZ+G/TOcmcyeY7i3/m4P9m+Vf6iOmNaqLJojtTBfIzfmRPGNWbGD6IhmnzJW//42TWKGGTElm4cOPKsdXyL/McSGasuJZebmQwova1LS23KBkNBbYotIy/S7ftitOlBufLPqWfOsDsinmnFQKuQ8OTmIb6r8FGNlWvmukFGrIlKfJH+ZC0w6mk9un+4aa8mV5OdCvqAN7UWfKNeUZ7OIktrTpmWQMLQ1myvfltWvKA/KMyJb2iWnfMk7m/tO0TDmeNG41/aj2xpYdgmPDOqjr7w+xQg2Zch+5KdkWrw1z40CdKWlmeGbqyAq26ZOSMbTU2ZQswP1jMGEl+T0uS2JkDt5THVz3eYgtJzdrt219C9N+MZiASY5Re7aObK/uC5wamffTbcGQJNKjQco3FiSLveJQ003yJphd4vRkDgo1ZEpeNC//S3V/eaOizpRbyp/5iHJM7UMtxJaa0lK9KamfyAp8RlVL10HRT80I1LE0P5QGEbLmp6ZjQ5xswj1itq3gOb6RX7NVmKug4WS+0w8cK5p+lWfpTt8fXTSfke4sEXqLd+TPBJwwVKcOQPLiL1xgVu7JTrVZMg+FGjIlN+HnxkPixJhQZ0qgGeElLjDdIe+MIy3VmxIelxvznDiRsKe8buVo6D55HVXHbaazYlD+579T52YBqENpMOh+62BX+EH1nw9kMsqmt+WZuQ7M+L18UXViPXm3/by8Pq56jIpX5O8c6upJKNSQKcedTqbsh5bpnhhMIBOcEYNThC+K5gcwUMzW8FgMjADKkVgD9gtmJxNvXY5ZyHwWP76kFMqm7ElLnbtH4ORh8xicAgeZbjTtKD9CqsvKnKfOjcERQN26qAuQ3fRnuQmpS8mmnA9fmV6kbMqu8PKul2/vn5luMG3SdoV38A+H2FTgHj/Ja7VKz7Vd4VCbsY2PEkzFOWq3ZqkXnNLcLj9g51cfTiFiDV0om3IgaEKiUZsG414TgyOARXFkDE4DhRYTU/KryXvyI4tRZ5xMPSw+vh+arcXin0NkMplMJpPRPyTM9dvP54pbAAAAAElFTkSuQmCC>

[image12]: <data:image/png;base64,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>

[image13]: <data:image/png;base64,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>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAaCAYAAAC6nQw6AAABDUlEQVR4Xu2SP0uCURSHT/6DJjGHmhWCCHHSqaGWvkBrW3u4uggOuhUEDYqBtkUk9A2acmoNgmiKQlBwbbKe23mVtwOR18DJB57hnt/h3Hu5V2SJLy0cYs0G83CDn7hlA1/2RQdVbeBLDAf4ZIN5aIieKm8DX3ZFB9VN3ZsIvuOLDXxJ4IPoqQomm5k43mJTdNDJz/ibEnZsMYx7sS5eBOtnfMWVaYeyjZumNsUNucae6NUc7oe7U+1Mmv4iilf4hhuhek500HmwXsNTvMf0pCnMJX5g0QbwiH3RzcqYFN0wG25yrIo2Htog4AjHeIAp3BN90X/TxmP55Wqz4q43wnWsmMybOzzDjA2WLIgvHHkrfA/1rCUAAAAASUVORK5CYII=>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAAA3klEQVR4XmNgGAWjYDABFyDeAsR3gdgbKiYC5XfAFOECMkC8DoiZgPgCEK+CigsB8QsgPgnl4wR5QGwNxApA/A+IC5DkEoF4GRLfDIhvI/FRQAMQ/2KAOB0GkoA4DYkvDMR2SHwUcAOId6KJrQFiCTQxrIAHiP8DcS2SmBIQz4eyGYG4Hoh3MeBxwSsgngplczFAAlYayndngGhcDsTJUDEM4ATE5xgg0bkCiA2R5ASAmBeI3zFAYocsEM8AcRU/ELOgyREFtgFxMBBXAjEbmhxRAJQiFzAgUuoooBYAAKHuIGWcNRBeAAAAAElFTkSuQmCC>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAaCAYAAAD1wA/qAAAB8klEQVR4Xu2VzSvlURjHH8xQ1KRm4T3Jv4BmCgvlrby/bGmklNkNCxt1lxaaxltssEBhRUix9FaykDCSpQ2iGE3y0sz36fn97j2/c/Fzf/du1PnUp845z3PrnPN7znOJDAaD4b3yA/6G17BDi0WKz7BBXwyBOXgL/8EyLeagjSQpVw+ESTLsheuwXIuFyhB8gJ/0gMoMvIDResAjabAfbsFaGOUMe+IYrumLKjHwCk7pAQ/wAQbgJqyhyByAySapmG49oPKVJKnJmhfBWbgN8+0kF/gAgyQlVKXFvJAD50nexiocIdljnpqk4yNJ4npuht9hI7yDXYG0Z0klOcAGrNRiXqmDf2GxNc+C9/CSXEqfy+CApGNVWGuFJKXGG32NdnhKkfkKTCb8A0eVtQ/wBk4ra0EkwkeSG9iBrTDWkeEOlxV3FL6QcA/UR1IdfJE2XN689k1ZC6KeJKkAfoHn5P3Rp1PgQNXk7aHvkfxfcAOy8ZHskS/sRYZJPuVHa74AT6xxCyy1xqFgt14vnWuX5Hcq3HL3rfEkOQ/ph3vzkjLnMXcJTl6B8UosVFLgL5KNvfW/5Cc8Uuad8AmOkbTgCSXmJw6ekZSXDdcjP3z+MiXKejgkwR6SzbiRAMfhMkn75argTnoIF2FGINVgMBgMhvD5D5FiXQuOxy88AAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAAaCAYAAAA38EtuAAADrklEQVR4Xu2YaahNURTHl3meM5UylQylZIgUMg8Rii9CxgwpimSeS2RKxgwPXyjzFBl65BlK8QXhC+klHwwh8gX/v7X2u/tt99537nM9N51f/XLOXue+s886e6+9D5GYmJj/g2awABaGgRLoDO/Ak2EgJjXz4LGwMQJ5cH7YGJOac3CmHVeGPb2YoxusFrS9EB3Z/4RysELY+JfYCp/A2/A4fAVvwkvwDbwM58BK7gcG+7gEboC74QfY1osvgn288x5wqXdOWsL3sDycKnr/EcWuSAFvzk7ypj/gR/gQNoc14F342WK8wT1rJ7zRJ4t9gXusvSwYAifaMR/W0Vq0H0OtvboXWw132DF//9qLOdaKJpgjdl0QI5PgGThFNEcPJGKiHXybTNjsMAB2icaS/cEB8CqsHQYygKOjosnjKAwWfdHkqB8Ah+zfvnCuHTeAX2FHO2d9Dn/n4GjfJzoIQw7Dt3Ch6IyJ2t8ipokmc1kYAKdEYxOCdnbkAmwStJcEOzgL5sNb8Iboy7oCVyQuS8sgSZ3og6L3qAX3WhsHxDtJJI/PxPpc184d7eA2uBF2CGLkpeho58zgdUx0+DfSMko0mVuC9t6inWWMo8BnhugUyoRGosllrcyogwFMXLpEE47oBXbcXXSak6aiZZCJZDlxtII7JTGzmAuWIkcL0dHMl8V7H4D9pXhdL5Feosnk1HDwhnzrYyzm1yx29rQkn16p4LXXRZP0p/ABkyW6q2htni66nvgvk7WbI5V1OM90pYS7ju32r4OzYhOsaues++4ltofX4CrJLAe/fshknvfaxsF6sJ/F/MXuCGzjnUeBdZUPkw2YaDebmFDOEi7iXOCewpWipSPn4JRmMvnVQxrD0XbcyWIn7Hy4/L7tiQK3VdyXZgM/0RzRnPZ5oouePytzDpaJ7/CZnbP+uinRXDTR3AbWhBel+BSLCmv9fdHRl8r1RVenZ6AUTzRh3eesGSu6uOcsXCC4MnPUdfHamVwm+rHo1E/2BRUFJoIjMRtw1zHZjl2i+fK5C+KXHLd4/kKWUzwXHdXceoV8M92GvzTwwbnZzwYcufx4IP5iyF0SF+2G8Cys4sVyBtZnjmp2MqTQrBMGMoSr9PKwsRRwBzDejsP/GOIHBxd3Jn2/ZLgrKAvcJj4ZBXBk2FgK+ND8KOLuZpjorobrQyZsho9EP3Q4mrnT4FaTdZvU92L8wOA2LOeSXVawjCwWTTgTkW+uSVwSExMTExMTExMTk5P8BHbftmq0xMO7AAAAAElFTkSuQmCC>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAbCAYAAACqenW9AAAAzUlEQVR4Xu3QsQtBURTH8ROhTEb5PxSFwcBik5WSMthYjP4Lf4GBVRZ2g6xS8g+glJQMiu9z783rdpPJ9H71qXvvOfXOOyJB3Oliiwt6Vs2ZNp5I2wVXxjghZBfshHHGyC64khU1Ql3fi5hghZxpMhmIak6igQ5quKP/aVNZYiNqExX9VhA1Vso0mfzcnMADN6zRQtTf4E9V1Lx5ZHCUL1sZ4oqIvk+x1+cmyvr8zg4z3907L0Ttfo64KcRwEDWKibdX72e9L5R870H+kBdncCc5XLQf0QAAAABJRU5ErkJggg==>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAZCAYAAADXPsWXAAAAw0lEQVR4XmNgGAWDCjACMRO64Fkg/grE/4H4DxA/AGI7ZAVAsIEBIg/C74A4FVUaAoIZIAoWoksggZNAHIkuiAwMGCCG7EWXgIIQIO5EF0QH/AwQQ+6gSwCBIBDvBGI2dAlsAOTXnwyYgTadAeJSosAZBohrpJDEnIG4AolPEKxmgBhiCeVzAfESIGaGqyACpDNADCkHYjMgTkGVJg64MkAMmQ/E3WhyRAMlBoghz4FYAk2OaADyOyjl+qNLjIJRQCkAAEjqIahLnhVtAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAA3CAYAAACxQxY4AAACCklEQVR4Xu3bzcuMURgH4BOJpCws2Emxk4+yVxLKf8DawkJKNljJgkIpK0qyVTb2lJSUz8JOrJSSrZJ83Kfz9L73HN7Jwjt4uq76NXN+9zPNLO/mmSkFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgL9kaV8AAPzvvkdOdt3FyLWuWwzvSnv/7FJkTdd9jnxI57Wlve5p6qp73RkAYBTq4vMynQ9ErqTzYjpVJhe28+l5Vhe7L+m8rbTXvUndvsjZdAYAGI3TZX5p2hJZnmYL2Rt5PiWPI6vnrp7uRuRJ5Fw/SO6WycVufeRV1+1KzwEARmVD5FtkU+R2N5uFHZGPZfpvz26W+eVs1fB4P3Vbh0cAgNG6HNnZlzNwKHK1tMXrTjfLzpR2TV0qdw/d9aE7Ejk4dAAAo/Uisqwvp9hT2m3PhfKw/N4t0bp0LYm8LW352jw5nnO0tPnh1F0YulupAwAYpXXl539qzkL9Vqwua9Xx0j5D/bbtV+q1db4xdSeGrt7SBQAYrWORT6UtPo8iKybHf1xduOq/Pev7fU39+6GreRZZmWbV9sjrrtsfedB1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8C/4AQ9PUViNnwC3AAAAAElFTkSuQmCC>
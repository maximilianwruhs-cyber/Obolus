# **High-Performance Engineering with the Pi Coding Agent: Context Optimization, Custom Skills, and Autonomous Self-Modification Loops**

## **Taxonomy of the Pi Harness and Core Runtimes**

The development of agentic software engineering tools has introduced a key architectural choice: monolithic "black-box" platforms versus minimal, highly transparent agent harnesses.1 Many commercial agentic systems feature extensive system prompts, proprietary context managers, and complex permission hierarchies that often introduce substantial token overhead, latency, and developer fatigue.1  
In contrast, the Pi coding agent operates on a philosophy of structural minimalism.3 The reference implementation of Pi features a system prompt of under one thousand tokens and exposes only four core built-in tools: file reading (read), file writing (write), precise text-replacement patching (edit), and general shell execution (bash).3 By relying on the premise that frontier models are heavily pre-trained and alignment-tuned on terminal execution sequences, the agent operates via direct, low-latency execution loops.1  
To satisfy high-throughput engineering environments, the Pi ecosystem relies on two primary runtime families 6: the reference TypeScript CLI and a high-performance native Rust port.6 The operational properties of these runtimes are detailed below:

| Dimension | TypeScript Reference Engine (@earendil-works/pi-coding-agent) | Native Rust Engine Port (pi\_agent\_rust) |
| :---- | :---- | :---- |
| **Primary Language** | TypeScript (93.5%), JavaScript (5.7%) 7 | Rust (utilizing the compiled native engine) 6 |
| **Concurrency & Async Runtime** | Node.js / Bun asynchronous event loop 7 | asupersync structured concurrency framework 6 |
| **Local File Indexing** | Periodic directory scans using workspace utilities 8 | Background thread re-indexing the file tree every 30 seconds via the ignore crate 6 |
| **Startup Performance** | Standard Node/Bun startup latency 6 | Sub-100ms cold load (P95); sub-1ms warm load via pre-warmed isolate reuse 6 |
| **Extension Engine** | Dynamic execution via the jiti compilation bypass 10 | Embedded QuickJS runtime executing scripts in an isolated, non-Node environment 6 |
| **Security Framework** | Direct execution without approval gates ("YOLO mode") 3 | Capability-gated host connectors with automated shell command pattern filtering 6 |

The structural minimalism of the reference engine is supported by local extensibility.3 Rather than baking advanced multi-agent coordination, web search, or specialized data parsers into the core engine, Pi exposes a lifecycle-hook architecture.10 This allows developers to build and share complex behaviors via modular packages.10

## **Context Optimization and Token-Saving Strategies**

Because the token cost and inference latency of large language models scale quadratically with context length, context engineering is essential for sustaining long-term productivity.1 Generic agents frequently waste valuable tokens on redundant conversational explanations and repetitive system files.1 Pi resolves this inefficiency by tightening its reasoning loop using three distinct optimization vectors: structured context files, custom system prompts, and strict session isolation.4

### **Grounding the Agent via AGENTS.md**

The primary optimization lever in the Pi context pipeline is the AGENTS.md file (or its legacy equivalent, CLAUDE.md).8 Rather than treating this file as a passive instruction sheet, the systems engineer treats it as a "Living System Architecture" document.8 This file is loaded automatically at startup from several nested scopes:

* **Global Scope:** Loaded from \~/.pi/agent/AGENTS.md.8  
* **Ancestor Scope:** Loaded by walking up parent directories from the current working directory (cwd).8  
* **Project Scope:** Loaded directly from the root of the active workspace.8

To ensure highly reliable code generation, the AGENTS.md file must explicitly document the project's strict coding standards (such as Rust-first design patterns, zero-cost abstractions, and memory alignment rules) and define the current infrastructure state. Incorporating these rules prevents the model from hallucinating outdated libraries or making incorrect project assumptions.

### **Custom System Prompts for High-Signal Communication**

To bypass generic, conversational default behaviors, the developer can enforce high-signal, concise communication by placing a system.md (or SYSTEM.md) file in the .pi/agent directory.4 This custom system prompt replaces or appends to the default instruction set, forcing the model to operate with strict professional constraints.4 A highly optimized system prompt block can be defined as follows:  
Prioritize edit for precise changes to existing code. Keep output concise.  
For Rust tasks, verify cargo check before finishing the turn.  
By explicitly commanding the model to use the precise edit tool rather than rewriting entire files with the verbose write tool, this prompt minimizes token write-back latency and reduces the risk of merge conflicts.5

### **Scope Limitation via Context Files and Isolated Sessions**

To keep the active inference window fast and clean, the developer must employ strict scope limitation.9 This is achieved using two coordinated practices:

1. **Targeted Context Injection:** Rather than passing entire source directories, the developer feeds only the strictly necessary source code or API definitions into the session using "Context Files".9 By prefixing specific paths with the @ symbol (e.g., pi @src/core/lib.rs @src/core/types.rs), only the exact target content is parsed and indexed into the startup message.6  
2. **Session Isolation:** Rather than carrying a single long-running conversation across multiple development stages, the developer must start fresh, isolated sessions for distinct tasks (e.g., one session for TUI dashboarding, and a completely separate session for battery telemetry parsing). This prevents "context drift"—where irrelevant diagnostic logs or design discussions from previous tasks pollute the attention heads of the model—and ensures optimal prompt-cache hits.9

### **Context Compaction Mechanics**

To maintain these strict token boundaries, the engine executes a continuous context compaction protocol when approaching hardware limits.8 Let ![][image1] represent the total active context size, defined by the system equation:  
![][image2]  
Where ![][image3] is the system prompt token weight, ![][image4] is the weight of the concatenated AGENTS.md instructions, and ![][image5] is the conversational history.9 Compaction is triggered dynamically when:  
![][image6]  
Where ![][image7] is the model's absolute context window and ![][image8] is the token budget reserved for the model's next turn response (configured via compaction.reserveTokens, defaulting to 16,384).18 During compaction, older messages are summarized using localized compaction prompts, while the most recent ![][image9] tokens (configured via compaction.keepRecentTokens, defaulting to 20,000) are preserved in their raw format to maintain immediate conversational accuracy.8  
Several community extensions optimize this context window further:

| Extension Name | Primary Optimization Mechanism | Token Reduction Benefit |
| :---- | :---- | :---- |
| **pi-skill-shiori** | Zero-Catalog Mode with policy-based retrieval; candidates are only triggered when explicit criteria are matched.19 | Hides the default, bulky skill catalog from the first-turn prompt; injects short suggestions instead of full files.19 |
| **pi-skillful** | Toggles skill visibility on-demand using nine hotkey-triggered session slots or explicit inline commands (/skill:name).20 | Prevents automatic skill-discovery prompt injection; keeps skills hidden from the LLM until explicitly invoked.20 |
| **pi-context-injector** | Intercepts turn generation to inject context only during initial prompts or compaction events.21 | Removes static contextual details from normal turn cycles, keeping the intermediate context window compact.21 |

## **Custom Skills and Autonomous Optimization Loops**

For repetitive tasks—such as benchmarking a terminal user interface (TUI) rendering loop or parsing specialized rail vehicle telemetry formats—asking the model to write the execution logic during every session is highly inefficient.22 Instead, the developer should package these capabilities into reusable "Skills".12

### **Skill Architecture and Custom Wrappers**

In the Pi framework, a Skill is defined as a self-contained directory containing a SKILL.md file along with any necessary helper scripts.22 The SKILL.md file contains specialized workflows, setup instructions, and reference documentation that the agent loads on-demand.22  
For high-frequency rail-tech workflows, a developer can build a custom TypeScript skill designed to wrap native Rust benchmarks. This skill executes cargo bench via a background process, intercepts the raw terminal output, parses the performance metrics, and returns only the final metric (e.g., "latency: 42 microseconds") back to the parent agent. This specialized wrapper keeps verbose build logs and compiler warnings out of the LLM's active context window, preventing token bloat.22

### **The Autoresearch Pattern**

When optimizing code at the hardware level—such as executing SIMD vectorization or cache-tuning experiments—the developer can leverage the pi-autoresearch extension to automate the search process.24 Based on Andrej Karpathy's autoresearch paradigm, this plugin turns any quantitative metric into an optimization target.24

  \+-------------------------------------------------------------+  
  |                                                             |  
  |                      Identify Target                        |  
  |                             |                               |  
  |                             v                               |  
  |                       Generate Patch                        |  
  |                             |                               |  
  v                             v                               |  
Rollback \<--- \[Fail\] \--- Verify Correctness                      |  
  ^                      (test.sh / checks.sh)                  |  
  |                             |                               |  
  |                          \[Pass\]                             |  
  |                             v                               |  
  |                     Benchmark Metric                        |  
  |                      (bench.sh / MAD)                       |  
  |                             |                               |  
  \+--- \<------+------\> \[Improve\] \---\> Commit  |  
                                                           |    |  
                                                           \+----+

The loop operates unattended across context limits, managing state via local project files 24:

* **autoresearch.md:** The primary session document capturing the optimization objective, metrics, files in scope, and attempts tried.24  
* **autoresearch.sh:** The benchmark script that executes the target paths and returns a single metric matching the structure METRIC name=number.24  
* **autoresearch.checks.sh:** An optional correctness gate that runs after successful benchmarks.24 If the test suite or linter returns a non-zero exit code, the proposed code change is aborted.24  
* **autoresearch.jsonl:** An append-only log tracking every run, parameter variation, and delta, allowing the loop to survive system restarts.24

To distinguish real performance improvements from system noise, pi-autoresearch calculates a confidence score using the Median Absolute Deviation (![][image10]) of all benchmark runs:  
![][image11]  
A proposed code change is only committed to the git history if the confidence score exceeds ![][image12] the calculated noise floor.24 Once the optimization run is complete, the developer executes /skill:autoresearch-finalize to parse autoresearch.jsonl, group the successful experiments into distinct, non-overlapping git branches, and prepare clean changesets for code review.24

## **Toolset Tuning and Local Execution Optimization**

Optimizing the physical environment in which the agent runs is as critical as managing its context window.3 By tuning the available toolset and utilizing local inference engines, the systems engineer can eliminate external network dependencies, lower latency, and enforce absolute data sovereignty.3

### **Lean Tooling via settings.json**

By default, Pi exposes a broad set of tools to the model.4 However, providing tools that are unnecessary for a given task increases the model's "decision surface," which can lead to tool-calling errors, slower execution, or security risks.3  
Developers can explicitly restrict and define the available tools by modifying the global (\~/.pi/agent/settings.json) or project-local (.pi/settings.json) settings files.9 For example, if a specific task does not require network access or file system indexing, the developer can strip these capabilities using the following configuration 9:

JSON  
{  
  "excludeTools": \["fetch", "web-search"\],  
  "noBuiltinTools": false,  
  "tools": \["read", "write", "edit", "bash"\]  
}

Restricting the tools ensures that the model executes only the necessary operations, leading to faster and more predictable execution.3

### **Leveraging Local Inference**

Pi is provider-agnostic, allowing developers to map the entire tool-execution loop to a local model stack running on local hardware.12 This eliminates API costs, bypasses network latency, and ensures that sensitive project data never leaves the local environment.6  
To integrate local model engines (such as a local llama.cpp server or an Ollama endpoint), the developer configures the local provider details in \~/.pi/agent/models.json 27:

JSON  
{  
  "providers": {  
    "llama-cpp": {  
      "baseUrl": "http://localhost:8080/v1",  
      "api": "openai-completions",  
      "apiKey": "none",  
      "models":  
    }  
  }  
}

The developer then updates \~/.pi/agent/settings.json to define the default provider and model 27:

JSON  
{  
  "defaultProvider": "llama-cpp",  
  "defaultModel": "ggml-org-gemma-4-26b-4b-gguf"  
}

This configuration routes all tool-calling loops locally, ensuring high-speed execution.6

### **Sub-Agent Delegation**

For complex workflows, utilizing a single, massive model to manage all tasks can result in slow execution and context congestion.3 Instead, developers can implement an "AgenticOS" style architecture using the sub-agent extension (pi-sub-agent).23  
This framework allows a primary coordinator agent to delegate specialized tasks to smaller, highly tuned local processes running with isolated context windows.23 For example, a coordinator can delegate user-interface creation to a sub-agent specialized in TUI generation, while routing core operations to a sub-agent optimized for backend logic.23

                    \+-----------------------+  
                    |                       |  
                    |   Coordinator Agent   |  
                    |       (Depth 0\)       |  
                    |                       |  
                    \+-----------+-----------+  
                                |  
             \+------------------+------------------+  
             |                                     |  
             v                                     v  
\+-----------------------+             \+-----------------------+  
|   TUI UI Sub-Agent    |             |   Backend Sub-Agent   |  
|  (Isolated Context)   |             |  (Isolated Context)   |  
|       (Depth 1\)       |             |       (Depth 1\)       |  
\+-----------------------+             \+-----------------------+

Sub-agents are configured via markdown files containing YAML frontmatter in \~/.pi/agent/agents/\*.md.23 The properties of these sub-agents are managed using the following parameters 31:

| Frontmatter Parameter | Accepted Values | Architectural Role |
| :---- | :---- | :---- |
| **name** | String (lowercase, alphanumeric) 22 | Unique identifier used by the coordinator to invoke the sub-agent.31 |
| **model** | Provider/Model ID string 31 | Overrides the active model, routing the sub-agent's task to a smaller model.31 |
| **thinking** | off, minimal, low, medium, high, xhigh 31 | Controls the reasoning effort of the local model to balance speed and accuracy.31 |
| **tools** | Comma-separated list (e.g., read,grep,find,ls) 31 | Defines the tools available to the sub-agent, limiting its execution scope.31 |

To prevent recursive loops and resource exhaustion, the framework enforces a rigid depth limit (typically capped at a maximum depth of 3\) and implements cycle-checking algorithms to block self-recursion (e.g., planner ![][image13] reviewer ![][image13] planner).31

## **The Self-Optimization Loop and Core Modification**

Because the Pi coding agent is completely transparent and has read access to its own source code, it serves as a powerful tool for self-optimization.1 If the agent is operating inefficiently, the developer can direct it to inspect, analyze, and rewrite its own core codebase.1

### **The "Explain Your Code" Pattern**

When a developer notices that the agent is taking multiple tool turns to execute a simple file edit, they can trigger an internal audit.1 The developer prompts the agent with the following targeted instruction:

Read the source code for the edit tool. Why is it taking multiple turns to apply this patch, and how can we optimize the diff format for this specific file?

This instruction prompts the agent to call its read tool on its own implementation files (such as packages/coding-agent/src/core/tools/edit.ts and edit-diff.ts).33 The model analyzes its fuzzy-matching logic and patch-application paths, generating a detailed report of the execution overhead.32

### **Modifying the Core Edit Tool**

If the default file-patching format (which requires matching line ranges and exact indentation) proves too verbose or error-prone for a terminal-native workflow, the developer can instruct Pi to rewrite its own edit tool.33 This self-modification process follows a precise engineering sequence:

1. **Analyze current behavior:** The agent reads applyEditsToNormalizedContent() in edit-diff.ts.35 It identifies that when fuzzy-matching triggers, the engine normalizes the entire file content using normalizeForFuzzyMatch(), which can strip trailing whitespace or silently modify smart quotes across the entire file.35  
2. **Propose code changes:** The agent proposes a targeted fix to map the fuzzy-matched positions back to original content offsets, ensuring that modifications are strictly confined to the targeted patch area.35  
3. **Compile and verify:** The agent executes npm run check and runs the unit tests in packages/coding-agent/test/model-registry.test.ts to ensure the modifications do not introduce regressions.36  
4. **Hot-reload:** The developer runs /reload in the interactive session to load the updated edit tool in-place, completing the self-modification loop without restarting the parent process.8

## **Strategic Action Plan for Rail-Tech Operations**

To apply this high-performance framework to specialized rail-technology workflows, developers should execute the following three-step action plan:

### **Step 1: Map Terminal Hot-Paths**

The systems engineer must identify and document the three most frequent terminal tasks executed during the rail-tech development cycle. For a typical rail-telemetry and control system, these hot-paths include:

1. **Telemetry Aggregation:** Consolidating battery and power logs from multiple vehicle diagnostic ports.  
2. **Performance Profiling:** Benchmarking high-frequency TUI rendering loops to prevent screen flickering on vehicle terminal displays.6  
3. **Binary Optimization:** Compiling and auditing embedded Rust binaries for size and execution speed constraints.6

### **Step 2: Document Rules in AGENTS.md**

The systems engineer should establish a dedicated "Performance & Optimization Rules" section in the primary project AGENTS.md file. This section provides strict operational guidelines for the model when editing code 8:

## **Performance & Optimization Rules**

When writing or refactoring code for this project, the model must adhere to the following strict guidelines:

1. Rust-First Patterns: Prioritize the use of idiomatic Rust, zero-cost abstractions, and strict memory alignment.  
2. Explicit Memory Allocation: Avoid hidden memory allocations in loop iterations. Pre-allocate vectors using Vec::with\_capacity where possible.  
3. Patch Verification: Always run cargo check and execute local benchmarks before marking a task as complete.  
4. High-Signal Commits: When committing successful optimization changes, include the precise metric delta and confidence score in the commit message.24

Grounding the agent with these guidelines ensures that all generated code is optimized for embedded rail environments from the first turn.8

### **Step 3: Build a Specialized Battery Telemetry Skill**

The systems engineer should build a specialized TypeScript skill wrapper to simplify telemetry log aggregation. This skill is registered under the standard location \~/.pi/agent/skills/battery-telemetry/.16 The directory contains two primary files:

#### **SKILL.md**

# **battery-telemetry**

description: Aggregates battery telemetry logs into a single summary block.  
classification: rail-tech-diagnostics  
hidden: false  
This skill processes raw log directories, extracts voltage, temperature, and  
state-of-charge metrics, and returns a clean, structured JSON summary block.

#### **index.ts**

TypeScript  
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";  
import { Type } from "typebox";  
import { exec } from "child\_process";  
import \* as fs from "fs/promises";

export default function telemetrySkill(pi: ExtensionAPI) {  
  pi.registerTool({  
    name: "aggregate\_telemetry",  
    label: "Aggregate Battery Telemetry",  
    description: "Aggregates raw battery telemetry logs into a structured summary.",  
    parameters: Type.Object({  
      logDirectory: Type.String({ description: "Path to the raw log directory" })  
    }),  
    async execute(toolCallId, params) {  
      const logDir \= params.logDirectory;  
      try {  
        // Read raw logs from directory  
        const files \= await fs.readdir(logDir);  
        let totalVoltage \= 0;  
        let logCount \= 0;  
          
        for (const file of files) {  
          if (file.endsWith(".log")) {  
            const content \= await fs.readFile(\`${logDir}/${file}\`, "utf-8");  
            const match \= content.match(/voltage=(\\d+\\.\\d+)/);  
            if (match) {  
              totalVoltage \+= parseFloat(match);  
              logCount++;  
            }  
          }  
        }  
          
        const avgVoltage \= logCount \> 0? totalVoltage / logCount : 0;  
        const summary \= \`Aggregated ${logCount} telemetry logs. Average Battery Voltage: ${avgVoltage.toFixed(2)}V.\`;

        return {  
          content: \[{ type: "text", text: summary }\],  
          details: { averageVoltage: avgVoltage, filesProcessed: logCount }  
        };  
      } catch (error: any) {  
        return {  
          content: \[{ type: "text", text: \`Failed to process telemetry: ${error.message}\` }\],  
          isError: true,  
          details: {}  
        };  
      }  
    }  
  });  
}

By deploying this specialized skill, the agent can summarize dense battery logs in a single tool call. This approach bypasses the need for the LLM to write custom log parsers in every session, keeping the active context window highly efficient and focused.12

#### **Referenzen**

1. Pi coding agent is amazing (or how I learned to stop worrying and leave OpenCode), Zugriff am Mai 29, 2026, [https://www.reddit.com/r/LocalLLM/comments/1ta2tzz/pi\_coding\_agent\_is\_amazing\_or\_how\_i\_learned\_to/](https://www.reddit.com/r/LocalLLM/comments/1ta2tzz/pi_coding_agent_is_amazing_or_how_i_learned_to/)  
2. Pi Coding Agent: The Only Claude Code Competitor \- Agentic Engineer, Zugriff am Mai 29, 2026, [https://agenticengineer.com/the-only-claude-code-competitor](https://agenticengineer.com/the-only-claude-code-competitor)  
3. Building Pi: A Minimal, Extensible Coding Agent Framework \- ZenML LLMOps Database, Zugriff am Mai 29, 2026, [https://www.zenml.io/llmops-database/building-pi-a-minimal-extensible-coding-agent-framework](https://www.zenml.io/llmops-database/building-pi-a-minimal-extensible-coding-agent-framework)  
4. I tried Pi after watching its founder explain why he quit Claude Code \- Medium, Zugriff am Mai 29, 2026, [https://medium.com/@urvvil08/i-tried-pi-after-watching-its-founder-explain-why-he-quit-claude-code-7b747c37fa22](https://medium.com/@urvvil08/i-tried-pi-after-watching-its-founder-explain-why-he-quit-claude-code-7b747c37fa22)  
5. Alternative Coding Agents: Pi, Zugriff am Mai 29, 2026, [https://blog.scottlogic.com/2026/05/13/alternative-coding-agents-pi.html](https://blog.scottlogic.com/2026/05/13/alternative-coding-agents-pi.html)  
6. GitHub \- Dicklesworthstone/pi\_agent\_rust: High-performance AI coding agent CLI written in Rust with zero unsafe code, Zugriff am Mai 29, 2026, [https://github.com/Dicklesworthstone/pi\_agent\_rust](https://github.com/Dicklesworthstone/pi_agent_rust)  
7. GitHub \- earendil-works/pi: AI agent toolkit: coding agent CLI, unified LLM API, TUI & web UI libraries, Slack bot, vLLM pods, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi](https://github.com/earendil-works/pi)  
8. pi/packages/coding-agent/README.md at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md)  
9. Using Pi · Docs \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/docs/latest/usage](https://pi.dev/docs/latest/usage)  
10. Extensions · Docs \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/docs/latest/extensions](https://pi.dev/docs/latest/extensions)  
11. pi/packages/coding-agent/docs/extensions.md at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md)  
12. Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/](https://pi.dev/)  
13. Introduction to Pi \- Pi, Zugriff am Mai 29, 2026, [https://pt-act-pi-mono.mintlify.app/introduction](https://pt-act-pi-mono.mintlify.app/introduction)  
14. Pi: The Open-Source AI Coding Agent You Probably Haven't Tried Yet \- DEV Community, Zugriff am Mai 29, 2026, [https://dev.to/arshtechpro/pi-the-open-source-ai-coding-agent-you-probably-havent-tried-yet-2h0h](https://dev.to/arshtechpro/pi-the-open-source-ai-coding-agent-you-probably-havent-tried-yet-2h0h)  
15. @mariozechner/pi-coding-agent \- Pi, Zugriff am Mai 29, 2026, [https://pt-act-pi-mono.mintlify.app/packages/coding-agent](https://pt-act-pi-mono.mintlify.app/packages/coding-agent)  
16. SDK · Docs \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/docs/latest/sdk](https://pi.dev/docs/latest/sdk)  
17. Pi Coding Agent: The Ultimate Guide to Terminal-Based AI Programming | Efficient Coder, Zugriff am Mai 29, 2026, [https://www.xugj520.cn/en/archives/pi-coding-agent-terminal-ai-programming-guide.html](https://www.xugj520.cn/en/archives/pi-coding-agent-terminal-ai-programming-guide.html)  
18. pi/packages/coding-agent/docs/settings.md at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md)  
19. pi-skill-shiori · Packages \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/packages/pi-skill-shiori](https://pi.dev/packages/pi-skill-shiori)  
20. pi-skillful · Packages \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/packages/pi-skillful](https://pi.dev/packages/pi-skillful)  
21. pi-skill-hub · Packages \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/packages/pi-skill-hub](https://pi.dev/packages/pi-skill-hub)  
22. Skills · Docs \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/docs/latest/skills](https://pi.dev/docs/latest/skills)  
23. pi-sub-agent \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/packages/pi-sub-agent](https://pi.dev/packages/pi-sub-agent)  
24. davebcn87/pi-autoresearch: Autonomous experiment loop ... \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/davebcn87/pi-autoresearch](https://github.com/davebcn87/pi-autoresearch)  
25. Speed up code with pi-autoresearch \- quanttype, Zugriff am Mai 29, 2026, [https://quanttype.net/p/speed-up-code-with-pi-autoresearch/](https://quanttype.net/p/speed-up-code-with-pi-autoresearch/)  
26. Autonomous Code Optimization with SkyPilot, Zugriff am Mai 29, 2026, [https://docs.skypilot.co/en/latest/examples/agents/autonomous-code-optimization.html](https://docs.skypilot.co/en/latest/examples/agents/autonomous-code-optimization.html)  
27. Pi \- Ollama's documentation, Zugriff am Mai 29, 2026, [https://docs.ollama.com/integrations/pi](https://docs.ollama.com/integrations/pi)  
28. Local Agents with llama.cpp \- Hugging Face, Zugriff am Mai 29, 2026, [https://huggingface.co/docs/hub/agents-local](https://huggingface.co/docs/hub/agents-local)  
29. How to run a local coding agent with Gemma 4 and Pi \- Patrick Loeber, Zugriff am Mai 29, 2026, [https://patloeber.com/gemma-4-pi-agent/](https://patloeber.com/gemma-4-pi-agent/)  
30. pi-llama-cpp · Packages \- Pi Coding Agent, Zugriff am Mai 29, 2026, [https://pi.dev/packages/pi-llama-cpp](https://pi.dev/packages/pi-llama-cpp)  
31. mjakl/pi-subagent: A lightweight subagent extension for the ... \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/mjakl/pi-subagent](https://github.com/mjakl/pi-subagent)  
32. Pi Coding Agent: A Self-Documenting, Extensible AI Partner \- DEV Community, Zugriff am Mai 29, 2026, [https://dev.to/theoklitosbam7/pi-coding-agent-a-self-documenting-extensible-ai-partner-dn](https://dev.to/theoklitosbam7/pi-coding-agent-a-self-documenting-extensible-ai-partner-dn)  
33. pi/packages/coding-agent/src/core/tools/edit-diff.ts at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/src/core/tools/edit-diff.ts](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/src/core/tools/edit-diff.ts)  
34. pi/packages/coding-agent/src/core/tools/edit.ts at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/src/core/tools/edit.ts](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/src/core/tools/edit.ts)  
35. Edit tool fuzzy matching normalizes entire file content, corrupting characters outside edited region · Issue \#3554 · badlogic/pi-mono \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/badlogic/pi-mono/issues/3554](https://github.com/badlogic/pi-mono/issues/3554)  
36. pi/AGENTS.md at main · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi/blob/main/AGENTS.md](https://github.com/earendil-works/pi/blob/main/AGENTS.md)  
37. Feature Request(coding-agent): Allow overriding providers with only "headers" in models.json · Issue \#3538 · earendil-works/pi \- GitHub, Zugriff am Mai 29, 2026, [https://github.com/earendil-works/pi/issues/3538](https://github.com/earendil-works/pi/issues/3538)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAaCAYAAAAjZdWPAAACOUlEQVR4Xu2WS0gVcRTGP3vQuygRJCgoCAolK8iNC90YRJtWPQyCIII2RS6MdoqPVW1qk2jQyoU9Nz2htEWERdtqFRWlq6CCQCKt7+Oc4Y6n9I5gjMT84Mede859nP+ZM/8ZoKCgoGAuWUtP0Sf0HX1FX9Ljnr9A9/jxvECFfaa3aANd4PHF9BJ9Rsfpco/nSgXtpT/psZBLUOGj9EFM5EUP/UXPxkTgIT0dg3lQTyfoe1g3Z0JnY1MM5sE1WJdbYyIH1LRtdHdMRL7Ait4RE2WYzQ6yntbG4F+oogP0Y0yk0cpU8A+6MOQiLXRD6v3N1HE5DtBDMTgNNShTtPhEJ+mKmEixmj6C7TLiCH1dSs+I9v0XyF70VmQouhPW7YMx4SylgyjNmWbuDmys+mFnQGhhF2kXvUybPa4daYw+hn1+JWyfv0/bYdfUCf+syFT0MtgP6qZyGKUdRF1tordpo8cSFH8TYjdQWoBGTfkt/n4YUzu9BjZeetUCvtJqz2UqWiyhJ+kIbFyew/ZkdUk/HGnC1KJXwUZscyp2l57z42H8OR668M/DzvQ3ut3jmYueLep8UvR+ug42YvrDBN05NSpiCFa0FqXi9P0PdKPn1ahdsOb9s6I132/9uNtfdWaO+rFGTDerOn+va0A5zbkK7oCNk9A18x02WlK7hxYx5yyi92gf3euxSnoF9mB1FXYGEvbRp7AnRD2EqcPqfhs9A/uOxmknvQ57KEuaMe/RgpL7RblHioKC/4LfvY1mCUPiufcAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAaCAYAAADi4p8jAAACdUlEQVR4Xu2WWahOURiG38yKIlLckDJkSu6EzC4QkozlStTpHGXKjSQuDGWMUC7cKBkulYy/QiFjFHVcUDInSqbC+/Z9y7/+lZ2L/Z/jP6f91tNe+11r1/7W+ta3FlCoUKFChfJrAflFPpMn5CH56N5b8og0km/kOxlnn7UcnSVbSMfIuwALcFDk9SU/SK/Iq3n1JNcSrxP5Qp4nvnQ/NWpddWRx4k2Brd6RxFfg5xOv5tWfdEi8bbAAtTdjtSMDEq9F6jb5CUvfVqcesODupB1VVB8yLDWbS/Ng6bkj7aii5pOFqdlcOgQLcFrakaG2/myT8UzVndzCfwzwKflKOqcdsIK0m6wjJ8hcspq8JzdIN+/X5WBRxvj15CW5BKvSXWBaTg6TA2SVe8dg/9IA++4mWeJtZdg5VJ7d/5QqpFavlPhBW8kKb48hMyP/qLcnwgIJ/t/Gl1C5guPJg+j9McoXjE9kmbf11OSFSblHJns7U73JXdjgV7AAdSXT9Ux+vz8j7XzUjMrfjPLxMgR2tdM5qSMm+FnjS6gMcA8swE3OaTLW+z6Qod7Wea2VD7pOZkXvuTXQUcpoAjZEfaq6Sp/tkZc1/jIsQKXwCFgan/S+VO/IYG/rG10hg66S2dF7bu0nI709ieyN+taQ12RC5GWNP0OWkqmw9BxNXsAKkDSdjPK2VjAEqH0dB6gr5pzoPbeUfgfJRlgx0AoE6Wx7hsrqmTV+BuzndqI8XumnS/8ulIuMCoku96dg+/cKeUNWwiZUxe0iGe7jm1RdYfunmmrvTx1FaofJ0JVRSPLCUdUk2gdLHZV57bdWp7XkOKlPOwoVyq/f7aSDTIygswwAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADwAAAAaCAYAAADrCT9ZAAACp0lEQVR4Xu2XWchNYRSGX/NYxkwXSIZEkrgx5JSh5EaROcmVDCnKXBTKkBSRKUWRoVwZMx1FkllkCBdSxA1KpsL7ttZm/8uFf/9DnN9+6ul839r7nPOtb9rfBnJycnJy/n0m0O/0A31E79F3HntD79Mn9DP9QofY10qXU3QVbZCKnYUl3CMV60S/0japWMnRml4OsYb0I30e4uJODJQas+jkEBsOG93dIa6OOBNiJUcXWj/E1sIS1tpOU5d2C7EawQ36DTbdazytYMnejBeqiZExUAE60N4xWF7Gwabz+nihmjgaAxVgPJ0Yg+VlOyzhquj5PzGFPojBjLSg11CJhJ/ST7RRvOCMpYfpOnqONqG16FKPbaDz/d4R9DE94te30hO0Du1Jj9O3sKdB8qRoT/fS1fQQ7QjbPK/AHpX96UX6ii6mi+hLeh72O02RAe3AGt1iiCdonbymzWhzeom2pXPpztR9++lULy+gz2g9r7+gfb1coA+9nHAB1qlCnXDAy41hp8AC3QP7/4QiMoywevQWvQ3rNSWsI6SOk4p3/nknsALWoMh1OiNVX0hPe3kebIQTNOIDvVxA2YSVhP5/M11JN6LsWWAwfY/fl1sRGRLOgqaZpnHkLp2Zqi+Bjb6YQw+mrinBQV4e6nUxBr8S7uWxSHdYh20JcQ2CEtaZok+4Vin6wXq4ndf1EjEAtj41zRI0orO9rBFOJ6xpqZES+q6mu1jjn1rj6jChvWGZl7Xud9GWsH1mmMeF9oJpsD1DnVilTIL1qEZba1fUhjV4B91Gl8Maq8Suws7kmvJaEnojO0a7wk5uJ2GJjIKhw442q32wDVCb23TYGV5vcUK7st7iNnl9NOx9QEtAbflraFSUuFByUqhRWRqm7+l3ko0vHc/JyfmP+AH4lIXnuUmTiQAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAACs0lEQVR4Xu2WWaiNURTH/2aiZEimMmR4kTwpIS+GQqRkKkOKrqGUhGQKSUKGiPJkCJmLyHg9yJSpEOFFihLyYBb+/9be5/us20E699Z3fL/6dfe39r6ns7619zobyMnJycmpPsbSH/Q9fUTv0Xch9orep0/oZ/qF9rd/yxan6UraIBU7B0uyeyrWgX6lrVKxTNCSXnaxhvQjfebi4q4PZIGZdIKLDYRVcaeLK/mzLpYJOtP6LrYGlqTOapq6tKuLZZab9DtsK5clLWAJ3vITZBGsA09x8cgRutQHHW1pDx+saUbDtupaPxE4huJJTqZDfNAxho7zwZpmOyzJwX4icBTFk/wTzegN/HuStYKiTuq5dmHFX/KUfqKN/ETgMN1Al9BTdGGI94ElsCU8D6Wr6Hx6nTanC+gLegHWuZuEtSPpVrqCbqSN6Qj6mB6ne+kJWNM7A7uQTKJdYJcVdfxi37cK+hBVsdLF0xyi+8JY69+m5ubQPWF8BclFQomqiqISv1ayF+yGFasxDclP13J6jbajs0KsKf1AO4XnzeHvb2lDb9M79CUsSV3fdJVTvGNhpaEkZ4exmojeamQGkiSXwS4Ul+jEwoqqSa6ju1LPvWFJaDsuhh0fz0FYE2xP57q5kqAOWhHGrWHXvIjiMclutB+s274JY3ERlqR+n3vCKrE/zAlt+2+wi4eS3JSai2grqwjzYImWHHXXmKR2gb5QJF3J80guGTpro8L4JOw8DaIDaF/6EHbRENqWqpTQudcZ9dSjr+kBP1EKptLn9CodDmsI2t47YJXSOVTj0ptWxVUFVUPVigkPg92V1yM5h+PpblhC2p46d1r3APZ52voerZvug6Ugvm21bb1NnRuhseb0pTUX11UnenmxmZUVOsfaRdoVq91c2aDfWm31bbDOnvNf8RPJKIcTd3FdNgAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,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>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAaCAYAAAAue6XIAAACDklEQVR4Xu2WXWjPURjHH+ZlyMtysZWIC3eKkrVSwy4sL5fk7UpxwQVys5KsRpu0lWI1ciPkLXEna5uUiFJKuXLBhZeScqEs759vz3Py67RWavv/p36f+rRzzvP//f/Pec75nTOzkpKSktGowwP4AF/jS3yGeyLeg+ujXVWU0Ce8jatxcoxPxTP4GIdxZoxXhUl4Dn/g7iyWUMLv8F4eqDSd+Bvb8kBGPx7MBytJI/7EN+bVGw1Vf0k+WElumlf1cB6YiHw2T3ZFHphoaNmV6DesyWI5O3FhPlhp3uIvnJUHCszBQfNTo6ocN6/utjwQ1OINXBX9BfjI/LI4hB34HDeanybX8GR8VugS0Rl9Hs/iFJyOl/CL+TuzzrxgD3GRPzYyM3DI/DLYYX9PBFVxLd7BNTGWWGk+waXRv4x3oz0Pv5snJHqxKdr6na3RFnvNV6zF/uFI1Bfvwyfm2+Kp+ZmqSs0tfC6xHD8W+qrasWhPM5+Ito6ox3bswhfmV3kRXTL6rXFjGX4o9PvwaLS1zEpWk5xvPvnWiF0xr2Dxuu7G97i4MDamqLLFZHVZpGTTCaPtoL2o7ZXQkmufn4j+BtyF+/G+jcML3IC3zI+7U7gdX5m/ZJvxgnmyF3E2XsXT5gkdMf9vbgtex6/R3hTPDGCzjSGafTqTVUUtu8ak2lKkvyORviM9k4+XlPz3/AH5KV7/sZKZBAAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAaCAYAAAANIPQdAAACQElEQVR4Xu2WS0hVURSGVxSZsywxnVgIFdFEnAlGCCEYBIWBEQWNFJoFJVlakg4qUTOIipzUIJIeNIqiJIUiEHooqQXVQAiCMGjQ017/z1rbu915MbiYnMv+4OPsu/a65551zj77LpFIJBKJzB218Df8BF/C5/Cjxd7DEfgKfoPf4Qb9WrK4DVthjhe7J1rkWi+2Ek7CAi+WCPLhwyC2BH6B40GcDIWBJLAX7gxim0SfYk8QZ/F3g1giKIGLg9hx0SL5rvosgquDWGJ5DH+JLuWsZLlogU/CiWxiu+hSPRlOZBPnRIusCif+MwtmOWbEa/gV5oYT4BCcEL0R3GUPWrwOnodn4D6LbYZtsAEOwmUWnyn3JvwMD8BRWAmviN7sC5bD+Bgsg0Xwouj5e2Gx5fwT3Dl54v4g7tMPT4h2PdVwIxz25l+INhCP7EhYaJ6kz10If4qeb4+kdvAHcJeNm+EKG9+HNTbm399lG6eFd+UpfAbfiRbJ9o2tHOOrpjIVdkI7vM+nRC+8xbwOK+BR0YZiAO6eJZf8gIU2dtTDOzbutONS0Ws8LXqODvn7/zxjWOQ273MXvOp9dqwRLeAI/GDjdLmERfJp+3CJcxlvldR/tityvUuaC/pEf9RRDt9K6gL5LvK9YZ5rMo6J3ph0uYTLlQWE3IBvZPoecQs22pgb0WFvLmP2i2487HX9bojvBZt8Lim3mfDiumGT6NJyBc+Ue0n06VyDpRZzbIFngxibFG44/F47XDd9OhKJROaZP4NBe+YlQnWqAAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADQAAAAaCAYAAAD43n+tAAACS0lEQVR4Xu2WS4hPYRjGHwbDjkjNZkg0yUbKwmUyC9QoRZSJnQWFGmKBSTRjGpeYSSnCgoVIrNzKbRYsLDA0k0tYiFJSLORWeJ7e98x88y70Hw1zJudXv/7fec6ZM+c93+V8QEFBQcH/wAr6k36iT2kn/ejZO9pFn9Ov9Buttj/LL1dpEy1PsuuwgqqSbAL9TscnWe4YR++EbCT9TF+FXDyMQd5YR1eGbD6sd46HXIVeC1numERHhGwPrCDNrZRhdErIBgX36A/YcBz0jIUVcz+eGGAWxqBUlsOG2754YoC5EINSOQIr6I/fyF9gFX0cw1J5Qb/QUfEE2U7fw4rWarfV8zX0KD1MN3k2hDbSE26b5xX0JN1Nz9JKuoA+o+dg/0P3uUzL6FR6iX6ArbpxRf4tWsHUO+0hT2mne2G7hVo6jz5Kzj+BfYzX0pue6dpsyNyiy7ythzvt7c30JR3ux6/pdG/XwO5bEnpjD2gHfQsrSFscbXeUT+y+0tAOoi451ptXQbvc83Qu7MF3dl9ljIbd/xDs2gPo+dbVw3ooQz0229s16ENBfUUFLU2OW9H7QTJu0x0hywqaFnKxgZ5JjlXAHG9rFGQFLfHffuMGet90Fn1Dx/jxIjqDbqR3YR9jsR6209Dc2OaZ5lmDt9VDaUHaJKunxUzYcBTN/tsvbIEtCtr7pbsIzQVtcA+iZ1EYSltgBainFnuuj7UWg1N0P2zS68FVvPaOq2FDVTv/i3Qy7KVcocdg8zb3aDVTbwk9fNareimyoKDgH/ELnAN0iXGVoHEAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAZCAYAAABzVH1EAAACnklEQVR4Xu2WS8gPURjGH5fIpVz6ZOmztlEoxQpZyrUIWWCFQkmsRrluPjs2LtlYsGAhkmKFLFAWbiEsUO6XSK7P03vOf855/38zs7GbXz3NmfO85zTvzJz3HKClpaWOjdQn6k/Q/dzu4gDK2K/UhdzOmEe9oIZ4I+EV9Q3lnO+pN0Hqv0Gt7kQ3QA/4HDbZdOdFBsMeXDFPwn0VR2Gxc73h6IPFKamUMdQ26gd1jBqU270pqH2wCQ/mVoc51HY0+3JDqbew2EPO84yGxelF9kJfRP5mb/SioBZSj6mX6P07HKH60SwR/VaXqd+w36vq68VEnrr+lNvUO2qcNzwFLJE9sEnnZy4wnDof2k0SOUwtoa7C4mfldkaTRPbDYrSmKylgiUyBDTiRufZQm0K7LhG9fa2hUdRWWPxAFpHTJJE1sJjT3vAUsETEHeozNbLjAqeoiaFdl8hs6mxoT4bFPyvtLpokomdTzENveAqUieyADVoR7sdS50Jb1CWiYrEqub8JGzMj6UtpksgCWIy+dCUFykT6YYPiw6+j1oa2qEtEb02lM7ITNkYlvhdNEomV64o3PAW1KLm/BqvfqvEXkVeLqkSmUd9he0LUa9iYR0lcSpNE9sJidnnDU1CLk3stbA3U3nIm6RdViSh+ve8k92DjpnoDzRK5BXuxWnOVFLDKFNHC/kn9opYn/aIqkbvUBN9JdsPG6eqpS2QpzNdXqUTVSUcP1ep047pEfYGV0cgI2KRadP7IsAz2G413/WImbNwDdG+2SlyeNs4U/c5bYGe6k+gel7EB9tY1kaRBcfPSAjse2kK7vvwYq8OmCsIk2GEv9muNpOc1bY4q59H/gHJz9YfGj7CXoRj1X6dWhtj/jr7iMN/Z0tLS0vIv/gJyjsLES2mkRgAAAABJRU5ErkJggg==>

[image11]: <data:image/png;base64,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>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAZCAYAAABHLbxYAAACJklEQVR4Xu2WzUtVQRjGX21Rin1gi1poREREhdGmRQSJfbqooCATikgK0YiICJdaFEHQJigIV24iiBAiKmzhwkoiciFWm+ofSIg+XGSYPg/vnNucp3u8RncjnB/8uMwzc88MM2dmjllOzvxhPxyFP8LvaViRapFNC3wNh+Aw3JeuLh+74AhcAZfAW3AaXokbZXAATsB1obwFfoc7Ci3KCGchfvAC+BH+hvVRXox38I5k9+ALyf4bDmoKfoJLo7zXfFbbo0zZaN7mrOQ9IecKlY1K+MX8wWuj/EbIzkeZcsy8zQnJ+R/meyU/JGVlD6zWMIbv1W7JBsw70zzmonmbVsnPhLxN8mvwqmQJR+AD8xWeM6vgL/jWfMaz6DYf0FHJO0J+TnJyG16WjBvyKVwkeUnuwm+wQSuEHvv3gfLI64NdocwVG4Q1hRZz5Lj5cdMoeTGylr4z5KckT+Dy3oc34XO4LF1dms1wHDZpRQYcIAd0UvJkM8128PPs5oRc0IpS1ML3ln54o/mtk8V68wFpZ9wwzFdKnrDV/Carg/3296uTCZfiMTws+SV4MCrz3GyOyoQHPs/cmIfwpWQJfO/fmA+SLISPzDdUSa6bL8NYkLv9A/wJN4Q23ASfzWcq3mTs4CvcFMrb4CTcXmjxB16znMnVkvPsfAZ3Sp6iyrzzYvIKjY+MJ+Y32PIoI1w6fiu8Mp/JrA45c2s0DCw2fz6/NXJycnLmCzNT7W+EszanHgAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAY0lEQVR4XmNgGAWjYPiCJHQBaoDtQCyGLkgpCATiDnRBaoCVQOyELogMlgHxETLwTSD+B8TNDFQCqgwQg43RJcgF7EB8FIgV0MQpArlAnIEuSCk4AMSc6IKUAhN0gVEwCiAAACBLE8KU5AMmAAAAAElFTkSuQmCC>
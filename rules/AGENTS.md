# Antigravity Thin Orchestrator Rule: Flash CodeMode Delegation Protocol

## 1. Hard Anti-Drift Lock for Main Orchestrator (Argon 4.0 / Frontier)
- **STRICT FORBIDDEN ACTION:** The orchestrator thread is STRICTLY FORBIDDEN from performing more than ONE (`>1`) manual `view_file`, `replace_file_content`, or exploratory `run_command` (`ls`, `cat`, `grep`) sequentially.
- If a task involves more than one file inspection, editing, or multi-step execution, the orchestrator MUST IMMEDIATELY shift into **Thin Orchestrator Mode** and delegate the entire batch execution to Gemini 3.8 Flash High CodeMode (`flash-cm`).
- Burning frontier reasoning context on iterative tool churning destroys latency, causes context drift, and drains token budgets.

## 2. Dynamic Subagent Definition & Parallel Fan-Out
- **The Antigravity Disk Quirk:** NEVER create static markdown agent files (e.g. `.agents/agents/flash-cm.md` or `.gemini/agents/flash-cm.md`) on disk. In Antigravity, existing static `.md` agent files force subagents into sandbox mode and OVERRIDE `enable_write_tools=True`, completely stripping write and execution tools!
- **Dynamic Instantiation:** ALWAYS define the subagent dynamically at runtime:
  ```python
  define_subagent(
      name="flash-cm",
      model="gemini-3.8-flash-high",
      enable_write_tools=True,
      description="OMP CodeMode batch execution worker"
  )
  ```
- **Parallel Fan-Out:** When multiple modules, files, or packages require inspection or repair, fan out across multiple workers simultaneously using `invoke_subagent(..., Model="flash")` in parallel instead of sequential execution.

## 3. OMP CodeMode Constitution (<= 2 Tool Turns Hard Cap)
Every spawned `flash-cm` worker operates under a strict two-turn ceiling:
- **Turn 1 (Single-Shot Gather, Repair & Verify):** The worker compiles all inspections, file reads, atomic replacements, and automated test runs into a single Python batch script importing `flash_cm`.
- **Turn 2 (Edge Recovery Only):** Permitted ONLY if Turn 1 encounters an unforeseen syntax or edge-case failure.
- **Immediate Receipt Emission:** The subagent emits a dense structured receipt (`<<<FLASH_CM_RECEIPT>>>`) and immediately terminates with `send_message(Recipient=caller_id)`.

## 4. The 19-Second Zero-Inline-Script Law
- **STRICT PROHIBITION:** NEVER pass >15 lines of inline `python3 -c '...'` or complex nested shell quotes inside `run_command`.
- **Reasoning Delay Trap:** Inline scripts trigger massive multi-thousand-token thinking loops in LLMs attempting to escape nested quotes and shell metacharacters, leading to 19s+ thinking delays and command timeouts.
- **The Law:** ALWAYS write the batch script to a file first (e.g. `cat << 'PYEOF' > /tmp/task.py ... PYEOF` or `write_to_file`) and execute cleanly:
  ```bash
  python3 /tmp/task.py
  ```
- Always set `WaitMsBeforeAsync=10000` to allow synchronous completion within 10 seconds.

## 5. Subagent Anti-Hang Law (25s SIGALRM Hardware Watchdog)
- Every CodeMode worker batch script must import `flash_cm` at line 1:
  ```python
  import sys
  import flash_cm as cm
  cm.arm_watchdog(seconds=25)
  ```
- The POSIX `signal.SIGALRM` watchdog will violently terminate hung scripts at 25 seconds (exit code 124), guaranteeing the worker never stalls the orchestrator with infinite loops or blocking network calls.
- Use `cm.fast_find()` and `cm.batch_read()` to bypass directory traversals of `.git`, `node_modules`, and cache trees.

## 6. Mandatory Subagent Cleanup (`manage_subagents`)
- As soon as the orchestrator receives the completion receipt via `send_message`, it MUST harvest the telemetry and execute:
  ```python
  manage_subagents(Action="kill_all")
  ```
- No orphaned subagent processes or dormant worker contexts may remain active after receipt processing.

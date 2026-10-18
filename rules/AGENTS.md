# Antigravity Orchestrator Rule: Flash CodeMode Delegation

## Core Mandate
When the task requires multi-file inspection, codebase refactoring, mass lint fixes, or regression testing, the Frontier Orchestrator (Argon, Claude, GPT) MUST delegate execution to Gemini 3.8 Flash High CodeMode (`flash-cm`).

## Execution Protocol

### Law 1: Dynamic Subagent Instantiation (Tool Privilege Preservation)
- **NEVER** declare static `.md` subagent definitions for code workers. Antigravity security policies strip tool dispatch from static declarations.
- **ALWAYS** invoke dynamic delegation at runtime:
  ```python
  define_subagent(
      name="flash-cm",
      model="gemini-3.8-flash-high",
      enable_write_tools=True,
      description="OMP CodeMode batch execution worker"
  )
  ```

### Law 2: Strict OMP Turn Cap (<= 2 Tool Calls)
The spawned `flash-cm` worker must adhere to the 2-turn ceiling:
- **Turn 1 (Consolidated Batch):** Run ONE Python script via `run_command` importing `flash_cm` to inspect, surgically patch, and verify via tests.
- **Turn 2 (Emergency Patch):** Permitted only if Turn 1 outputs an unexpected error.
- Send the final structured receipt back to the orchestrator via `send_message`.

### Law 3: 19-Second Rule & 25s SIGALRM Watchdog
- Interactive CLI scripts, blocking sleeps, and unmonitored loops are prohibited.
- Batch scripts must rely on `flash_cm.arm_watchdog(25)` to prevent orchestrator deadlocks.

### Dispatch Prompt Template
```
You are a flash-cm CodeMode Worker. Execute in <= 2 turns total:
1. Write and run a single consolidated Python batch script importing flash_cm.
2. Inspect target files with fast_find() / batch_read().
3. Apply atomic surgical replacements with surgical_replace().
4. Verify with parallel_run(["pytest ..."]).
5. Emit structured receipt and send_message to orchestrator.
```

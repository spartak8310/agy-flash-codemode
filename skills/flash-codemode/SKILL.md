---
name: flash-codemode
description: Dispatches high-velocity programmatic batch code refactoring and multi-file repairs using Gemini 3.8 Flash High CodeMode in <= 2 turns.
version: 1.0.0
---

# Flash CodeMode Skill

## Purpose
Enables Frontier Orchestrators (Argon, Gemini, GPT) to offload complex file inspection, batch transformations, and verification runs to Gemini 3.8 Flash High CodeMode.

## Trigger Conditions
Use this skill when:
- Inspecting or modifying more than 2 files across a workspace.
- Resolving compiler, linter, or test failures across multiple modules.
- Performing fast regression verification without burning frontier context.

## Execution Sequence
1. Orchestrator calls `define_subagent(model="gemini-3.8-flash-high", enable_write_tools=True)`.
2. Worker launches a single batch script importing `flash_cm`.
3. Worker runs automated verification and emits `<<<FLASH_CM_RECEIPT>>>`.
4. Worker sends receipt via `send_message(Recipient=caller_id)`.

"""
flash_cm - Antigravity Flash CodeMode Portable SDK
Zero-dependency, high-velocity programmatic batch execution library for Gemini 3.8 Flash workers.
"""

import os
import sys
import time
import json
import fnmatch
import signal
import subprocess
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Any

__version__ = "1.0.0"

# ==============================================================================
# 1. 25-Second SIGALRM Hardware Watchdog
# ==============================================================================

def _watchdog_handler(signum, frame):
    sys.stderr.write("\n[FATAL] 25s Hardware Watchdog Expired! Terminating batch worker.\n")
    sys.stderr.flush()
    os._exit(124)  # Standard POSIX timeout exit code

def arm_watchdog(seconds: int = 25) -> None:
    """Arms POSIX SIGALRM timer to terminate the process if execution stalls."""
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _watchdog_handler)
        signal.alarm(seconds)
    else:
        sys.stderr.write("[WARN] SIGALRM not available on this platform.\n")

def cancel_watchdog() -> None:
    """Cancels any active SIGALRM timer."""
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)

class watchdog_scope:
    """Context manager for hardware watchdog."""
    def __init__(self, seconds: int = 25):
        self.seconds = seconds

    def __enter__(self):
        arm_watchdog(self.seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cancel_watchdog()

# ==============================================================================
# 2. High-Performance File Search & Batch Read
# ==============================================================================

def fast_find(
    root: str = ".",
    pattern: str = "*",
    max_results: int = 100,
    ignore_dirs: Optional[List[str]] = None
) -> List[str]:
    """Fast recursive file discovery ignoring junk and cache directories."""
    if ignore_dirs is None:
        ignore_set = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", ".idea", ".vscode", ".tox", ".pytest_cache"
        }
    else:
        ignore_set = set(ignore_dirs)

    results = []
    root_path = Path(root).resolve()

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in ignore_set and not d.startswith(".")]
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                results.append(str(Path(dirpath) / filename))
                if len(results) >= max_results:
                    return results
    return results

def batch_read(files: List[str], max_bytes_per_file: int = 65536) -> Dict[str, str]:
    """Safely reads content of multiple files with byte capping."""
    data = {}
    for f in files:
        path = Path(f)
        if path.is_file():
            try:
                with open(path, "rb") as fp:
                    raw = fp.read(max_bytes_per_file)
                    data[str(path)] = raw.decode("utf-8", errors="replace")
            except Exception as e:
                data[str(path)] = f"<ReadError: {e}>"
    return data

# ==============================================================================
# 3. Atomic Surgical String Replacement
# ==============================================================================

def surgical_replace(file_path: str, old_str: str, new_str: str, count: int = 1) -> bool:
    """Performs an exact atomic replacement of old_str with new_str in file_path."""
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    if old_str not in content:
        raise ValueError(f"Target string not found in {file_path}")

    new_content = content.replace(old_str, new_str, count)
    tmp_path = path.with_suffix(path.suffix + f".tmp_{os.getpid()}")
    try:
        tmp_path.write_text(new_content, encoding="utf-8")
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return True

# ==============================================================================
# 4. Parallel Command Execution
# ==============================================================================

def parallel_run(
    commands: List[str],
    max_workers: int = 4,
    timeout: int = 20
) -> List[Dict[str, Any]]:
    """Runs shell commands in parallel threads with timeout protections."""
    def _execute(cmd: str) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            res = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = round((time.perf_counter() - start) * 1000, 2)
            return {
                "command": cmd,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "duration_ms": duration,
                "success": res.returncode == 0
            }
        except subprocess.TimeoutExpired:
            duration = round((time.perf_counter() - start) * 1000, 2)
            return {
                "command": cmd,
                "returncode": 124,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "duration_ms": duration,
                "success": False
            }
        except Exception as e:
            duration = round((time.perf_counter() - start) * 1000, 2)
            return {
                "command": cmd,
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": duration,
                "success": False
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_execute, commands))

# ==============================================================================
# 5. Environment Telemetry & Sanitization Audit
# ==============================================================================

def audit_telemetry() -> Dict[str, Any]:
    """Collects host environment details while strictly masking any credentials."""
    git_branch = None
    git_commit = None
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            git_branch = res.stdout.strip()
        res_hash = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=2)
        if res_hash.returncode == 0:
            git_commit = res_hash.stdout.strip()
    except Exception:
        pass

    sensitive_keywords = ["TOKEN", "SECRET", "KEY", "AUTH", "PASS"]
    detected_env_keys = [
        k for k in os.environ.keys()
        if any(w in k.upper() for w in sensitive_keywords)
    ]

    return {
        "sdk_version": __version__,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "sensitive_env_keys_detected": sorted(detected_env_keys),
        "status": "HEALTHY"
    }

# ==============================================================================
# 6. Structured Receipt Emission
# ==============================================================================

def emit(receipt: Dict[str, Any]) -> None:
    """Emits structured JSON receipt to stdout."""
    payload = json.dumps(receipt, indent=2, ensure_ascii=False)
    sys.stdout.write(f"\n<<<FLASH_CM_RECEIPT>>>\n{payload}\n<<<END_FLASH_CM_RECEIPT>>>\n")
    sys.stdout.flush()

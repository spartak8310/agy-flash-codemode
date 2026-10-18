#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="agy-flash-codemode"
CONFIG_BASE="${ANTIGRAVITY_CONFIG_DIR:-$HOME/.gemini/config}"
TARGET_PLUGIN_DIR="${CONFIG_BASE}/plugins/${PLUGIN_NAME}"

echo "=========================================================="
echo "⚡ Installing agy-flash-codemode Antigravity Plugin"
echo "=========================================================="

# 1. Plugin Definitions
echo "[1/3] Installing Antigravity rules & skills..."
mkdir -p "${TARGET_PLUGIN_DIR}/rules"
mkdir -p "${TARGET_PLUGIN_DIR}/skills/flash-codemode"

cp -f "${SCRIPT_DIR}/rules/AGENTS.md" "${TARGET_PLUGIN_DIR}/rules/AGENTS.md"
cp -f "${SCRIPT_DIR}/skills/flash-codemode/SKILL.md" "${TARGET_PLUGIN_DIR}/skills/flash-codemode/SKILL.md"
echo "  -> Installed at: ${TARGET_PLUGIN_DIR}"

# 2. Python SDK Installation
echo "[2/3] Installing flash_cm Python SDK..."
USER_SITE="$(python3 -m site --user-site 2>/dev/null || true)"
if [ -z "${USER_SITE}" ]; then
    USER_SITE="$HOME/.local/lib/python3/site-packages"
fi
mkdir -p "${USER_SITE}"
cp -f "${SCRIPT_DIR}/sdk/flash_cm.py" "${USER_SITE}/flash_cm.py"
echo "  -> SDK installed at: ${USER_SITE}/flash_cm.py"

if command -v pip3 >/dev/null 2>&1; then
    pip3 install -q --no-deps -e "${SCRIPT_DIR}" 2>/dev/null || true
fi

# 3. Verification
echo "[3/3] Verifying installation..."
python3 -c "import flash_cm; print('  ✓ flash_cm imported successfully (v' + flash_cm.__version__ + ')')"

echo "=========================================================="
echo "✓ Installation complete! Flash CodeMode is ready."
echo "=========================================================="

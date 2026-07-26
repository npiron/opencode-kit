#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

KIT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENDIR="${HOME}/.config/opencode"

echo -e "${GREEN}opencode-kit installer${NC}"
echo "Kit source : ${KIT_DIR}"
echo "Target     : ${OPENDIR}"
echo ""

if ! command -v opencode &>/dev/null; then
    echo -e "${YELLOW}⚠ opencode is not installed.${NC}"
    echo "  → curl -fsSL https://opencode.ai/install.sh | sh"
    echo ""
fi

if ! command -v bun &>/dev/null; then
    echo -e "${YELLOW}⚠ bun is not installed (needed for plugins).${NC}"
    echo "  → curl -fsSL https://bun.sh/install | bash"
    echo ""
fi

mkdir -p "${OPENDIR}/agents"
mkdir -p "${OPENDIR}/skills"
mkdir -p "${OPENDIR}/tasks"
mkdir -p "${OPENDIR}/plugins"
mkdir -p "${OPENDIR}/memory/sessions"
mkdir -p "${OPENDIR}/heartbeat"

echo "→ Installing agents..."
for file in "${KIT_DIR}/agents/"*.md; do
    if [[ -f "$file" ]]; then
        name=$(basename "$file")
        target="${OPENDIR}/agents/${name}"
        if [[ -L "$target" ]] || [[ -f "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (already exists)"
        else
            ln -s "$file" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

echo "→ Installing skills..."
for skill_dir in "${KIT_DIR}/skills/"*/; do
    if [[ -d "$skill_dir" ]]; then
        name=$(basename "$skill_dir")
        target="${OPENDIR}/skills/${name}"
        if [[ -L "$target" ]] || [[ -d "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (already exists)"
        else
            ln -s "$skill_dir" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

echo "→ Installing tasks..."
for file in "${KIT_DIR}/tasks/"*.md; do
    if [[ -f "$file" ]]; then
        name=$(basename "$file")
        target="${OPENDIR}/tasks/${name}"
        if [[ -L "$target" ]] || [[ -f "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (already exists)"
        else
            ln -s "$file" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

echo "→ Installing plugins..."
for plugin_dir in "${KIT_DIR}/plugins/"*/; do
    if [[ -d "$plugin_dir" ]]; then
        name=$(basename "$plugin_dir")
        target="${OPENDIR}/plugins/${name}"
        if [[ -L "$target" ]] || [[ -d "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (already exists)"
        else
            ln -s "$plugin_dir" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

echo "→ Installing heartbeat config..."
for file in "${KIT_DIR}/heartbeat/"*; do
    if [[ -f "$file" ]]; then
        name=$(basename "$file")
        target="${OPENDIR}/heartbeat/${name}"
        if [[ -L "$target" ]] || [[ -f "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (already exists)"
        else
            ln -s "$file" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

echo "→ Configuration..."
if [[ -f "${OPENDIR}/opencode.jsonc" ]]; then
    echo "  ${YELLOW}skip${NC} opencode.jsonc (already exists, manual merge recommended)"
    echo "  Template available : ${KIT_DIR}/config/opencode.jsonc"
else
    cp "${KIT_DIR}/config/opencode.jsonc" "${OPENDIR}/opencode.jsonc"
    echo "  ${GREEN}copy${NC} opencode.jsonc"
fi

echo "→ Installing opencode-tasks scheduler..."
if command -v bun &>/dev/null; then
    bunx opencode-tasks --install 2>/dev/null && \
        echo "  ${GREEN}ok${NC} opencode-tasks daemon installed" || \
        echo "  ${YELLOW}skip${NC} opencode-tasks (install manually: bunx opencode-tasks --install)"
else
    echo "  ${YELLOW}skip${NC} opencode-tasks (bun not found)"
fi

echo "→ Dashboard..."
mkdir -p "${OPENDIR}/scripts"
dash_source="${KIT_DIR}/dashboard/main.py"
chmod +x "$dash_source"

# Symlink in ~/.config/opencode/scripts/
dash_target="${OPENDIR}/scripts/crush-dash"
if [[ -L "$dash_target" ]] || [[ -f "$dash_target" ]]; then
    echo "  ${YELLOW}skip${NC} ${OPENDIR}/scripts/crush-dash (already exists)"
else
    ln -s "$dash_source" "$dash_target"
    echo "  ${GREEN}link${NC} ${OPENDIR}/scripts/crush-dash → dashboard/main.py"
fi

# Symlink in /usr/local/bin for global access
if [[ -d "/usr/local/bin" ]]; then
    bin_target="/usr/local/bin/crush-dash"
    if [[ -L "$bin_target" ]] || [[ -f "$bin_target" ]]; then
        echo "  ${YELLOW}skip${NC} /usr/local/bin/crush-dash (already exists)"
    else
        sudo ln -s "$dash_source" "$bin_target" 2>/dev/null && \
            echo "  ${GREEN}link${NC} /usr/local/bin/crush-dash" || \
            echo "  ${YELLOW}skip${NC} /usr/local/bin/crush-dash (sudo required)"
    fi
fi

if ! python3 -c "import textual" 2>/dev/null; then
    echo "  ${YELLOW}⚠  'textual' Python package missing. Install with: pip3 install textual${NC}"
fi

echo "→ Scripts..."
for script in "${KIT_DIR}/scripts/"*.sh; do
    if [[ -f "$script" ]]; then
        chmod +x "$script"
    fi
done
echo "  ${GREEN}ok${NC} scripts made executable"

echo ""
if [[ ! -f "${OPENDIR}/.env" ]]; then
    if [[ -f "${KIT_DIR}/.env.example" ]]; then
        cp "${KIT_DIR}/.env.example" "${OPENDIR}/.env"
        echo -e "${YELLOW}⚠  Created ${OPENDIR}/.env — fill in your API keys!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Notes :"
echo "  • Edit ${OPENDIR}/opencode.jsonc to configure your AI providers"
echo "  • Edit ${OPENDIR}/.env to set your API keys"
echo "  • Heartbeat logs : ${OPENDIR}/heartbeat/heartbeat.log"
echo "  • To update : git pull in ${KIT_DIR}"
echo "  • Dashboard : crush-dash (or python3 ${KIT_DIR}/dashboard/main.py)"
echo ""
echo "Heartbeat Pouls setup (manual) :"
echo "  1. Create Gmail labels: AgentTrigger, AgentProcessed"
echo "  2. Create Gmail filter: subject:[AGENT] → label AgentTrigger + archive"
echo "  3. Create Drive folder: Pouls/Heartbeat/"
echo "  4. Edit ${OPENDIR}/heartbeat/repos-whitelist.txt"
echo "  5. The heartbeat runs every hour via opencode-tasks daemon"

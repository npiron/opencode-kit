#!/usr/bin/env bash
set -euo pipefail

# ─── opencode-kit installer ───────────────────────────────────────────────
# Installs the kit by creating symlinks from the repo to
# ~/.config/opencode/. No copy, no overwrite without backup.
# ──────────────────────────────────────────────────────────────────────────

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

# ─── Pre-flight checks ────────────────────────────────────────────────────

if ! command -v opencode &>/dev/null; then
    echo -e "${YELLOW}⚠ opencode is not installed.${NC}"
    echo "  → brew install charmbracelet/tap/crush"
    echo ""
fi

# ─── Create target directories ─────────────────────────────────────────────

mkdir -p "${OPENDIR}/agents"
mkdir -p "${OPENDIR}/skills"
mkdir -p "${OPENDIR}/memory/sessions"

# ─── Symlink agents ────────────────────────────────────────────────────────

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

# ─── Symlink skills ────────────────────────────────────────────────────────

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

# ─── Merge config ──────────────────────────────────────────────────────────

echo "→ Configuration..."
if [[ -f "${OPENDIR}/opencode.jsonc" ]]; then
    echo "  ${YELLOW}skip${NC} opencode.jsonc (already exists, manual merge recommended)"
    echo "  Template available : ${KIT_DIR}/config/opencode.jsonc"
else
    cp "${KIT_DIR}/config/opencode.jsonc" "${OPENDIR}/opencode.jsonc"
    echo "  ${GREEN}copy${NC} opencode.jsonc"
fi

# ─── Scripts ───────────────────────────────────────────────────────────────

echo "→ Scripts..."
for script in "${KIT_DIR}/scripts/"*.sh; do
    if [[ -f "$script" ]]; then
        chmod +x "$script"
    fi
done
echo "  ${GREEN}ok${NC} scripts made executable"

# ─── Done ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Notes :"
echo "  • Edit ${OPENDIR}/opencode.jsonc to configure your AI providers"
echo "  • Import your Knowledge Graph : ./scripts/import-kg.sh <export_file>"
echo "  • Session archives (L3) are stored in ${OPENDIR}/memory/sessions/"
echo "  • To update : git pull in ${KIT_DIR}"

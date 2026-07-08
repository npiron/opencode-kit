#!/usr/bin/env bash
set -euo pipefail

# ─── opencode-kit installer ───────────────────────────────────────────────
# Installe le kit en creant des symlinks depuis le repo vers
# ~/.config/opencode/. Pas de copie, pas d'ecrasement sans backup.
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
    echo -e "${YELLOW}⚠ opencode n'est pas installe.${NC}"
    echo "  → brew install charmbracelet/tap/crush"
    echo ""
fi

# ─── Create target directories ─────────────────────────────────────────────

mkdir -p "${OPENDIR}/agents"
mkdir -p "${OPENDIR}/skills"
mkdir -p "${OPENDIR}/memory/sessions"

# ─── Symlink agents ────────────────────────────────────────────────────────

echo "→ Installation des agents..."
for file in "${KIT_DIR}/agents/"*.md; do
    if [[ -f "$file" ]]; then
        name=$(basename "$file")
        target="${OPENDIR}/agents/${name}"
        if [[ -L "$target" ]] || [[ -f "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (existe deja)"
        else
            ln -s "$file" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

# ─── Symlink skills ────────────────────────────────────────────────────────

echo "→ Installation des skills..."
for skill_dir in "${KIT_DIR}/skills/"*/; do
    if [[ -d "$skill_dir" ]]; then
        name=$(basename "$skill_dir")
        target="${OPENDIR}/skills/${name}"
        if [[ -L "$target" ]] || [[ -d "$target" ]]; then
            echo "  ${YELLOW}skip${NC} ${name} (existe deja)"
        else
            ln -s "$skill_dir" "$target"
            echo "  ${GREEN}link${NC} ${name}"
        fi
    fi
done

# ─── Merge config ──────────────────────────────────────────────────────────

echo "→ Configuration..."
if [[ -f "${OPENDIR}/opencode.jsonc" ]]; then
    echo "  ${YELLOW}skip${NC} opencode.jsonc (existe deja, merge manuel recommande)"
    echo "  Template disponible : ${KIT_DIR}/config/opencode.jsonc"
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
echo "  ${GREEN}ok${NC} scripts rendus executables"

# ─── Done ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}✓ Installation terminee !${NC}"
echo ""
echo "Notes :"
echo "  • Edite ${OPENDIR}/opencode.jsonc pour configurer tes providers IA"
echo "  • Importe ton Knowledge Graph : ./scripts/import-kg.sh <fichier_export>"
echo "  • Les archives de session (L3) sont stockees dans ${OPENDIR}/memory/sessions/"
echo "  • Pour mettre a jour : git pull dans ${KIT_DIR}"

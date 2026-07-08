#!/usr/bin/env bash
set -euo pipefail

# ─── opencode-kit: Knowledge Graph importer ─────────────────────────────────
# Usage: ./import-kg.sh <export_file.json>
#
# Importe un Knowledge Graph depuis un fichier JSON d'export.
# Le format attendu est celui produit par memory_read_graph.
# ──────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <export_file.json>"
    echo ""
    echo "Exporte d'abord ton KG depuis OpenCode :"
    echo "  1. Demande a ton agent : 'exporte le knowledge graph'"
    echo "  2. Sauvegarde la sortie dans un fichier .json"
    echo "  3. Lance ce script avec le fichier"
    exit 1
fi

INPUT="$1"

if [[ ! -f "$INPUT" ]]; then
    echo -e "${RED}✗ Fichier introuvable : ${INPUT}${NC}"
    exit 1
fi

# Validate JSON
if ! python3 -m json.tool "$INPUT" > /dev/null 2>&1; then
    echo -e "${RED}✗ JSON invalide${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Fichier d'export valide :${NC} $(basename "$INPUT")"
echo ""
echo "Pour importer ce Knowledge Graph dans OpenCode :"
echo "  1. Ouvre une session OpenCode"
echo "  2. Demande a l'agent : 'importe ce knowledge graph'"
echo "  3. Colle le contenu de $(basename "$INPUT")"
echo ""
echo "Contenu (preview) :"
echo "──────────────────────────────────────"
python3 -c "
import json, sys
with open('$INPUT') as f:
    data = json.load(f)
entities = data.get('entities', [])
relations = data.get('relations', [])
print(f'Entites : {len(entities)}')
print(f'Relations : {len(relations)}')
for e in entities[:5]:
    print(f'  • {e[\"name\"]} ({e[\"entityType\"]})')
if len(entities) > 5:
    print(f'  ... et {len(entities)-5} autres')
"

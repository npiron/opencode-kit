# opencode-kit

> Un kit clé en main pour transformer [OpenCode](https://github.com/anomalyco/opencode) en un agent IA puissant, avec mémoire persistante, skills spécialisés, et un heartbeat autonome.

**Ce kit inclut un système de mémoire à 3 couches (L1/L2/L3), des skills prêts à l'emploi, un mécanisme de consolidation automatique, et un heartbeat (Pouls) qui transforme l'agent en service autonome.**

---

## Installation

```bash
git clone https://github.com/npiron/opencode-kit.git
cd opencode-kit && ./install.sh
```

L'installateur crée des **symlinks** (pas de copies) vers `~/.config/opencode/`, ce qui permet de mettre à jour le kit avec un simple `git pull`.

### Prérequis

- [OpenCode](https://github.com/anomalyco/opencode) installé (`curl -fsSL https://opencode.ai/install.sh | sh`)
- Au moins un provider IA configuré (Claude, DeepSeek, Gemini, OpenAI, etc.)
- [Bun](https://bun.sh) (pour les plugins npm comme `opencode-tasks`)

---

## Heartbeat Pouls

**Pouls** est un agent de fond qui s'exécute toutes les heures via `opencode-tasks` :

1. **CHECK INBOX** — Lit les mails Gmail avec le label `AgentTrigger`
2. **PROCESS TASK** — Exécute les demandes (résumé PRs, recherche web, etc.)
3. **CONSOLIDATE** — Consolide la mémoire si nouvelles sessions
4. **JOURNAL** — Écrit un log + résumé quotidien dans un Google Doc

Le plugin `pouls-guard` bloque tout email non destiné à `piron.nicolas@gmail.com` et applique un rate limiting (max 3 réponses/battement, 10/jour).

**Setup Gmail requis :**
1. Créer le label `AgentTrigger`
2. Créer le label `AgentProcessed`
3. Créer un filtre : `subject:[AGENT]` → appliquer `AgentTrigger` + archiver

Voir [docs/CAHIER-DES-CHARGES.md](docs/CAHIER-DES-CHARGES.md) pour la spécification complète.

---

## Fonctionnalités clés

### 🧠 Mémoire sceptique
L'agent vérifie toujours le code réel avant d'agir, même s'il "se souvient" d'une information.

### 🔄 Consolidation automatique
- **microCompact** : après chaque session
- **fullCompact** : toutes les 3 sessions ou 6h

### 📦 Import/Export
- `scripts/import-kg.sh` : importe un Knowledge Graph depuis un export JSON

---

## Personnalisation

1. Édite `config/opencode.jsonc` pour configurer tes providers IA
2. Ajoute tes propres skills dans `skills/`
3. Modifie `agents/preferences.md` pour adapter le comportement de l'agent
4. Configure le heartbeat : édite `tasks/pouls-cycle.md` et `heartbeat/repos-whitelist.txt`

---

## Licence

MIT — voir [LICENSE](LICENSE)

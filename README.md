# opencode-kit

> Un kit clé en main pour transformer [OpenCode](https://github.com/charmbracelet/crush) en un agent IA puissant, avec mémoire persistante et skills spécialisés.

**Contrairement à un simple fichier de config, ce kit inclut un système de mémoire à 3 couches (L1/L2/L3) inspiré de l'architecture interne de Claude Code, des skills prêts à l'emploi, et un mécanisme de consolidation automatique.**

---

## Installation

```bash
git clone https://github.com/nicolaspiron/opencode-kit.git
cd opencode-kit && ./install.sh
```

L'installateur crée des **symlinks** (pas de copies) vers `~/.config/opencode/`, ce qui permet de mettre à jour le kit avec un simple `git pull`.

### Prérequis

- [OpenCode](https://github.com/charmbracelet/crush) installé
- Au moins un provider IA configuré (Claude, Gemini, OpenAI, etc.)

---

## Architecture

Le kit est structuré autour de **3 couches de mémoire** :

| Couche | Emplacement | Rôle |
|---|---|---|
| **L1** | `agents/preferences.md` | Règles comportementales intemporelles (~50 lignes). Toujours chargée. |
| **L2** | Knowledge Graph (runtime) | Faits structurés : projets, technos, contacts. Queryable via `memory_*`. |
| **L3** | `~/.config/opencode/memory/sessions/` | Archives datées des sessions. Historique complet. |

### Skills inclus

| Skill | Description |
|---|---|
| **memory-harness** | Consolidation mémoire en 4 phases (Orient → Gather → Consolidate → Prune) |
| **google-workspace** | Gmail, Google Docs, Drive, Calendar, Contacts |
| **git-conventions** | Workflows git, commits, PRs |
| **scraper** | Web scraping et extraction de données |
| **devstral-helper** | Optimisation pour modèles locaux (LM Studio / Mistral) |
| **rulebook** | Règles de code (Clean Code, Refactoring, Pragmatic Programmer) |

---

## Fonctionnalités clés

### 🧠 Mémoire sceptique
L'agent vérifie toujours le code réel avant d'agir, même s'il "se souvient" d'une information. La mémoire est un indice, pas une vérité.

### 🔄 Consolidation automatique
- **microCompact** : après chaque session, les décisions clés sont ajoutées au Knowledge Graph
- **fullCompact** : toutes les 3 sessions ou 6h, une consolidation complète fusionne, nettoie et indexe la mémoire

### 🔒 ConsolidationLock
Un fichier `.consolidate-lock` empêche les écritures concurrentes lors de la consolidation.

### 📦 Import/Export
- `scripts/import-kg.sh` : importe un Knowledge Graph depuis un export JSON
- Le KG n'est **pas inclus** dans le repo (données personnelles)

---

## Personnalisation

1. Édite `config/opencode.jsonc` pour configurer tes providers IA
2. Ajoute tes propres skills dans `skills/`
3. Modifie `agents/preferences.md` pour adapter le comportement de l'agent
4. Importe ton KG existant : `./scripts/import-kg.sh backup.json`

---

## Mise à jour

```bash
cd /chemin/vers/opencode-kit
git pull
```

Les symlinks pointent vers le repo, donc les mises à jour sont immédiates.

---

## Licence

MIT — voir [LICENSE](LICENSE)

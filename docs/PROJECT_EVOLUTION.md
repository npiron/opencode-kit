# Opencode Kit — Plan d'évolution

> **Public cible : agents IA (OpenCode, Claude Code, Codex, etc.)**
> Ce document est rédigé pour être lu et exécuté par un agent de manière autonome.
> Chaque section est une action concrète, avec l'état attendu en sortie.

---

## Principes fondateurs

Avant toute modification, tu dois respecter ces principes. Aucune évolution ne doit les violer.

| Principe | Règle |
|----------|-------|
| **Simplicité** | Le projet doit rester compréhensible en 10 minutes |
| **Zéro dépendance inutile** | Pas de framework, pas de base de données, pas d'ORM |
| **Orienté fichiers** | La config = des fichiers JSON/Markdown, rien d'autre |
| **Compatible OpenCode** | Doit fonctionner avec `opencode run --agent` |
| **Forkable** | Un `git clone && ./install.sh` doit suffire |
| **Symlinks** | Jamais de copie de fichiers. Tout passe par des liens symboliques |

---

## Axe 1 — Diagramme d'architecture

### Action

Ajouter un diagramme Mermaid dans le README.md, juste après l'introduction, avant la section "Installation".

### Emplacement

Dans `/README.md`, après le bloc de description (lignes 1-3), ajouter :

```markdown
## Architecture

\`\`\`mermaid
graph TB
    User[👤 Utilisateur]

    subgraph OpenCode["OpenCode Runtime"]
        Agent[🤖 Agent IA]
        Skills[🎯 Skills]
        Plugins[🔌 Plugins]
        Memory[🧠 Mémoire]
        Heartbeat[💓 Pouls]
        Config[⚙️ Config]
    end

    subgraph Kit["opencode-kit"]
        SkillsKit[skills/]
        PluginsKit[plugins/]
        AgentsKit[agents/]
        ConfigKit[config/]
        TasksKit[tasks/]
    end

    subgraph Workspace["Workspace"]
        L1[Working Memory]
        L2[Session Memory — Knowledge Graph]
        L3[Knowledge Base — Archives]
    end

    User --> OpenCode
    Kit -->|symlinks| OpenCode
    Agent --> Skills
    Agent --> Plugins
    Agent --> Memory
    Plugins -->|pouls-guard| Heartbeat
    Memory --> Workspace
\`\`\`
```

---

## Axe 2 — Noms explicites pour la mémoire

### Problème

Les noms L1, L2, L3 sont opaques pour un nouveau contributeur.

### Action

Renommer conceptuellement les niveaux de mémoire dans toute la documentation et le code.

| Ancien nom | Nouveau nom | Description |
|-----------|-------------|-------------|
| L1 | **Working Memory** | Règles comportementales intemporelles. Chargée à chaque session. |
| L2 | **Session Memory** | Graphe de connaissances structuré (faits, projets, contacts). |
| L3 | **Knowledge Base** | Archives historiques des sessions passées. |

### Fichiers à mettre à jour

1. `/README.md` — remplacer "mémoire à 3 couches (L1/L2/L3)" par "mémoire à 3 couches (Working / Session / Knowledge Base)"
2. `/agents/preferences.md` — remplacer les références L1/L2/L3 par les nouveaux noms
3. `/docs/CAHIER-DES-CHARGES.md` — idem

---

## Axe 3 — Configuration externalisée

### Problème

Les constantes métier sont codées en dur dans `plugins/pouls-guard/index.ts`.

### Action

Créer des fichiers de configuration JSON et faire lire ces fichiers par le plugin au lieu d'utiliser des constantes.

### Étape 3.1 — Créer le fichier de config guard

Créer `/config/guard.json` :

```json
{
  "email": {
    "allowed_recipient": "piron.nicolas@gmail.com",
    "max_per_beat": 3,
    "max_per_day": 10
  },
  "destructive_patterns": {
    "tool_names": ["delete", "rm", "drop", "trash"],
    "shell_commands": ["rm -rf", "git clean", "git reset --hard", "truncate", "sudo", "chmod 777", "mv /* /dev/null"],
    "git_commands": ["push --force", "hard reset", "clean -fd"]
  },
  "rate_limiting": {
    "max_emails_per_beat": 3,
    "max_emails_per_day": 10,
    "max_mails_processed_per_beat": 10
  }
}
```

### Étape 3.2 — Créer le fichier de config heartbeat

Créer `/config/heartbeat.json` :

```json
{
  "schedule": "0 * * * *",
  "dead_mans_switch": {
    "max_delay_minutes": 150,
    "alert_recipient": "piron.nicolas@gmail.com"
  },
  "gmail": {
    "trigger_label": "AgentTrigger",
    "processed_label": "AgentProcessed"
  }
}
```

### Étape 3.3 — Créer le fichier de config memory

Créer `/config/memory.json` :

```json
{
  "levels": {
    "working": {
      "path": "agents/preferences.md",
      "max_lines": 60,
      "description": "Timeless behavioral rules"
    },
    "session": {
      "path": "memory/knowledge-graph/",
      "description": "Structured knowledge graph"
    },
    "knowledge_base": {
      "path": "memory/sessions/",
      "retention_days": 90,
      "description": "Session archives"
    }
  },
  "consolidation": {
    "micro_compact_trigger": "every_session",
    "full_compact_trigger": "every_3_sessions_or_6_hours"
  }
}
```

### Étape 3.4 — Modifier le plugin pouls-guard

Dans `/plugins/pouls-guard/index.ts` :

1. Supprimer les constantes `ALLOWED_EMAIL`, `MAX_EMAILS_PER_BEAT`, `MAX_EMAILS_PER_DAY`, `DESTRUCTIVE_PATTERNS`
2. Ajouter une fonction `readGuardConfig()` qui lit `/config/guard.json` (chercher dans le répertoire du kit, pas dans `~/.config/opencode/`)
3. Remplacer toutes les références aux constantes par des lectures depuis `readGuardConfig()`
4. Étendre `isDestructive()` pour analyser aussi les arguments des commandes shell, pas seulement le nom du tool
5. Ajouter une détection pour `sudo`, `chmod`, `truncate`, `git push --force`, etc.

### Structure attendue après modification

```
config/
├── opencode.jsonc
├── guard.json          ← nouveau
├── heartbeat.json      ← nouveau
└── memory.json         ← nouveau
```

---

## Axe 4 — Restructuration des plugins

### Problème

Un seul dossier `plugins/pouls-guard/`. Si 10 plugins arrivent, c'est ingérable.

### Action

Renommer et préparer l'arborescence pour plusieurs plugins indépendants.

### Structure cible

```
plugins/
├── guard/              ← anciennement pouls-guard
│   ├── index.ts
│   └── config.example.json
├── heartbeat/
│   └── (futur plugin heartbeat)
├── gmail/
│   └── (futur plugin Gmail)
├── memory/
│   └── (futur plugin mémoire)
└── workspace/
    └── (futur plugin workspace)
```

### Étape 4.1 — Renommer le plugin

1. Renommer `plugins/pouls-guard/` → `plugins/guard/`
2. Mettre à jour le `name` dans `index.ts` : `"pouls-guard"` → `"guard"`
3. Mettre à jour la référence dans `install.sh` (aucun changement nécessaire car le script itère sur tous les dossiers de `plugins/`)

### Étape 4.2 — Ajouter un template de plugin

Créer `/plugins/_template/` :

```
plugins/_template/
├── index.ts             ← template vide
├── config.example.json  ← config minimale
└── README.md            ← explications pour créer un plugin
```

Contenu de `README.md` :

```markdown
# Plugin Template

Pour créer un nouveau plugin :

1. Copier ce dossier : `cp -r plugins/_template plugins/mon-plugin`
2. Renommer le plugin dans `index.ts` (propriété `name`)
3. Implémenter les hooks nécessaires
4. Ajouter la config dans `config/mon-plugin.json`
5. Le plugin sera automatiquement linké par `install.sh`
```

---

## Axe 5 — Découpage de l'installateur

### Problème

`install.sh` fait 150 lignes. Difficile à maintenir, impossible à tester unitairement.

### Action

Découper en modules indépendants.

### Structure cible

```
install/
├── check.sh             ← vérification des prérequis (opencode, bun, git)
├── brew.sh              ← installation des dépendances système
├── links.sh             ← création des symlinks (agents, skills, plugins, tasks)
├── config.sh            ← copie des fichiers de configuration
├── providers.sh         ← configuration des providers IA
└── scheduler.sh         ← installation du daemon opencode-tasks
```

`install.sh` devient un simple orchestrateur :

```bash
#!/usr/bin/env bash
set -euo pipefail

KIT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "${KIT_DIR}/install/check.sh"
source "${KIT_DIR}/install/links.sh"
source "${KIT_DIR}/install/config.sh"
source "${KIT_DIR}/install/scheduler.sh"

echo "✓ Installation terminée."
```

### Étape 5.1 — check.sh

Contenu : vérification de `opencode`, `bun`, `git`, `python3`. Affiche des warnings sans bloquer.

### Étape 5.2 — links.sh

Contenu : boucles de création de symlinks pour agents, skills, tasks, plugins, heartbeat, scripts. C'est le cœur actuel de `install.sh`.

### Étape 5.3 — config.sh

Contenu : copie de `opencode.jsonc` si absent, copie de `.env.example` → `.env`, création des dossiers nécessaires.

### Étape 5.4 — scheduler.sh

Contenu : `bunx opencode-tasks --install`.

---

## Axe 6 — Documentation

### Action

Créer les documents suivants.

### Étape 6.1 — ROADMAP.md

Créer `/ROADMAP.md` :

```markdown
# Roadmap

## v0.1 — Fondations ✅
- [x] Architecture mémoire L1/L2/L3
- [x] Skills (git-conventions, scraper, google-workspace, etc.)
- [x] Plugin pouls-guard (sécurité email + rate limiting)
- [x] Installateur par symlinks
- [x] Heartbeat Pouls (spécification)

## v0.2 — Robustesse (en cours)
- [ ] Configuration externalisée (guard.json, heartbeat.json, memory.json)
- [ ] Découpage de l'installateur en modules
- [ ] Renommage mémoire (Working / Session / Knowledge Base)
- [ ] Diagrammes Mermaid dans la documentation
- [ ] Tests unitaires sur le plugin guard

## v0.3 — Maturité Open Source
- [ ] ARCHITECTURE.md avec diagrammes
- [ ] DECISIONS.md (ADR — pourquoi les symlinks, pourquoi pas de DB, etc.)
- [ ] CONTRIBUTING.md
- [ ] CI GitHub Actions (lint, tests, validation markdown)
- [ ] CHANGELOG.md auto-généré
- [ ] Semantic versioning + GitHub Releases

## v1.0 — Distribution
- [ ] Site de documentation (VitePress)
- [ ] Marketplace de skills
- [ ] Versioning des skills
- [ ] Plugins découplés avec config standardisée
- [ ] Tests d'intégration
```

### Étape 6.2 — ARCHITECTURE.md

Créer `/docs/ARCHITECTURE.md` avec :

- Diagramme Mermaid global (composants + flux)
- Description de chaque dossier
- Flux de démarrage (install → opencode → agent → skills → plugins → memory)
- Flux heartbeat (cron → opencode-tasks → opencode run → guard → agent → gmail → memory)

### Étape 6.3 — DECISIONS.md

Créer `/docs/DECISIONS.md` (Architecture Decision Records) :

```markdown
# Architecture Decision Records

## ADR-001 : Symlinks plutôt que copie de fichiers
**Date :** 2026-07-08
**Statut :** Accepté

**Contexte :** Comment distribuer les fichiers du kit vers `~/.config/opencode/` ?

**Décision :** Utiliser des symlinks plutôt que de copier les fichiers.

**Conséquences :**
- Un `git pull` met à jour toute l'installation
- Pas de désynchronisation entre le repo et la config locale
- Impossible sur Windows sans WSL

## ADR-002 : Configuration orientée fichiers plutôt que base de données
**Date :** 2026-07-08
**Statut :** Accepté

**Contexte :** Comment stocker la configuration et la mémoire ?

**Décision :** Fichiers JSON et Markdown, pas de base de données.

**Conséquences :**
- Zéro dépendance
- Versionnable avec git
- Limité en volumétrie (acceptable pour un usage personnel)

## ADR-003 : Plugin guard au niveau runtime plutôt que prompt
**Date :** 2026-07-08
**Statut :** Accepté

**Contexte :** Comment empêcher l'agent d'envoyer des emails à la mauvaise personne ?

**Décision :** Double couche — prompt (guidage) + plugin hook `tool.execute.before` (blocage).

**Conséquences :**
- Le prompt peut être contourné, le hook non
- Le hook est exécuté avant chaque appel d'outil
- Overhead minimal
```

### Étape 6.4 — CONTRIBUTING.md

Créer `/CONTRIBUTING.md` avec :

- Structure du projet
- Convention de nommage
- Comment créer un skill
- Comment créer un plugin
- Comment tester
- Process de Pull Request

### Étape 6.5 — Documents complémentaires

Créer (même vides, avec un titre et une phrase) :

- `/docs/PLUGINS.md` — "Comment créer et configurer un plugin"
- `/docs/MEMORY.md` — "Fonctionnement de la mémoire à 3 niveaux"
- `/docs/SKILLS.md` — "Liste et description des skills disponibles"
- `/docs/CONFIGURATION.md` — "Guide de configuration complet"
- `/docs/FAQ.md` — "Questions fréquentes"
- `/LICENSE` — déjà présent, vérifier que c'est MIT

---

## Axe 7 — Amélioration du plugin Guard

### Problème

La détection des opérations destructives est trop naïve (match sur le nom du tool uniquement).

### Action

Modifier `plugins/guard/index.ts` pour analyser :

1. Le nom du tool (comportement actuel)
2. Les arguments de la commande shell (détecter `rm -rf`, `sudo`, etc.)
3. Les commandes Git dangereuses (`push --force`, `reset --hard`, `clean -fd`)

### Implémentation

```typescript
function isDestructive(toolName: string, args?: Record<string, unknown>): boolean {
  const config = readGuardConfig()
  const lower = toolName.toLowerCase()

  // Vérifier le nom du tool
  if (config.destructive_patterns.tool_names.some(p => lower.includes(p))) {
    return true
  }

  // Vérifier les commandes shell
  if (toolName === "bash" || toolName === "execute_command") {
    const command = (args?.command as string) || ""
    const cmdLower = command.toLowerCase()
    if (config.destructive_patterns.shell_commands.some(p => cmdLower.includes(p))) {
      return true
    }
  }

  // Vérifier les commandes Git dangereuses
  if (toolName.startsWith("git")) {
    const command = (args?.command as string) || ""
    if (config.destructive_patterns.git_commands.some(p => command.includes(p))) {
      return true
    }
  }

  return false
}
```

---

## Axe 8 — Tests

### Action

Mettre en place une structure de tests.

### Structure cible

```
tests/
├── guard/
│   └── index.test.ts       ← tests unitaires du plugin guard
├── install/
│   └── links.test.sh       ← tests du script de symlinks
└── fixtures/
    ├── guard-config.json   ← config de test
    └── rate-limits.json    ← état de test
```

### Étape 8.1 — Tests du plugin guard

Écrire des tests pour :

- Blocage d'email vers un destinataire non autorisé
- Autorisation d'email vers le destinataire autorisé
- Blocage quand le rate limit est atteint (par battement)
- Blocage quand le rate limit est atteint (par jour)
- Blocage des commandes destructives (`delete`, `rm`, `drop`, `trash`)
- Blocage de `git push --force`
- Blocage de `sudo`
- Blocage de `rm -rf`
- Autorisation de `git status`
- Autorisation de `ls`

Utiliser `bun test` (le projet utilise déjà Bun).

---

## Axe 9 — CI GitHub Actions

### Action

Créer `.github/workflows/ci.yml`.

### Contenu

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun test

  markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v15
```

---

## Axe 10 — Fichiers Open Source

### Action

Créer les fichiers standards d'un projet open source mature.

### Liste

1. `/CODE_OF_CONDUCT.md` — utiliser le template Contributor Covenant
2. `/SECURITY.md` — expliquer comment signaler une vulnérabilité
3. `/SUPPORT.md` — expliquer où poser des questions (GitHub Issues)
4. `/.github/ISSUE_TEMPLATE/bug_report.md` — template de bug
5. `/.github/ISSUE_TEMPLATE/feature_request.md` — template de feature
6. `/.github/PULL_REQUEST_TEMPLATE.md` — checklist PR

---

## Axe 11 — Site de documentation (VitePress)

### Quand

Phase v1.0 — ne pas faire maintenant, mais préparer la structure.

### Action

Créer un fichier `/docs/.vitepress/config.ts` minimal pour anticiper.

```typescript
export default {
  title: "Opencode Kit",
  description: "Kit clé en main pour transformer OpenCode en agent IA autonome",
  themeConfig: {
    nav: [
      { text: "Guide", link: "/guide/" },
      { text: "Plugins", link: "/plugins/" },
      { text: "API", link: "/api/" }
    ],
    sidebar: {
      "/guide/": [
        { text: "Installation", link: "/guide/installation" },
        { text: "Configuration", link: "/guide/configuration" },
        { text: "Skills", link: "/guide/skills" },
        { text: "Mémoire", link: "/guide/memory" }
      ]
    }
  }
}
```

---

## Axe 12 — Changelog automatique

### Action

Configurer la génération automatique du changelog basé sur les conventions de commit.

### Étape 12.1

Créer `/CHANGELOG.md` avec un placeholder.

### Étape 12.2

Ajouter un script `scripts/changelog.sh` qui génère le changelog à partir de `git log`.

Ou utiliser un outil comme `git-cliff` si une dépendance est acceptable.

---

## Résumé des fichiers à créer

Voici la liste exhaustive de tous les fichiers à créer ou modifier, dans l'ordre recommandé :

| Priorité | Fichier | Action |
|----------|---------|--------|
| 🔴 P0 | `/docs/ARCHITECTURE.md` | Créer |
| 🔴 P0 | `/README.md` | Ajouter diagramme Mermaid |
| 🔴 P0 | `/config/guard.json` | Créer |
| 🔴 P0 | `/config/heartbeat.json` | Créer |
| 🔴 P0 | `/config/memory.json` | Créer |
| 🔴 P0 | `/plugins/guard/index.ts` | Modifier (externaliser config) |
| 🟡 P1 | `/ROADMAP.md` | Créer |
| 🟡 P1 | `/docs/DECISIONS.md` | Créer |
| 🟡 P1 | `/install/check.sh` | Créer (extraire de install.sh) |
| 🟡 P1 | `/install/links.sh` | Créer (extraire de install.sh) |
| 🟡 P1 | `/install/config.sh` | Créer (extraire de install.sh) |
| 🟡 P1 | `/install/scheduler.sh` | Créer (extraire de install.sh) |
| 🟡 P1 | `/install.sh` | Simplifier (orchestrateur) |
| 🟡 P1 | `/agents/preferences.md` | Renommer L1/L2/L3 |
| 🟢 P2 | `/docs/PLUGINS.md` | Créer |
| 🟢 P2 | `/docs/MEMORY.md` | Créer |
| 🟢 P2 | `/docs/SKILLS.md` | Créer |
| 🟢 P2 | `/docs/CONFIGURATION.md` | Créer |
| 🟢 P2 | `/docs/FAQ.md` | Créer |
| 🟢 P2 | `/CONTRIBUTING.md` | Créer |
| 🟢 P2 | `/plugins/_template/` | Créer template |
| 🟢 P2 | `/tests/guard/index.test.ts` | Créer |
| 🔵 P3 | `/.github/workflows/ci.yml` | Créer |
| 🔵 P3 | `/CODE_OF_CONDUCT.md` | Créer |
| 🔵 P3 | `/SECURITY.md` | Créer |
| 🔵 P3 | `/SUPPORT.md` | Créer |
| 🔵 P3 | `/.github/ISSUE_TEMPLATE/` | Créer |
| 🔵 P3 | `/.github/PULL_REQUEST_TEMPLATE.md` | Créer |
| 🔵 P3 | `/CHANGELOG.md` | Créer |
| ⚪ P4 | `/docs/.vitepress/config.ts` | Créer (placeholder) |

---

## Vérifications finales

Avant de considérer le travail comme terminé, vérifier :

- [ ] `./install.sh` fonctionne sans erreur
- [ ] Tous les symlinks pointent vers les bons fichiers
- [ ] Le plugin guard lit bien `config/guard.json`
- [ ] Les tests passent : `bun test`
- [ ] Le README s'affiche correctement sur GitHub (diagramme Mermaid rendu)
- [ ] Aucune constante métier ne reste dans le code
- [ ] Tous les nouveaux fichiers sont versionnés dans git

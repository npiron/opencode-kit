# Cahier des charges — Heartbeat pour Pouls

| Rédacteur | Date | Version |
|-----------|------|---------|
| Nicolas Piron | 2026-07-08 | 1.2 — refonte architecture (plugin-based, opencode-tasks, nom Pouls) |

---

## 0. Prérequis techniques

### 0.1 Runtime headless d'opencode ✅ RÉSOLU

**Solution :** `opencode run` est le mode batch natif.

```bash
opencode run --agent heartbeat --auto --dir "$HOME"
```

| Flag | Utilité |
|------|---------|
| `--auto` | Auto-approve les permissions → pas d'interaction humaine |
| `--agent` | Utilise l'agent `heartbeat` dédié |
| `--dir` | Répertoire de travail |

### 0.2 Setup Gmail requis

1. **Label Gmail `AgentTrigger`** — pour isoler les mails heartbeat
2. **Filtre Gmail** : `subject:[AGENT]` → appliquer `AgentTrigger` + archiver

### 0.3 Fichiers d'état

`~/.config/opencode/heartbeat/` contient :
- `heartbeat.log` — journal des battements
- `heartbeat.last` — dead man's switch
- `consolidation.lock` — timestamp du dernier microCompact
- `rate-limits.json` — compteurs de rate limiting

---

## 1. Présentation du projet

**Pouls** est un agent IA personnel sur l'écosystème `opencode` avec mémoire L1/L2/L3, skills spécialisés, et capacité de raisonnement cross-session.

L'objectif du projet **Heartbeat** : transformer l'agent interactif en **service autonome** qui s'exécute toutes les heures.

> **"Pouls n'est plus un outil que tu lances quand tu as besoin. Il est toujours là, en veille, prêt à réagir."**

---

## 2. Objectifs

| # | Objectif | Critère de succès |
|---|----------|-------------------|
| 1 | Traiter les mails `[AGENT]` | Mail marqué lu/traité ; réponse threadée avec le résultat (sauf `[NOREPLY]`) |
| 2 | Consolider la mémoire (microCompact) | Timestamp mis à jour dans `consolidation.lock` |
| 3 | Maintenir un journal | `heartbeat.log` + Google Doc quotidien |

---

## 3. Cycle Heartbeat

```
Toutes les heures (opencode-tasks daemon) :
  ├── 1. CHECK INBOX   → Mails label:AgentTrigger non lus ?
  ├── 2. PROCESS TASK  → Exécuter, répondre avec le résultat (sauf [NOREPLY])
  ├── 3. CONSOLIDATE   → microCompact si nouvelles sessions L3
  ├── 4. JOURNAL       → heartbeat.log + Google Doc + heartbeat.last
  └── 5. SLEEP         → Exit. Le daemon relancera.
```

---

## 4. Architecture technique

```
┌─────────────────────────────────────────────────────┐
│         opencode-tasks daemon (launchd)              │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│     opencode run --agent heartbeat --auto --dir ~    │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Plugin "pouls-guard" (tool.execute.before)   │   │
│  │  ├── Bloque email si to ≠ nicolas@...        │   │
│  │  ├── Bloque opérations destructives           │   │
│  │  └── Rate limiting (3/battement, 10/jour)    │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Agent "heartbeat" (skill heartbeat/SKILL.md) │   │
│  │  CHECK → ACT → SYNC → LOG                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  MCP Google Workspace (Gmail + Drive)                │
│  Mémoire L2/L3 (knowledge graph + sessions)          │
└─────────────────────────────────────────────────────┘
```

### Composants

| Composant | Rôle |
|-----------|------|
| opencode-tasks (npm) | Daemon launchd + exécution cron |
| tasks/pouls-cycle.md | Tâche cron horaire |
| agents/heartbeat.md | Config agent (modèle, permissions) |
| skills/heartbeat/SKILL.md | Prompt système |
| plugins/pouls-guard/ | Hook sécurité + rate limiting |
| skills/memory-harness/ | Consolidation L2/L3 |
| MCP Google Workspace | Gmail + Drive |

---

## 5. Sécurité

### 5.1 Règle email (NON-NÉGOCIABLE)

> **Tu as le droit d'envoyer des emails UNIQUEMENT à : `piron.nicolas@gmail.com`**

Double couche : prompt (guidage) + plugin pouls-guard (blocage runtime).

### 5.2 Rate limiting

| Ressource | Limite |
|-----------|--------|
| Emails envoyés | Max 3/battement |
| Emails envoyés | Max 10/jour glissant |
| Mails traités | Max 10/battement |

### 5.3 Dead man's switch

`heartbeat.last` mis à jour à chaque battement. Si > 2h30 → alerte.

---

## 6. Phases d'implémentation

### Phase 0 — Prérequis (✅)
- [x] opencode + MCP Google Workspace
- [x] Skills memory-harness, scraper, git-conventions
- [x] Architecture mémoire L1/L2/L3

### Phase 0.5 — Validation technique
- [x] Runtime headless : `opencode run` validé
- [ ] opencode-tasks + daemon launchd
- [ ] Setup Gmail (labels + filtre)
- [ ] Créer dossier Drive `Pouls/Heartbeat/`

### Phase 1 — MVP (7 jours)
- [ ] tasks/pouls-cycle.md
- [ ] agents/heartbeat.md
- [ ] skills/heartbeat/SKILL.md
- [ ] plugins/pouls-guard/index.ts
- [ ] 7 jours de test

### Phase 2 — Consolidation + Journal Drive
- [ ] microCompact automatique
- [ ] Google Doc quotidien
- [ ] heartbeat-healthcheck.sh

### Phase 3 — Roadmap future
- [ ] Tâches planifiées
- [ ] Widget macOS SwiftBar/xbar
- [ ] Notifications Telegram/Slack
- [ ] Modèle cheap dédié
- [ ] opencode-evolve (heartbeat natif V2)

---

## 7. Critères de succès

| Métrique | Cible |
|----------|-------|
| Fiabilité | 0 crash / 168 battements |
| Traitement mails | 100% traités |
| Rate limit | 3/battement, 10/jour |
| Double battement | 0 |
| Coût/battement | < 0,05 $ |
| Portabilité | Install < 10 min |

---

## 8. Annexes

### Stack technique

| Composant | Technologie |
|-----------|-------------|
| Runtime | opencode (Node.js, Bun) |
| Scheduler | opencode-tasks → launchd |
| Modèle V1 | deepseek-v4-pro |
| Email | Gmail via MCP |
| Sécurité | Plugin pouls-guard (hook runtime) |
| Portabilité | Repo git opencode-kit |

### Portabilité

```bash
git clone https://github.com/npiron/opencode-kit.git
cd opencode-kit && ./install.sh
# → remplir .env
# → créer labels Gmail (2 clics)
# → c'est tout
```

### Pourquoi "Pouls" ?

Le nom `Crush` entrait en collision avec [Charmbracelet Crush](https://github.com/charmbracelet/crush). Renommé **Pouls** — le battement, le rythme, la vie.

---

> **Document rédigé le 8 juillet 2026 par Nicolas Piron. Projet "Heartbeat pour Pouls". v1.2.**

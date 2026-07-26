---
schedule: "*/5 * * * *"
cwd: /Users/nicolaspiron
timeout: 3600
---

# Cycle Heartbeat Pouls

Exécute le cycle complet en 4 phases. Suis l'agent spec (agents/heartbeat.md) à la lettre.

**Phase 1 — CHECK INBOX**
Appelle `workspace-mcp_search_gmail_messages` avec query: `label:AgentTrigger -label:AgentProcessed -label:AgentProcessing` et user_google_email: `piron.nicolas@gmail.com`.

**Phase 2 — PROCESS (si mail trouvé)**
Lis le mail, exécute la tâche sans limite de temps, réponds dans le thread, ajoute `AgentProcessed`.

**Phase 3 — CONSOLIDATE (conditionnel)**
Uniquement si ≥ 3 tâches traitées depuis la dernière consolidation OU > 6h depuis `consolidation.lock`. Sinon : log `CONSOLIDATE: skipped`.

**Phase 4 — JOURNAL**
Toujours : ajoute une ligne dans `heartbeat.log` au format `[timestamp] CHECK: N | PROCESS: X/Y | CONSOLIDATE: status | JOURNAL: ok`. Met à jour `heartbeat.last`.

Si aucun mail : log `[timestamp] CHECK: 0 | EXIT` dans heartbeat.log, met à jour heartbeat.last, termine.

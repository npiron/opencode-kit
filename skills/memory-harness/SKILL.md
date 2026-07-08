# Memory Harness — Consolidation memoire 4 phases

Skill de consolidation memoire inspire de l'architecture KAIROS/autoDream de Claude Code.
Implemente un systeme de memoire a 3 couches (L1/L2/L3) avec consolidation asynchrone
et lock anti-concurrence.

## Architecture

```
L1 (preferences.md)     ← Règles intemporelles, toujours chargees
L2 (Knowledge Graph)     ← Faits structures, queryable
L3 (archives sessions)   ← Historique daté, jamais relu en entier

.consolidate-lock        ← Mutex fichier (timestamp lastConsolidatedAt)
```

## Seuils de consolidation

| Paramètre | Valeur | Description |
|---|---|---|
| `minSessions` | 3 | Nombre minimum de sessions avant fullCompact |
| `minHours` | 6 | Temps minimum ecoule avant fullCompact |
| `maxL1Lines` | 60 | L1 nettoye si depasse cette limite |

Ces seuils sont configurables dans le contexte du skill.

## Niveaux de compaction

### microCompact (chaque fin de session)

Action rapide, declenchee automatiquement :
1. Ajouter les decisions cles et nouvelles infos dans le L2 (Knowledge Graph)
2. Creer un fichier d'archive L3 : `memory/sessions/YYYY-MM-DD.md`
3. Si une preference explicite est exprimee : l'ajouter dans L1 ET L2

### fullCompact (toutes les `minSessions` sessions ou `minHours` ecoulees)

Consolidation complete en 4 phases :

---

## Prompt de consolidation 4 phases

Quand les conditions de fullCompact sont reunies, executer ce workflow :

### Phase 1 — ORIENT

Objectif : Comprendre l'etat actuel de la memoire avant de la modifier.

```
1. Lire L1 (agents/preferences.md) pour comprendre les regles en vigueur
2. Ouvrir le Knowledge Graph (memory_open_nodes) sur les entites principales
3. Lister les archives L3 existantes (memory/sessions/)
4. Verifier le .consolidate-lock pour connaitre lastConsolidatedAt
```

### Phase 2 — GATHER

Objectif : Collecter tous les nouveaux signaux depuis la derniere consolidation.

```
1. Scanner les archives L3 creees depuis lastConsolidatedAt
2. Identifier dans chaque archive :
   - Decisions cles prises
   - Nouvelles entites/projets/technos mentionnes
   - Preferences ou regles exprimees par l'utilisateur
   - Lecons apprises (erreurs, corrections)
   - Patterns recurrents
3. Lister les entites du L2 qui n'ont pas ete mises a jour depuis >30 jours
```

### Phase 3 — CONSOLIDATE

Objectif : Fusionner les nouveaux signaux dans la memoire persistante.

```
POUR CHAQUE entite concernee :
  1. memory_open_nodes sur l'entite existante
  2. memory_add_observations pour ajouter les nouvelles infos
  3. Si l'entite n'existe pas : memory_create_entities

POUR CHAQUE relation identifiee :
  1. memory_create_relations

FUSIONNER les doublons :
  - Deux entites avec des noms similaires → merger les observations
  - Deux observations identiques → supprimer le doublon via memory_delete_observations

METTRE A JOUR le perime :
  - Supprimer les observations obsolete (memory_delete_observations)
  - Mettre a jour les entites dont le statut a change
```

### Phase 4 — PRUNE & INDEX

Objectif : Nettoyer et finaliser.

```
1. NETTOYER L1 :
   - Si preferences.md > maxL1Lines (60 lignes) :
     - Identifier les regles devenues obsoletes
     - Supprimer ou condenser
     - Cible : ~50 lignes

2. METTRE A JOUR LE LOCK :
   - Ecrire le timestamp actuel dans memory/.consolidate-lock
   - Format : date ISO 8601

3. CREER L'ARCHIVE DE CONSOLIDATION :
   - Fichier : memory/sessions/YYYY-MM-DD-consolidation.md
   - Contenu : resume des changements effectues

4. VERIFIER :
   - memory_read_graph pour confirmer l'etat final
   - S'assurer qu'aucune donnee n'a ete perdue
```

---

## ConsolidationLock

### Format du fichier

```
/Users/$USER/.config/opencode/memory/.consolidate-lock
```

Contient une seule ligne : le timestamp ISO 8601 de la derniere consolidation.

```
2026-07-08T14:30:00Z
```

### Regles d'acquisition

1. **Avant de consolider** : verifier que le lock n'est pas deja detenu
2. **Lock stale** : si le timestamp est >1h, le lock est considere comme perime
3. **Apres consolidation** : mettre a jour le timestamp
4. **En cas d'echec** : ne pas modifier le lock (rollback implicite)

---

## Regle de "memoire sceptique"

> La memoire est un indice, pas une verite. Toujours verifier le code reel avant d'agir.

En pratique :
- Avant d'explorer un projet connu : `memory_open_nodes` sur l'entite **puis** explorer le code
- Si la memoire contredit le code : le code a raison, mettre a jour la memoire
- Les transcripts L3 ne sont jamais relus en entier, seulement fouilles par mots-cles
- L'agent traite sa propre memoire comme un "hint" — il doit verifier

---

## Maintenance periodique

Toutes les 10 sessions ou 30 jours (au premier atteint) :
1. Lister toutes les entites du L2
2. Identifier les entites non touchees depuis >30 jours
3. Proposer a l'utilisateur de les archiver ou supprimer
4. Verifier la coherence des relations (orphelins, circularites)

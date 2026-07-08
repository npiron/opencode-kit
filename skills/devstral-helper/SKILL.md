---
name: devstral-helper
description: Use when working with the local Devstral Small model (LM Studio / Mistral). Optimize prompts, manage context window limits, and adapt instructions for small local models. Trigger with keywords: devstral, lm studio, local model, prompt, token, context.
---

# Devstral Small Helper

Optimisations pour `mistralai/devstral-small-2-2512` via LM Studio.

## Limites du modèle

| Paramètre | Valeur |
|-----------|--------|
| Contexte max | 32 768 tokens |
| Output max | 4 096 tokens |
| Provider | LM Studio (local) |

## Optimisation des prompts

- **Concis** : instructions courtes, pas de verbosité inutile
- **Structure** : utiliser listes, tableaux, formats clairs
- **Priorité** : mettre l'info critique au début (primacy effect)
- **Itération** : pour les tâches complexes, décomposer en étapes et utiliser Sequential Thinking
- **Exemples** : inclure des exemples concrets quand pertinent

## Gestion du contexte

- Garder 10-15k tokens de marge pour l'historique de conversation
- Les fichiers lus comptent dans le contexte : limiter la taille des lectures
- Éviter de lire des fichiers entiers >2000 lignes
- Préférer `grep` et recherches ciblées aux lectures massives

## Stratégies

- Pour les gros fichiers : lire par portions (offset/limit)
- Pour les recherches : utiliser `grep` + `glob` avant de lire
- Pour les modifications : cibler des `edit` précis plutôt que des `write` complets
- Déléguer les sous-tâches à des agents spécialisés (`explore`, `general`)

## À éviter

- Instructions redondantes ou trop longues
- Lectures de fichiers massives sans offset
- Prompts qui gaspillent le contexte sur du boilerplate
- Trop d'outils en parallèle si le contexte est déjà chargé

# Contributing

## Structure du projet

```
agents/          — prompts système des agents (heartbeat.md, preferences.md)
config/          — configuration JSON externalisée
dashboard/       — TUI de monitoring (Python/Textual)
docs/            — documentation et plan d'évolution
heartbeat/       — whitelist des repos git autorisés
plugins/         — plugins OpenCode (TypeScript/Bun)
scripts/         — scripts shell d'infrastructure
skills/          — skills réutilisables (dossiers SKILL.md)
tasks/           — tâches planifiées opencode-tasks
tests/           — tests unitaires (bun test)
```

## Lancer les tests

```bash
bun test
```

## Ajouter un skill

1. Créer un dossier `skills/mon-skill/`
2. Y placer un fichier `SKILL.md` avec les instructions
3. Relancer `./install.sh` (crée le symlink automatiquement)

## Ajouter un plugin

1. Copier le template : `cp -r plugins/_template plugins/mon-plugin`
2. Renommer le plugin dans `index.ts` (propriété `name`)
3. Implémenter les hooks nécessaires
4. Ajouter la config dans `config/mon-plugin.json` si besoin
5. Relancer `./install.sh`

## Modifier la config guard

Éditer `config/guard.json` — pas besoin de toucher au TypeScript.

## Pull Request

- Conventional commits : `feat:`, `fix:`, `refactor:`, `docs:`
- `bun test` doit passer
- Pas de nouvelles dépendances sans justification

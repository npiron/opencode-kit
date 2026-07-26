# Plugin Template

## Créer un plugin

```bash
cp -r plugins/_template plugins/mon-plugin
```

1. Renommer `name` dans `index.ts`
2. Implémenter les hooks nécessaires
3. Ajouter la config dans `config/mon-plugin.json` si besoin
4. Relancer `./install.sh` — le symlink est créé automatiquement

## Hooks disponibles

| Hook | Quand |
|------|-------|
| `tool.execute.before` | Avant chaque appel d'outil — peut bloquer |
| `session.start` | Une fois au démarrage de la session |

## Bloquer un outil

```typescript
return { block: true, reason: "Message affiché à l'agent" }
```

## Autoriser

```typescript
return {}
```

---
name: scraper
description: Use for web scraping, data extraction from websites, crawling multi-page content, handling anti-bot measures, and extracting structured data from HTML. Trigger with keywords: scrape, extract, crawl, récupérer, extraire, parsing, DOM, selectors.
---

# Scraping Skill

Méthodologie de scraping web efficace avec Playwright et Fetch.

## Priorité des outils

1. **Fetch MCP** pour le contenu statique/APIs (rapide, léger)
   - `fetch_markdown` pour pages documentaires
   - `fetch_txt` pour texte brut
   - `fetch_readable` pour articles (Readability)
   - `fetch_json` pour APIs REST
   - `fetch_youtube_transcript` pour sous-titres YouTube

2. **Playwright** pour le contenu dynamique (rendu JS, SPA, formulaires)
   - Naviguer, cliquer, remplir des formulaires, scroller

3. **webfetch** intégré en fallback

## Anti-détection

- Google : accepter les cookies (`Tout accepter`) ou préférer DuckDuckGo
- Respecter `robots.txt`
- User-agent réaliste (Playwright le gère par défaut)
- Pas de rafale de requêtes : attendre 1-2s entre les navigations

## Extraction structurée

- Utiliser les snapshots Playwright (accessibilité tree) pour extraire le contenu
- Préférer les sélecteurs stables (data attributes, rôles ARIA) aux classes CSS
- Pour les tableaux/listes, extraire et formater en markdown

## Pagination

- Détecter les liens "Suivant" / "Page suivante"
- Parcourir séquentiellement avec un compteur max (défaut: 5 pages)
- Regrouper les résultats à la fin

## Erreurs courantes

- 403/429 → attendre 5-10s, réessayer avec moins d'agressivité
- Cookie wall → cliquer "Tout accepter" ou "Tout refuser"
- CAPTCHA → abandonner, proposer une alternative
- Timeout → augmenter le timeout ou simplifier la page cible

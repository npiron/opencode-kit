---
name: google-workspace
description: Use for Gmail, Google Docs, Drive, Sheets, Calendar, and other Google Workspace tasks. Trigger with keywords: gmail, google doc, google drive, google sheets, calendar, workspace, email, draft.
---

# Google Workspace

Regles et retours d'experience accumules pour l'utilisation des APIs Google Workspace via MCP.

## Regles Gmail

- **NE JAMAIS envoyer un mail** sans demande explicite de l'utilisateur.
  Toujours utiliser `draft_gmail_message` (brouillon) et laisser l'utilisateur
  verifier et valider avant envoi. Cette regle est absolue et prioritaire.

## Retour d'experience (07/2026)

- **Compte Gmail principal** : `piron.nicolas@gmail.com` (pas `nicolaspiron@gmail.com`).
- **APIs Google a activer** : Si erreur "API not enabled", donner directement les liens :
  - Google Docs API : `https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=206984738692`
  - Google Drive API : `https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com`
- **Upload de fichiers binaires** : Utiliser `fileUrl` (file://...) ou `base64_content`, jamais `content` pour
  les images/PDF.
- **Insertion d'image dans Google Docs** :
  - Preferer `insert_doc_image` avec l'ID Drive plutot que `batch_update_doc` + `insert_image`.
  - Rendre le fichier public (anyone with link) avant insertion.
  - Toujours specifier `width` ET `height` (> 0).
  - Les URLs `drive.google.com/uc?export=view` et `lh3.googleusercontent.com/d/` ne fonctionnent pas
    pour l'API Docs.
- **PDF non extractible** : Si `PyPDF2` ne trouve pas de texte, convertir en PNG (`sips`) puis OCR
  (`tesseract`). Si c'est un plan/schema visuel, l'OCR donnera peu -- integrer l'image directement.
- **Workflow creation de doc** :
  1. Importer le contenu texte en Markdown via `import_to_google_doc`
  2. Ajouter sauts de page avec `batch_update_doc` + `insert_section_break`
  3. Inserer images avec `insert_doc_image`
- **Recherche Gmail** : Toujours verifier le bon compte utilisateur avant de lancer `search_gmail_messages`.

---
name: google-workspace
description: Use for Gmail, Google Docs, Drive, Sheets, Calendar, and other Google Workspace tasks. Trigger with keywords: gmail, google doc, google drive, google sheets, calendar, workspace, email, draft.
---

# Google Workspace

Rules and lessons learned for using Google Workspace APIs via MCP.

## Gmail Rules

- **NEVER send an email** without an explicit request from the user.
  Always use `draft_gmail_message` (draft) and let the user
  review and approve before sending. This rule is absolute and takes priority.

## Lessons Learned (07/2026)

- **Main Gmail account**: `piron.nicolas@gmail.com` (not `nicolaspiron@gmail.com`).
- **Google APIs to enable**: If "API not enabled" error, provide the links directly:
  - Google Docs API: `https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=206984738692`
  - Google Drive API: `https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com`
- **Binary file uploads**: Use `fileUrl` (file://...) or `base64_content`, never `content` for
  images/PDFs.
- **Image insertion in Google Docs**:
  - Prefer `insert_doc_image` with the Drive ID rather than `batch_update_doc` + `insert_image`.
  - Make the file public (anyone with the link) before insertion.
  - Always specify `width` AND `height` (> 0).
  - `drive.google.com/uc?export=view` and `lh3.googleusercontent.com/d/` URLs don't work
    with the Docs API.
- **Non-extractable PDF**: If `PyPDF2` finds no text, convert to PNG (`sips`) then OCR
  (`tesseract`). If it's a visual plan/diagram, OCR will yield little — embed the image directly.
- **Doc creation workflow**:
  1. Import text content as Markdown via `import_to_google_doc`
  2. Add page breaks with `batch_update_doc` + `insert_section_break`
  3. Insert images with `insert_doc_image`
- **Gmail search**: Always verify the correct user account before running `search_gmail_messages`.

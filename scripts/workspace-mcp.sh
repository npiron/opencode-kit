#!/bin/bash
# Set these in your environment or replace with your own credentials
export GOOGLE_OAUTH_CLIENT_ID="${GOOGLE_OAUTH_CLIENT_ID:-your-client-id}"
export GOOGLE_OAUTH_CLIENT_SECRET="${GOOGLE_OAUTH_CLIENT_SECRET:-your-client-secret}"
export OAUTHLIB_INSECURE_TRANSPORT="1"
exec /Library/Frameworks/Python.framework/Versions/3.11/bin/workspace-mcp --tool-tier complete "$@"

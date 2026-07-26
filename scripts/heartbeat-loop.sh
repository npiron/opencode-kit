#!/bin/bash
BREW_PREFIX=$([ -d /opt/homebrew ] && echo /opt/homebrew || echo /usr/local)
export PATH="${BREW_PREFIX}/bin:${HOME}/.bun/bin:/usr/local/bin:/usr/bin:/bin"

echo "[$(date)] Démarrage heartbeat..." >> ~/.config/opencode/heartbeat/launchd.log

# Empêcher les doubles exécutions
LOCKFILE="$HOME/.config/opencode/heartbeat/running.lock"
if [ -f "$LOCKFILE" ]; then
    LOCKED_PID=$(cat "$LOCKFILE" 2>/dev/null)
    if [ -n "$LOCKED_PID" ] && kill -0 "$LOCKED_PID" 2>/dev/null; then
        echo "[$(date)] SKIP: heartbeat déjà en cours (PID $LOCKED_PID)" >> ~/.config/opencode/heartbeat/launchd.log
        exit 0
    fi
    echo "[$(date)] STALE LOCK détecté (PID $LOCKED_PID mort), nettoyage" >> ~/.config/opencode/heartbeat/launchd.log
fi
echo $$ > "$LOCKFILE"
trap "rm -f '$LOCKFILE'" EXIT

opencode run --agent heartbeat --dangerously-skip-permissions --dir "$HOME" \
  "Cycle heartbeat complet. CHECK INBOX → PROCESS → CONSOLIDATE → JOURNAL." \
  >> ~/.config/opencode/heartbeat/launchd.log 2>&1

echo "[$(date)] Heartbeat terminé (exit: $?)" >> ~/.config/opencode/heartbeat/launchd.log

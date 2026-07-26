/**
 * Pouls Guard — Security plugin for the heartbeat agent.
 *
 * Blocks:
 * - Destructive operations (by tool name, shell args, or git args)
 * - Email to anyone other than the allowed recipient
 * - Email rate limit exceed (per-beat and per-day)
 * - Git operations outside whitelisted repos
 */

import type { Plugin, ToolExecuteBeforeContext } from "@opencode-ai/plugin"
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { readGuardConfig, isDestructiveTool, isGitAllowed, checkEmailRateLimit } from "./lib.ts"
import type { RateLimits } from "./lib.ts"

const HEARTBEAT_DIR = join(homedir(), ".config", "opencode", "heartbeat")
const RATE_LIMITS_FILE = join(HEARTBEAT_DIR, "rate-limits.json")
const WHITELIST_FILE = join(HEARTBEAT_DIR, "repos-whitelist.txt")

const SEND_TOOLS = ["send_gmail_message", "workspace-mcp_send_gmail_message"]

function getToday(): string {
  return new Date().toISOString().slice(0, 10)
}

function readRateLimits(): RateLimits {
  const today = getToday()
  try {
    if (existsSync(RATE_LIMITS_FILE)) {
      const raw = JSON.parse(readFileSync(RATE_LIMITS_FILE, "utf-8")) as RateLimits
      if (raw.date === today) return raw
    }
  } catch { /* ignore */ }
  return { date: today, emails_sent: 0, emails_this_beat: 0, mails_processed: 0 }
}

function updateRateLimits(updates: Partial<RateLimits>): void {
  const current = readRateLimits()
  if (!existsSync(HEARTBEAT_DIR)) mkdirSync(HEARTBEAT_DIR, { recursive: true })
  writeFileSync(RATE_LIMITS_FILE, JSON.stringify({ ...current, ...updates }, null, 2))
}

function readWhitelist(): string[] {
  try {
    if (existsSync(WHITELIST_FILE)) {
      return readFileSync(WHITELIST_FILE, "utf-8")
        .split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"))
    }
  } catch { /* ignore */ }
  return []
}

export default async function poulsGuard(): Promise<Plugin> {
  return {
    name: "pouls-guard",
    hooks: {
      "tool.execute.before": async (ctx: ToolExecuteBeforeContext) => {
        const { tool, args } = ctx
        const config = readGuardConfig()

        if (isDestructiveTool(tool, args, config)) {
          return { block: true, reason: `[Pouls] Opération destructive bloquée : ${tool}` }
        }

        if (SEND_TOOLS.includes(tool)) {
          const to = args?.to as string | undefined
          if (to && to !== config.email.allowed_recipient) {
            return {
              block: true,
              reason: `[Pouls] Email bloqué : "${to}" non autorisé. Seul ${config.email.allowed_recipient} est permis.`,
            }
          }
          const limits = readRateLimits()
          const limitErr = checkEmailRateLimit(limits, config.email.max_per_beat, config.email.max_per_day)
          if (limitErr) return { block: true, reason: `[Pouls] ${limitErr}` }
          // Optimistic increment — stays incremented if downstream send fails (conservative).
          updateRateLimits({ emails_sent: limits.emails_sent + 1, emails_this_beat: limits.emails_this_beat + 1 })
        }

        if (!isGitAllowed(tool, args, readWhitelist())) {
          const cwd = String(args?.cwd ?? args?.dir ?? "")
          return { block: true, reason: `[Pouls] Git bloqué : "${cwd}" hors de la liste blanche` }
        }

        return {}
      },

      "session.start": async () => {
        updateRateLimits({ emails_this_beat: 0, mails_processed: 0 })
      },
    },
  }
}

/**
 * Pouls Guard — Security plugin for the heartbeat agent.
 *
 * Blocks:
 * - Email to anyone other than piron.nicolas@gmail.com
 * - Destructive operations (delete, rm, drop, trash)
 * - Email rate limit exceed (3/beat, 10/day)
 * - Git operations outside whitelisted repos
 */

import type { Plugin, ToolExecuteBeforeContext } from "@opencode-ai/plugin"
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"

const HEARTBEAT_DIR = join(homedir(), ".config", "opencode", "heartbeat")
const RATE_LIMITS_FILE = join(HEARTBEAT_DIR, "rate-limits.json")
const WHITELIST_FILE = join(HEARTBEAT_DIR, "repos-whitelist.txt")

const ALLOWED_EMAIL = "piron.nicolas@gmail.com"
const DESTRUCTIVE_PATTERNS = ["delete", "rm", "drop", "trash"]
const MAX_EMAILS_PER_BEAT = 3
const MAX_EMAILS_PER_DAY = 10

interface RateLimits {
  date: string
  emails_sent: number
  emails_this_beat: number
  mails_processed: number
}

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
  const merged = { ...current, ...updates }
  if (!existsSync(HEARTBEAT_DIR)) {
    mkdirSync(HEARTBEAT_DIR, { recursive: true })
  }
  writeFileSync(RATE_LIMITS_FILE, JSON.stringify(merged, null, 2))
}

function readWhitelist(): string[] {
  try {
    if (existsSync(WHITELIST_FILE)) {
      return readFileSync(WHITELIST_FILE, "utf-8")
        .split("\n")
        .map(l => l.trim())
        .filter(l => l.length > 0 && !l.startsWith("#"))
    }
  } catch { /* ignore */ }
  return []
}

function isDestructive(toolName: string): boolean {
  const lower = toolName.toLowerCase()
  return DESTRUCTIVE_PATTERNS.some(p => lower.includes(p))
}

function isGitTool(toolName: string): boolean {
  return toolName.startsWith("git")
}

export default async function poulsGuard(): Promise<Plugin> {
  return {
    name: "pouls-guard",
    hooks: {
      "tool.execute.before": async (ctx: ToolExecuteBeforeContext) => {
        const { tool, args } = ctx

        // Block destructive operations
        if (isDestructive(tool)) {
          return {
            block: true,
            reason: `[Pouls] Opération destructive bloquée : ${tool}`
          }
        }

        // Block email to unauthorized recipients
        if (tool === "send_gmail_message" || tool === "workspace-mcp_send_gmail_message") {
          const to = args?.to as string | undefined
          if (to && to !== ALLOWED_EMAIL) {
            return {
              block: true,
              reason: `[Pouls] Email bloqué : destinataire "${to}" non autorisé. Seul ${ALLOWED_EMAIL} est permis.`
            }
          }

          // Rate limiting
          const limits = readRateLimits()
          if (limits.emails_this_beat >= MAX_EMAILS_PER_BEAT) {
            return {
              block: true,
              reason: `[Pouls] Rate limit battement atteint (max ${MAX_EMAILS_PER_BEAT} emails/battement)`
            }
          }
          if (limits.emails_sent >= MAX_EMAILS_PER_DAY) {
            return {
              block: true,
              reason: `[Pouls] Rate limit journalier atteint (max ${MAX_EMAILS_PER_DAY} emails/jour)`
            }
          }
          updateRateLimits({
            emails_sent: limits.emails_sent + 1,
            emails_this_beat: limits.emails_this_beat + 1
          })
        }

        // Block git outside whitelisted repos
        if (isGitTool(tool)) {
          const whitelist = readWhitelist()
          const cwd = (args?.cwd as string) || (args?.dir as string) || process.cwd()
          const allowed = whitelist.some(repo => cwd.startsWith(repo))
          if (!allowed) {
            return {
              block: true,
              reason: `[Pouls] Git bloqué : "${cwd}" hors de la liste blanche`
            }
          }
        }

        return {} // allow
      },

      "session.start": async () => {
        const limits = readRateLimits()
        updateRateLimits({ ...limits, emails_this_beat: 0, mails_processed: 0 })
      }
    }
  }
}

/**
 * Pure, testable functions for pouls-guard.
 * No side effects — all file I/O stays in index.ts.
 */

import { readFileSync, existsSync } from "node:fs"

export interface GuardConfig {
  email: {
    allowed_recipient: string
    max_per_beat: number
    max_per_day: number
  }
  destructive: {
    tool_names: string[]
    shell_commands: string[]
    git_commands: string[]
  }
}

export interface RateLimits {
  date: string
  emails_sent: number
  emails_this_beat: number
  mails_processed: number
}

const DEFAULT_CONFIG: GuardConfig = {
  email: { allowed_recipient: "piron.nicolas@gmail.com", max_per_beat: 3, max_per_day: 10 },
  destructive: {
    tool_names: ["delete", "rm", "drop", "trash"],
    shell_commands: ["rm -rf", "sudo", "truncate", "mkfs"],
    git_commands: ["push --force", "push -f", "reset --hard", "clean -f"],
  },
}

export function readGuardConfig(configPath?: string): GuardConfig {
  const path = configPath ?? new URL("../../config/guard.json", import.meta.url).pathname
  try {
    if (existsSync(path)) return JSON.parse(readFileSync(path, "utf-8")) as GuardConfig
  } catch { /* fall through to defaults */ }
  return DEFAULT_CONFIG
}

const SHELL_TOOLS = ["bash", "execute_command", "run_command", "run_terminal_cmd"]

export function isDestructiveTool(
  toolName: string,
  args: Record<string, unknown> | undefined,
  config: GuardConfig,
): boolean {
  const lower = toolName.toLowerCase()

  if (config.destructive.tool_names.some(p => lower.includes(p))) return true

  if (SHELL_TOOLS.some(t => lower.includes(t))) {
    const cmd = String(args?.command ?? args?.cmd ?? args?.input ?? "").toLowerCase()
    if (config.destructive.shell_commands.some(p => cmd.includes(p.toLowerCase()))) return true
  }

  if (lower.startsWith("git")) {
    const cmd = String(args?.command ?? args?.args ?? "").toLowerCase()
    if (config.destructive.git_commands.some(p => cmd.includes(p.toLowerCase()))) return true
  }

  return false
}

export function isGitAllowed(
  toolName: string,
  args: Record<string, unknown> | undefined,
  whitelist: string[],
): boolean {
  if (!toolName.toLowerCase().startsWith("git")) return true
  const cwd = String(args?.cwd ?? args?.dir ?? "")
  return whitelist.some(repo => cwd.startsWith(repo))
}

export function checkEmailRateLimit(
  limits: RateLimits,
  maxPerBeat: number,
  maxPerDay: number,
): string | null {
  if (limits.emails_this_beat >= maxPerBeat) return `Rate limit battement atteint (max ${maxPerBeat}/battement)`
  if (limits.emails_sent >= maxPerDay) return `Rate limit journalier atteint (max ${maxPerDay}/jour)`
  return null
}

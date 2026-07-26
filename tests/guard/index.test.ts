import { test, expect, describe } from "bun:test"
import { isDestructiveTool, isGitAllowed, checkEmailRateLimit } from "../../plugins/pouls-guard/lib.ts"
import type { GuardConfig, RateLimits } from "../../plugins/pouls-guard/lib.ts"

const config: GuardConfig = {
  email: { allowed_recipient: "test@example.com", max_per_beat: 3, max_per_day: 10 },
  destructive: {
    tool_names: ["delete", "rm", "drop", "trash"],
    shell_commands: ["rm -rf", "sudo", "truncate"],
    git_commands: ["push --force", "push -f", "reset --hard", "clean -f"],
  },
}

const base: RateLimits = { date: "2026-01-01", emails_sent: 0, emails_this_beat: 0, mails_processed: 0 }
const whitelist = ["/home/user/safe-repo", "/home/user/project"]

// ── isDestructiveTool ─────────────────────────────────────

describe("isDestructiveTool — tool names", () => {
  test("blocks tool with destructive name", () => {
    expect(isDestructiveTool("delete_file", undefined, config)).toBe(true)
    expect(isDestructiveTool("workspace-mcp_trash_email", undefined, config)).toBe(true)
    expect(isDestructiveTool("drop_table", undefined, config)).toBe(true)
  })

  test("allows safe tool names", () => {
    expect(isDestructiveTool("read_file", undefined, config)).toBe(false)
    expect(isDestructiveTool("list_directory", undefined, config)).toBe(false)
    expect(isDestructiveTool("send_gmail_message", undefined, config)).toBe(false)
    expect(isDestructiveTool("workspace-mcp_search_gmail_messages", undefined, config)).toBe(false)
  })
})

describe("isDestructiveTool — shell args", () => {
  test("blocks rm -rf in command args", () => {
    expect(isDestructiveTool("bash", { command: "rm -rf /tmp/test" }, config)).toBe(true)
    expect(isDestructiveTool("execute_command", { cmd: "sudo apt install vim" }, config)).toBe(true)
    expect(isDestructiveTool("run_terminal_cmd", { input: "truncate -s 0 file.log" }, config)).toBe(true)
  })

  test("allows safe shell commands", () => {
    expect(isDestructiveTool("bash", { command: "ls -la" }, config)).toBe(false)
    expect(isDestructiveTool("bash", { command: "git status" }, config)).toBe(false)
    expect(isDestructiveTool("bash", { command: "echo hello" }, config)).toBe(false)
  })

  test("case-insensitive matching", () => {
    expect(isDestructiveTool("BASH", { command: "RM -RF /tmp" }, config)).toBe(true)
  })
})

describe("isDestructiveTool — git args", () => {
  test("blocks dangerous git commands", () => {
    expect(isDestructiveTool("git_run", { command: "push --force" }, config)).toBe(true)
    expect(isDestructiveTool("git_execute", { args: "reset --hard HEAD~1" }, config)).toBe(true)
    expect(isDestructiveTool("git_cmd", { command: "push -f origin main" }, config)).toBe(true)
    expect(isDestructiveTool("git_run", { command: "clean -f dist/" }, config)).toBe(true)
  })

  test("allows safe git commands", () => {
    expect(isDestructiveTool("git_status", { command: "status" }, config)).toBe(false)
    expect(isDestructiveTool("git_log", { args: "--oneline -10" }, config)).toBe(false)
    expect(isDestructiveTool("git_diff", { command: "diff HEAD" }, config)).toBe(false)
    expect(isDestructiveTool("git_commit", { args: "-m 'fix: something'" }, config)).toBe(false)
  })
})

// ── isGitAllowed ──────────────────────────────────────────

describe("isGitAllowed", () => {
  test("always allows non-git tools", () => {
    expect(isGitAllowed("read_file", { cwd: "/etc" }, whitelist)).toBe(true)
    expect(isGitAllowed("bash", { cwd: "/tmp" }, whitelist)).toBe(true)
  })

  test("allows git inside whitelisted repo", () => {
    expect(isGitAllowed("git_status", { cwd: "/home/user/safe-repo" }, whitelist)).toBe(true)
    expect(isGitAllowed("git_commit", { dir: "/home/user/project/subdir" }, whitelist)).toBe(true)
  })

  test("blocks git outside whitelist", () => {
    expect(isGitAllowed("git_commit", { cwd: "/tmp/random" }, whitelist)).toBe(false)
    expect(isGitAllowed("git_push", { cwd: "/etc/config" }, whitelist)).toBe(false)
    expect(isGitAllowed("git_status", { cwd: "" }, whitelist)).toBe(false)
  })

  test("blocks git with empty whitelist", () => {
    expect(isGitAllowed("git_status", { cwd: "/home/user/safe-repo" }, [])).toBe(false)
  })
})

// ── checkEmailRateLimit ───────────────────────────────────

describe("checkEmailRateLimit", () => {
  test("allows when well under limits", () => {
    expect(checkEmailRateLimit(base, 3, 10)).toBeNull()
    expect(checkEmailRateLimit({ ...base, emails_sent: 5, emails_this_beat: 1 }, 3, 10)).toBeNull()
  })

  test("allows at limit boundary (exclusive)", () => {
    expect(checkEmailRateLimit({ ...base, emails_this_beat: 2 }, 3, 10)).toBeNull()
    expect(checkEmailRateLimit({ ...base, emails_sent: 9 }, 3, 10)).toBeNull()
  })

  test("blocks when per-beat limit reached", () => {
    const result = checkEmailRateLimit({ ...base, emails_this_beat: 3 }, 3, 10)
    expect(result).not.toBeNull()
    expect(result).toMatch(/battement/)
  })

  test("blocks when daily limit reached", () => {
    const result = checkEmailRateLimit({ ...base, emails_sent: 10 }, 3, 10)
    expect(result).not.toBeNull()
    expect(result).toMatch(/journalier/)
  })

  test("per-beat limit takes priority over daily", () => {
    const result = checkEmailRateLimit({ ...base, emails_this_beat: 5, emails_sent: 15 }, 3, 10)
    expect(result).toMatch(/battement/)
  })
})

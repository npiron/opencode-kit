import type { Plugin, ToolExecuteBeforeContext } from "@opencode-ai/plugin"

export default async function myPlugin(): Promise<Plugin> {
  return {
    name: "my-plugin",
    hooks: {
      "tool.execute.before": async (ctx: ToolExecuteBeforeContext) => {
        const { tool, args } = ctx
        // Return { block: true, reason: "..." } to block, or {} to allow.
        return {}
      },

      "session.start": async () => {
        // Called once at the beginning of each session.
      },
    },
  }
}

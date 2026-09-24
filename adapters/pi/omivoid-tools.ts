/**
 * Omivoid Pi Tool Bridge (docs/ai/02 §17–19, docs/ai/10 §17, AI-11)
 *
 * Exposes the Omivoid AI-accessible capability catalogue as Pi tools.
 *
 * Tool definitions are GENERATED from the Action Registry at session
 * start via `omivoid ai capabilities --json` — no hand-written
 * catalogue (docs/ai/02 §18).
 *
 * Tool name translation: Pi tool names are restricted to [a-z0-9_],
 * so `app.browser.open` becomes `app_browser_open`. The canonical
 * action ID is preserved and passed to the runner.
 *
 * Execution: `omivoid action run <id> --json`. Pi never executes
 * implementation commands directly for registered capabilities
 * (docs/ai/02 §19). Only actions in the AI-accessible catalogue can
 * be invoked — the catalogue is the policy boundary (AGENTS.md §17).
 *
 * CLI resolution: $OMIVOID_CLI if set, otherwise `omivoid` from PATH.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

interface Capability {
  id: string;
  name: string;
  description: string;
  risk: string;
  confirmation: string;
}

interface ActionResult {
  success: boolean;
  action?: string;
  state?: Record<string, unknown>;
  error?: { code: string; message: string };
}

/** Pi tool names must match /^[a-z0-9_]+$/ (see dynamic-tools example). */
function toToolName(actionId: string): string {
  return actionId.replace(/[^a-z0-9_]/g, "_");
}

function resolveOmivoidCli(): string {
  return process.env.OMIVOID_CLI ?? "omivoid";
}

export default function omivoidToolsExtension(pi: ExtensionAPI) {
  const cli = resolveOmivoidCli();

  async function loadCapabilities(): Promise<Capability[]> {
    const result = await pi.exec(cli, ["ai", "capabilities", "--json"]);
    if (result.code !== 0) {
      throw new Error(
        `omivoid ai capabilities failed (${result.code}): ` +
          `${result.stderr || result.stdout}`,
      );
    }
    return JSON.parse(result.stdout) as Capability[];
  }

  async function runAction(actionId: string): Promise<ActionResult> {
    const result = await pi.exec(cli, ["action", "run", actionId, "--json"]);
    if (result.code !== 0) {
      throw new Error(
        `omivoid action run ${actionId} failed (${result.code}): ` +
          `${result.stderr || result.stdout}`,
      );
    }
    return JSON.parse(result.stdout) as ActionResult;
  }

  function registerTool(cap: Capability): void {
    const toolName = toToolName(cap.id);
    pi.registerTool({
      name: toolName,
      label: cap.name,
      description: `${cap.description} (Omivoid action ${cap.id}, risk: ${cap.risk})`,
      promptSnippet: `Run the Omivoid desktop action ${cap.id} (${cap.name})`,
      promptGuidelines: [
        `Use ${toolName} when the user asks to ${cap.description.toLowerCase()}`,
      ],
      parameters: Type.Object({}),
      async execute(_toolCallId, _params, _signal, _onUpdate, _ctx) {
        const result = await runAction(cap.id);
        if (!result.success) {
          const err = result.error ?? { code: "UNKNOWN", message: "unknown error" };
          throw new Error(`${err.code}: ${err.message}`);
        }
        return {
          content: [
            {
              type: "text",
              text: `Omivoid action ${cap.id} executed successfully.`,
            },
          ],
          details: { action: cap.id, state: result.state ?? {} },
        };
      },
    });
  }

  pi.on("session_start", async (_event, ctx) => {
    try {
      const caps = await loadCapabilities();
      for (const cap of caps) {
        registerTool(cap);
      }
      ctx.ui.notify(
        `Omivoid bridge: ${caps.length} capability/capabilities registered`,
        "info",
      );
    } catch (err) {
      ctx.ui.notify(
        `Omivoid bridge: ${(err as Error).message}`,
        "error",
      );
    }
  });
}
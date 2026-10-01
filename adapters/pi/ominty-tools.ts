/**
 * Ominty Pi Tool Bridge (docs/ai/02 §17–19, docs/ai/10 §17, AI-11)
 *
 * Exposes the Ominty AI-accessible capability catalogue as Pi tools.
 *
 * Tool definitions are GENERATED from the Action Registry at session
 * start via `ominty ai capabilities --json` — no hand-written
 * catalogue (docs/ai/02 §18).
 *
 * Tool name translation: Pi tool names are restricted to [a-z0-9_],
 * so `app.browser.open` becomes `app_browser_open`. The canonical
 * action ID is preserved and passed to the runner.
 *
 * Execution: `ominty action run <id> --ai --json`. Pi never executes
 * implementation commands directly for registered capabilities
 * (docs/ai/02 §19). Only actions in the AI-accessible catalogue can
 * be invoked — the catalogue is the policy boundary (AGENTS.md §17),
 * and Ominty re-checks policy per request (docs/ai/09).
 *
 * Confirmation: when Ominty returns CONFIRMATION_REQUIRED, the user
 * is asked via Pi's UI and the action is retried with --confirmed.
 * The model can never approve its own action (docs/ai/09 §10).
 *
 * CLI resolution: $OMINTY_CLI if set, otherwise `ominty` from PATH.
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
  confirmation_required?: boolean;
  error?: { code: string; message: string; reason?: string };
}

/** Pi tool names must match /^[a-z0-9_]+$/ (see dynamic-tools example). */
function toToolName(actionId: string): string {
  return actionId.replace(/[^a-z0-9_]/g, "_");
}

function resolveOmintyCli(): string {
  return process.env.OMINTY_CLI ?? "ominty";
}

export default function omintyToolsExtension(pi: ExtensionAPI) {
  const cli = resolveOmintyCli();

  async function loadCapabilities(): Promise<Capability[]> {
    const result = await pi.exec(cli, ["ai", "capabilities", "--json"]);
    if (result.code !== 0) {
      throw new Error(
        `ominty ai capabilities failed (${result.code}): ` +
          `${result.stderr || result.stdout}`,
      );
    }
    return JSON.parse(result.stdout) as Capability[];
  }

  async function runAction(
    actionId: string,
    confirmed: boolean,
  ): Promise<ActionResult> {
    const args = ["action", "run", actionId, "--ai", "--json"];
    if (confirmed) {
      args.push("--confirmed");
    }
    const result = await pi.exec(cli, args);
    // A denial still exits non-zero, but --json emits a structured result
    // on stdout. Prefer the structured result; throw only if it is absent.
    try {
      return JSON.parse(result.stdout) as ActionResult;
    } catch {
      throw new Error(
        `ominty action run ${actionId} failed (${result.code}): ` +
          `${result.stderr || result.stdout}`,
      );
    }
  }

  function registerTool(cap: Capability): void {
    const toolName = toToolName(cap.id);
    pi.registerTool({
      name: toolName,
      label: cap.name,
      description: `${cap.description} (Ominty action ${cap.id}, risk: ${cap.risk})`,
      promptSnippet: `Run the Ominty desktop action ${cap.id} (${cap.name})`,
      promptGuidelines: [
        `Use ${toolName} when the user asks to ${cap.description.toLowerCase()}`,
      ],
      parameters: Type.Object({}),
      async execute(_toolCallId, _params, _signal, _onUpdate, ctx) {
        let result = await runAction(cap.id, false);

        // Ominty policy may require user confirmation. The user decides;
        // the model can never set --confirmed itself (docs/ai/09 §10).
        if (!result.success && result.confirmation_required) {
          let approved = false;
          try {
            approved = await ctx.ui.confirm(
              "Ominty: confirm action",
              `${cap.name} (${cap.id})\n` +
                `risk: ${cap.risk}  ·  confirmation: ${cap.confirmation}\n\n` +
                `An AI request wants to run this action. Approve?`,
            );
          } catch {
            throw new Error(
              `CONFIRMATION_REQUIRED: '${cap.id}' needs user approval ` +
                `(interactive session required)`,
            );
          }
          if (!approved) {
            throw new Error(`PERMISSION_DENIED: user denied '${cap.id}'`);
          }
          result = await runAction(cap.id, true);
        }

        if (!result.success) {
          const err = result.error ?? {
            code: "UNKNOWN",
            message: "unknown error",
          };
          throw new Error(`${err.code}: ${err.message}`);
        }
        return {
          content: [
            {
              type: "text",
              text: `Ominty action ${cap.id} executed successfully.`,
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
        `Ominty bridge: ${caps.length} capability/capabilities registered`,
        "info",
      );
    } catch (err) {
      ctx.ui.notify(
        `Ominty bridge: ${(err as Error).message}`,
        "error",
      );
    }
  });
}
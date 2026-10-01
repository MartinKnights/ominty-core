// Ominty Actions — DMS launcher provider.
//
// Bridges the Ominty Action Registry into the DMS launcher.
//
//   Ominty Action Registry
//          │  (ominty action list --json)
//          ▼
//   OmintyActions.qml
//          │  (launcher items)
//          ▼
//   DMS launcher / spotlight
//          │  (executeItem)
//          ▼
//   ominty action run <id>
//
// The Action Registry remains authoritative. This plugin is presentation
// and invocation only; it never redefines action semantics (ADR-006 §5–6).

import QtQuick
import Quickshell
import Quickshell.Io
import qs.Services

Item {
    id: root

    // ---- Plugin interface (DMS launcher contract) ------------------------
    property var pluginService: null
    property string trigger: ""

    signal itemsChanged()

    // ---- Configuration ---------------------------------------------------
    // Path to the Ominty CLI. Portable default: the OMINTY_CLI environment
    // variable if set, otherwise `ominty` on PATH. Machine-specific paths
    // belong in plugin settings (user config), not in this source
    // (AGENTS.md §22–24).
    property string cliPath: Quickshell.env("OMINTY_CLI") || "ominty"

    // Which registry actions to surface.
    //   "all"          — every action
    //   "discoverable" — actions flagged discoverable (Super+K explorer)
    //   "palette"      — actions flagged palette (Super+Space palette)
    property string filterMode: "all"

    // ---- State -----------------------------------------------------------
    property var _actions: []
    property bool _loading: false

    Component.onCompleted: {
        if (!pluginService)
            return;

        // First-run default (ADR-006 §13): merge Ominty actions into the
        // universal palette (Super+Space). The interaction explorer (Super+K)
        // is opened with the "!!" sentinel instead of a trigger. Users may
        // switch to trigger mode from the plugin settings.
        if (pluginService.loadPluginData("omintyActions", "noTrigger", undefined) === undefined) {
            pluginService.savePluginData("omintyActions", "noTrigger", true);
            pluginService.savePluginData("omintyActions", "trigger", "");
        }

        trigger = pluginService.loadPluginData("omintyActions", "trigger", "");
        cliPath = pluginService.loadPluginData("omintyActions", "cliPath", cliPath);
        filterMode = pluginService.loadPluginData("omintyActions", "filterMode", "all");
        console.info("[OmintyActions] Activation mode:",
                     trigger.trim() === "" ? "always-active (palette merge)" : ("trigger '" + trigger + "'"));
        Qt.callLater(loadActions);
    }

    // ---- Registry loading ------------------------------------------------
    function loadActions() {
        _loading = true;
        listProcess.running = true;
    }

    function _accepts(action) {
        if (filterMode === "discoverable")
            return action.discoverable !== false;
        if (filterMode === "palette")
            return action.palette !== false;
        return true;
    }

    function _binding(action) {
        if (action.primary_key)
            return action.primary_key;
        if (action.keys && action.keys.length > 0)
            return action.keys[0];
        return "";
    }

    // ---- Context indicator (AI-21) --------------------------------------
    // Shows which context an AI action consumes, so the user can see what
    // is being sent (docs/ai/03 §11, docs/ai/05 §9). Only implemented
    // context types are shown (docs/ai/10 §27).
    function _contextChip(action) {
        const ctx = action.contexts || [];
        if (ctx.indexOf("clipboard") !== -1)
            return "[Clipboard]";
        return "";
    }

    // ---- AI menu (Super+A) -----------------------------------------------
    // Lists AI-category actions. When the query carried a prompt
    // ("!ai what is 2+2"), a direct "Ask AI" entry is offered first.
    // ai.ask routes through the Ominty provider layer, never a second path.
    function aiItems(rest) {
        const prompt = (rest || "").trim();
        const results = [];

        if (prompt.length > 0) {
            results.push({
                name: "Ask AI: " + prompt,
                icon: "material:bolt",
                comment: "Ask the default AI provider",
                action: "ask:" + prompt,
                categories: ["Ominty · AI"]
            });
        } else {
            results.push({
                name: "Ask AI",
                icon: "material:bolt",
                comment: "Type your question to ask the default AI provider",
                action: "askhint:",
                categories: ["Ominty · AI"]
            });
        }

        for (let i = 0; i < _actions.length; i++) {
            const a = _actions[i];
            if (!_accepts(a))
                continue;
            if ((a.category || "") !== "AI")
                continue;
            // The menu itself and ai.ask (handled above) are not listed.
            if (a.id === "ai.menu.open" || a.id === "ai.ask")
                continue;
            const binding = _binding(a);
            const chip = _contextChip(a);
            results.push({
                name: a.name || a.id,
                icon: "material:bolt",
                comment: (binding ? binding + "  ·  " : "") +
                         (chip ? chip + "  " : "") +
                         (a.description || a.id),
                action: "run:" + a.id,
                categories: ["Ominty · AI"],
                _omintyId: a.id,
                _omintyBinding: binding,
                _omintyRisk: a.risk || "routine"
            });
        }

        console.info("[OmintyActions] AI mode:", results.length, "items");
        return results;
    }

    // ---- Launcher contract ----------------------------------------------
    // Query semantics (ADR-006 §12–13, ai-dms-evaluation.md §7):
    //   "!!..."  explicit interaction-explorer request (Super+K): show all
    //            actions, or filter the remainder after "!!". Two characters
    //            are used because the DMS launcher ignores 1-char queries
    //            in the plugin phase.
    //   "!ai..." AI menu (Super+A): list AI actions; "!ai <text>" offers a
    //            direct "Ask AI: <text>" entry. The AI prefix is presented
    //            here because Niri has no keybinding chords.
    //   ""       in trigger mode DMS strips the trigger, so an empty query
    //            means "show everything"; in no-trigger mode an empty query
    //            is the palette default view, which we leave to DMS to avoid
    //            clutter until the user types.
    //   other    normal filter against the registry.
    function getItems(query) {
        let q = query ? String(query) : "";

        if (q.indexOf("!ai") === 0)
            return aiItems(q.slice(3));

        let explicit = false;
        if (q.indexOf("!") === 0) {
            explicit = true;
            q = q.replace(/^!+/, "");
        }
        q = q.toLowerCase().trim();

        const triggerMode = trigger && trigger.trim() !== "";
        const showAll = q.length === 0 && (explicit || triggerMode);
        if (q.length === 0 && !showAll)
            return [];

        const results = [];

        for (let i = 0; i < _actions.length; i++) {
            const a = _actions[i];
            if (!_accepts(a))
                continue;

            const haystack = [
                a.name || "",
                a.description || "",
                a.category || "",
                a.id || "",
                (a.keywords || []).join(" "),
                (a.keys || []).join(" ")
            ].join(" ").toLowerCase();

            if (!showAll && q.length > 0 && haystack.indexOf(q) === -1)
                continue;

            const binding = _binding(a);
            results.push({
                name: a.name || a.id,
                icon: "material:bolt",
                comment: (binding ? binding + "  ·  " : "") + (a.description || a.id),
                action: "run:" + a.id,
                categories: ["Ominty · " + (a.category || "Actions")],
                _omintyId: a.id,
                _omintyBinding: binding,
                _omintyRisk: a.risk || "routine"
            });
        }

        results.sort((x, y) => (x.name || "").localeCompare(y.name || ""));
        if (explicit)
            console.info("[OmintyActions] Explorer requested:", results.length, "actions");
        return results.slice(0, 50);
    }

    function executeItem(item) {
        if (!item || !item.action)
            return;
        const parts = item.action.split(":");
        const kind = parts[0];
        const value = parts.slice(1).join(":");

        if (kind === "run") {
            // AI response actions (ai.clipboard.*) capture their reply and
            // deliver it as a notification; other actions are fire-and-forget.
            if (value.indexOf("ai.clipboard.") === 0) {
                askProcess.command = [cliPath, "action", "run", value, "--json"];
                askProcess.running = true;
                if (typeof ToastService !== "undefined")
                    ToastService.showInfo("Ominty AI", "Asking…");
                return;
            }
            Quickshell.execDetached([cliPath, "action", "run", value]);
            if (typeof ToastService !== "undefined")
                ToastService.showInfo("Ominty", item.name);
            return;
        }

        if (kind === "ask") {
            // Runs the same provider architecture as `ominty ai ask`
            // (AI-19); the AI menu never creates a second invocation path.
            askProcess.command = [cliPath, "ai", "ask", value];
            askProcess.running = true;
            if (typeof ToastService !== "undefined")
                ToastService.showInfo("Ominty AI", "Asking…");
            return;
        }

        if (kind === "askhint") {
            if (typeof ToastService !== "undefined")
                ToastService.showInfo("Ominty AI", "Type your question after Super+A");
        }
    }

    onTriggerChanged: {
        if (pluginService)
            pluginService.savePluginData("omintyActions", "trigger", trigger);
    }

    // ---- AI ask ----------------------------------------------------------
    // Runs `ominty ai ask <prompt>` (plain text) or
    // `ominty action run ai.clipboard.* --json` (structured). Replies are
    // delivered as DMS notifications (docs/ai/03 §34) — persistent in the
    // notification centre, unlike a transient toast.
    function notifyReply(reply) {
        const body = (reply && reply.length > 0) ? reply : "(no response)";
        Quickshell.execDetached(["notify-send", "-a", "Ominty AI", "-t", "0",
                                 "Ominty AI", body]);
    }

    Process {
        id: askProcess
        running: false

        stdout: StdioCollector {
            onStreamFinished: {
                const raw = (text || "").trim();
                let reply = raw;
                try {
                    const parsed = JSON.parse(raw);
                    if (parsed && parsed.state && parsed.state.response)
                        reply = parsed.state.response;
                    else if (parsed && parsed.error)
                        reply = parsed.error.code + ": " + parsed.error.message;
                } catch (e) {
                    // Plain text reply (ai ask).
                }
                root.notifyReply(reply);
            }
        }

        onExited: exitCode => {
            if (exitCode !== 0) {
                Quickshell.execDetached(["notify-send", "-a", "Ominty AI",
                                         "-u", "critical", "Ominty AI",
                                         "Ask failed (exit " + exitCode + ")"]);
            }
        }
    }

    // ---- Registry read ---------------------------------------------------
    Process {
        id: listProcess
        command: [root.cliPath, "action", "list", "--json"]
        running: false

        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    root._actions = JSON.parse(text);
                    console.info("[OmintyActions] Loaded", root._actions.length, "actions from registry");
                } catch (e) {
                    console.error("[OmintyActions] Failed to parse action list:", e);
                    root._actions = [];
                }
                root._loading = false;
                root.itemsChanged();
            }
        }

        onExited: exitCode => {
            if (exitCode !== 0) {
                console.warn("[OmintyActions] action list failed, exit:", exitCode);
                root._loading = false;
                root.itemsChanged();
            }
        }
    }
}

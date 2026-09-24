// Omivoid Actions — DMS launcher provider.
//
// Bridges the Omivoid Action Registry into the DMS launcher.
//
//   Omivoid Action Registry
//          │  (omivoid action list --json)
//          ▼
//   OmivoidActions.qml
//          │  (launcher items)
//          ▼
//   DMS launcher / spotlight
//          │  (executeItem)
//          ▼
//   omivoid action run <id>
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
    // Path to the Omivoid CLI. Defaults to the in-repository entry point.
    // Override in plugin settings once Omivoid installs a `omivoid` binary.
    property string cliPath: "/home/mk/Projects/OmiVoid/omivoid-lmde/cli/omivoid"

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

        // First-run default (ADR-006 §13): merge Omivoid actions into the
        // universal palette (Super+Space). The interaction explorer (Super+K)
        // is opened with the "!!" sentinel instead of a trigger. Users may
        // switch to trigger mode from the plugin settings.
        if (pluginService.loadPluginData("omivoidActions", "noTrigger", undefined) === undefined) {
            pluginService.savePluginData("omivoidActions", "noTrigger", true);
            pluginService.savePluginData("omivoidActions", "trigger", "");
        }

        trigger = pluginService.loadPluginData("omivoidActions", "trigger", "");
        cliPath = pluginService.loadPluginData("omivoidActions", "cliPath", cliPath);
        filterMode = pluginService.loadPluginData("omivoidActions", "filterMode", "all");
        console.info("[OmivoidActions] Activation mode:",
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

    // ---- Launcher contract ----------------------------------------------
    // Query semantics (ADR-006 §12–13):
    //   "!!..."  explicit interaction-explorer request (Super+K): show all
    //            actions, or filter the remainder after "!!". Two characters
    //            are used because the DMS launcher ignores 1-char queries
    //            in the plugin phase.
    //   ""       in trigger mode DMS strips the trigger, so an empty query
    //            means "show everything"; in no-trigger mode an empty query
    //            is the palette default view, which we leave to DMS to avoid
    //            clutter until the user types.
    //   other    normal filter against the registry.
    function getItems(query) {
        let q = query ? String(query) : "";
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
                categories: ["Omivoid · " + (a.category || "Actions")],
                _omivoidId: a.id,
                _omivoidBinding: binding,
                _omivoidRisk: a.risk || "routine"
            });
        }

        results.sort((x, y) => (x.name || "").localeCompare(y.name || ""));
        if (explicit)
            console.info("[OmivoidActions] Explorer requested:", results.length, "actions");
        return results.slice(0, 50);
    }

    function executeItem(item) {
        if (!item || !item.action)
            return;
        const parts = item.action.split(":");
        if (parts[0] !== "run")
            return;
        const id = parts.slice(1).join(":");
        Quickshell.execDetached([cliPath, "action", "run", id]);
        if (typeof ToastService !== "undefined")
            ToastService.showInfo("Omivoid", item.name);
    }

    onTriggerChanged: {
        if (pluginService)
            pluginService.savePluginData("omivoidActions", "trigger", trigger);
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
                    console.info("[OmivoidActions] Loaded", root._actions.length, "actions from registry");
                } catch (e) {
                    console.error("[OmivoidActions] Failed to parse action list:", e);
                    root._actions = [];
                }
                root._loading = false;
                root.itemsChanged();
            }
        }

        onExited: exitCode => {
            if (exitCode !== 0) {
                console.warn("[OmivoidActions] action list failed, exit:", exitCode);
                root._loading = false;
                root.itemsChanged();
            }
        }
    }
}

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import qs.Common
import qs.Widgets
import qs.Modules.Plugins

// Ominty Keybindings — GKS cheat sheet (docs/14-gks-keyboard-grammar.md §22).
//
// A read-only, tabbed overlay: one tab per GKS domain, each listing
// `key → action`. Data comes from `ominty keybinds --json`, which walks the
// live Niri config tree (following `include` files, like NiriMod does) and
// merges the registry, DMS and universal convention rows — so the sheet
// cannot drift from what actually runs.
//
// Personalisation: rows that differ from the shipped defaults are marked
// (custom/change), a "Custom" toggle shows only those, and each row's
// `managed_by` says which editor owns it — click the ✎ to open that editor
// (DMS Settings → Keybinds for DMS rows, NiriMod for Niri rows).
//
// Opened with:  dms ipc call omintyKeybinds toggle   (bound to Super+Shift+S)

PluginComponent {
    id: root

    // ---- Data -----------------------------------------------------------
    property var _domains: []
    property var _bindings: []
    property int _tab: 0
    property string _query: ""
    property bool _customOnly: false

    readonly property string cliPath: Quickshell.env("OMINTY_CLI") || "ominty"

    // Accent for rows the user has changed (a safe local colour — the
    // external DMS Theme singleton may not expose a `warn` token).
    readonly property string customColor: "#f38ba8"

    readonly property int _customCount: root._bindings.filter(b => b.custom).length

    readonly property var _rows: {
        const domain = (root._tab >= 0 && root._tab < root._domains.length)
            ? root._domains[root._tab] : "";
        const q = root._query.trim().toLowerCase();
        return root._bindings.filter(b =>
            b.domain === domain &&
            (!root._customOnly || b.custom) &&
            (q === "" ||
                (b.key + " " + b.action + " " + b.source).toLowerCase().includes(q)));
    }

    // Display-layer only: short tab labels. GKS domain keys stay unchanged.
    readonly property var _domainLabels: ({
        "Application": "Apps",
        "Navigation": "Navigate",
        "Desktop": "Desktop",
        "Workspace topology": "Workspaces",
        "System": "System",
        "AI": "AI",
        "Projects": "Projects",
        "Hardware": "Hardware"
    })

    readonly property var _editorHint: ({
        "dms-settings": "DMS settings",
        "niri": "NiriMod",
        "ominty-registry": "ominty registry",
        "universal": "app convention",
        "function-keys": "your function map"
    })

    function _label(domain) {
        return root._domainLabels[domain] || domain;
    }

    function reload() {
        loadProc.running = false;
        loadProc.running = true;
    }

    Process {
        id: loadProc
        command: [root.cliPath, "keybinds", "--json"]
        running: false
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    const data = JSON.parse(text);
                    root._domains = data.domains || [];
                    root._bindings = data.bindings || [];
                } catch (e) {
                    console.warn("[omintyKeybinds] parse failed:", e);
                }
            }
        }
    }

    // One reusable process for "open the editor that manages this row".
    readonly property var _editCommands: ({
        "dms-settings": ["dms", "ipc", "call", "settings", "openWith", "keybinds"],
        "niri": ["nirimod"]
    })

    Process {
        id: editorProc
        command: ["true"]
        running: false
    }

    function openEditor(managedBy: string) {
        const cmd = root._editCommands[managedBy];
        if (!cmd) return;
        editorProc.running = false;
        editorProc.command = cmd;
        editorProc.running = true;
    }

    // ---- IPC ------------------------------------------------------------
    IpcHandler {
        target: "omintyKeybinds"

        function toggle(): string {
            overlay.visible = !overlay.visible;
            if (overlay.visible)
                root.reload();
            return overlay.visible ? "opened" : "closed";
        }
        function open(): string {
            overlay.visible = true;
            root.reload();
            return "opened";
        }
        function close(): string {
            overlay.visible = false;
            return "closed";
        }
    }

    // ---- Overlay --------------------------------------------------------
    PanelWindow {
        id: overlay
        visible: false
        color: "transparent"

        WlrLayershell.namespace: "ominty:keybinds"
        WlrLayershell.layer: WlrLayershell.Overlay
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive

        anchors {
            top: true
            bottom: true
            left: true
            right: true
        }

        FocusScope {
            id: content
            anchors.fill: parent
            focus: true

            Keys.onPressed: event => {
                if (event.key === Qt.Key_Escape) {
                    overlay.visible = false;
                    event.accepted = true;
                }
            }

            // Backdrop — click outside the panel to dismiss.
            Rectangle {
                anchors.fill: parent
                color: Qt.rgba(0, 0, 0, 0.55)
                MouseArea {
                    anchors.fill: parent
                    onClicked: overlay.visible = false
                }
            }

            Rectangle {
                id: panel
                anchors.centerIn: parent
                width: Math.min(1020, content.width - 80)
                height: Math.min(700, content.height - 80)
                radius: Theme.cornerRadius
                color: Theme.withAlpha(Theme.surface, 0.8)

                MouseArea {
                    anchors.fill: parent
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingL
                    spacing: Theme.spacingM

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingM

                        StyledText {
                            text: "Keybindings"
                            font.pixelSize: Theme.fontSizeLarge
                            font.weight: Font.Bold
                            color: Theme.surfaceText
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        StyledText {
                            text: root._customOnly
                                ? `Showing ${root._rows.length} custom binding(s)`
                                : (root._customCount > 0
                                    ? `${root._customCount} custom · reflect your edits`
                                    : "GKS · read-only")
                            color: Theme.surfaceVariantText
                        }
                    }

                    DankTabBar {
                        id: tabs
                        Layout.fillWidth: true
                        Layout.preferredHeight: 48
                        model: root._domains.map(d => ({
                            "text": root._label(d),
                            "icon": ""
                        }))
                        currentIndex: root._tab
                        onTabClicked: index => {
                            root._tab = index;
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingM

                        TextField {
                            id: search
                            Layout.fillWidth: true
                            placeholderText: "Filter bindings…"
                            color: "white"
                            placeholderTextColor: Theme.surfaceVariantText
                            leftPadding: Theme.spacingS
                            rightPadding: Theme.spacingS
                            background: Rectangle {
                                color: "transparent"
                                radius: 6
                                border.width: 1
                                border.color: Theme.outline
                            }
                            onTextChanged: root._query = text
                        }

                        Rectangle {
                            id: customToggle
                            Layout.preferredWidth: 96
                            Layout.preferredHeight: 34
                            radius: 6
                            color: root._customOnly ? Theme.primary : "transparent"
                            border.width: 1
                            border.color: root._customOnly ? Theme.primary : Theme.outline
                            visible: root._customCount > 0
                            opacity: enabled ? 1 : 0.45
                            enabled: root._customCount > 0

                            StyledText {
                                anchors.centerIn: parent
                                text: "Custom"
                                color: root._customOnly ? "black" : Theme.surfaceText
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: root._customOnly = !root._customOnly
                            }
                        }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: root._rows
                        spacing: 2

                        delegate: Rectangle {
                            id: row
                            required property var modelData
                            width: ListView.view.width
                            height: 30
                            color: "transparent"

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: Theme.spacingS
                                anchors.rightMargin: Theme.spacingS
                                spacing: Theme.spacingM

                                StyledText {
                                    text: row.modelData.key_label || row.modelData.key
                                    color: row.modelData.custom ? root.customColor : Theme.primary
                                    Layout.preferredWidth: 230
                                    elide: Text.ElideRight
                                }
                                StyledText {
                                    text: row.modelData.action_label || row.modelData.action
                                    color: Theme.surfaceText
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                StyledText {
                                    text: root._editorHint[row.modelData.managed_by]
                                        || row.modelData.managed_by
                                    color: Theme.surfaceVariantText
                                    Layout.preferredWidth: 130
                                    elide: Text.ElideRight
                                    visible: !row.modelData.custom
                                }
                                StyledText {
                                    text: row.modelData.custom
                                        ? (row.modelData.change === "remapped" ? "remapped" : "added")
                                        : ""
                                    color: root.customColor
                                    Layout.preferredWidth: 76
                                    visible: row.modelData.custom
                                }
                                StyledText {
                                    text: row.modelData.shadowed ? "shadowed" : ""
                                    color: Theme.surfaceVariantText
                                    Layout.preferredWidth: 64
                                }
                                // Open the editor that owns this binding.
                                Rectangle {
                                    width: 34; height: 22; radius: 4
                                    color: "transparent"
                                    border.width: 1
                                    border.color: Theme.outline
                                    visible: row.modelData.managed_by === "dms-settings"
                                        || row.modelData.managed_by === "niri"

                                    StyledText {
                                        anchors.centerIn: parent
                                        text: "\u270E"
                                        color: Theme.primary
                                        font.pixelSize: 12
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: root.openEditor(row.modelData.managed_by)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
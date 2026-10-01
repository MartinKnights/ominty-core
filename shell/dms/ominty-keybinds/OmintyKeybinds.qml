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
// `key → action`. Data comes from `ominty keybinds --json`, which merges
// the registry, Niri and DMS bindings, so the sheet cannot drift.
//
// Opened with:  dms ipc call omintyKeybinds toggle   (bound to Super+Shift+S)

PluginComponent {
    id: root

    // ---- Data -----------------------------------------------------------
    property var _domains: []
    property var _bindings: []
    property int _tab: 0
    property string _query: ""

    readonly property string cliPath: Quickshell.env("OMINTY_CLI") || "ominty"

    readonly property var _rows: {
        const domain = (root._tab >= 0 && root._tab < root._domains.length)
            ? root._domains[root._tab] : "";
        const q = root._query.trim().toLowerCase();
        return root._bindings.filter(b =>
            b.domain === domain &&
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
                width: Math.min(940, content.width - 80)
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
                            text: "GKS · read-only"
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
                                    color: Theme.primary
                                    Layout.preferredWidth: 260
                                    elide: Text.ElideRight
                                }
                                StyledText {
                                    text: row.modelData.action_label || row.modelData.action
                                    color: Theme.surfaceText
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                StyledText {
                                    text: row.modelData.source
                                          + (row.modelData.shadowed ? "  (shadowed)" : "")
                                    color: Theme.surfaceVariantText
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

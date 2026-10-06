// Ominty voice — dictation control panel (docs/ai/11-voice-integration.md, ADR-007).
//
// A focused Quickshell popup the user summons with Super+Alt+T. It is both
// the *indicator* (live input level while recording) and the *control*: a
// mouse toggle that starts and stops dictation. It is presentation only —
// it invokes the canonical `voice.dictate` action and never talks to an
// engine directly.
//
// The adapter publishes state to $XDG_RUNTIME_DIR/ominty-voice/status.json:
//   {"state": "idle"|"recording"|"transcribing"|"panel", "panel": bool}
//
// Run with:  quickshell -c ominty-voice

import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Services.Pipewire
import QtQuick

Scope {
    id: root

    readonly property string runtimeDir: Quickshell.env("XDG_RUNTIME_DIR") || "/tmp"
    readonly property string statusPath: root.runtimeDir + "/ominty-voice/status.json"

    property string state: "idle"     // idle | panel | recording | transcribing
    property bool panel: false
    readonly property bool active: root.state === "recording" || root.state === "transcribing"
    readonly property bool shown: root.panel || root.active

    // Trailing peaks for the level meter.
    property var history: []
    readonly property int historyLength: 26

    function refresh() {
        try {
            const data = JSON.parse(statusFile.text());
            root.state = data.state || "idle";
            root.panel = !!data.panel;
        } catch (e) {
            root.state = "idle";
            root.panel = false;
        }
    }

    function pushPeak(value) {
        const next = root.history.slice(1);
        next.push(value);
        root.history = next;
    }

    // Toggle dictation through the canonical action (Contract 3).
    function toggleDictation() {
        toggleProcess.exec(["ominty", "action", "run", "voice.dictate"]);
    }

    function closePanel() {
        panelProcess.exec(["ominty", "voice", "panel"]);
    }

    FileView {
        id: statusFile
        path: root.statusPath
        __preload: true   // so reload() performs an actual async re-read
        printErrors: false
        onLoaded: root.refresh()
    }

    // Poll the status file rather than relying on the watcher signal: it is
    // the same robust pattern the Piper indicator uses, and the watcher's
    // fileChanged signal proved unreliable on this stack.
    Timer {
        interval: 250
        running: true
        repeat: true
        onTriggered: statusFile.reload()
    }

    PwNodePeakMonitor {
        id: peakMonitor
        node: Pipewire.defaultAudioSource
        enabled: root.active
    }

    Timer {
        interval: 50
        running: root.active
        repeat: true
        onTriggered: root.pushPeak(peakMonitor.peak)
    }

    Process { id: toggleProcess; running: false }
    Process { id: panelProcess; running: false }

    PanelWindow {
        id: popup
        visible: root.shown

        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        WlrLayershell.namespace: "ominty:voice"

        anchors {
            top: true
            left: true
        }

        readonly property int panelW: 320
        readonly property int panelH: 60
        readonly property int marginTop: 12

        WlrLayershell.margins {
            top: popup.marginTop
            left: popup.screen ? Math.round((popup.screen.width - popup.panelW) / 2) : 0
        }

        implicitWidth: popup.panelW
        implicitHeight: popup.panelH
        color: "transparent"

        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: "#11111b"
            border.width: 1
            border.color: root.active ? "#f38ba8" : "#7f849c"

            // Start / Stop button (mouse toggle).
            Rectangle {
                id: toggle
                anchors.left: parent.left
                anchors.leftMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                width: 46
                height: 46
                radius: width / 2
                color: root.active ? "#f38ba8" : "#89b4fa"

                Text {
                    anchors.centerIn: parent
                    text: root.state === "recording" ? "\u25A0" : "\u25B6"   // stop / play
                    color: "#11111b"
                    font.pixelSize: 16
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.toggleDictation()
                }
            }

            // Level meter.
            Row {
                anchors.left: toggle.right
                anchors.leftMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                Repeater {
                    model: root.history

                    Rectangle {
                        required property var modelData
                        readonly property real lvl: Math.max(0.05, Math.min(1, modelData))
                        width: 3
                        height: 10 + 30 * lvl
                        radius: 1.5
                        anchors.verticalCenter: parent.verticalCenter
                        color: root.active ? "#f38ba8" : "#7f849c"
                    }
                }
            }

            Column {
                anchors.left: parent.left
                anchors.leftMargin: 18 + 46 + 12 + 3 * 26 + 14
                anchors.verticalCenter: parent.verticalCenter
                spacing: 1

                Text {
                    text: root.state === "recording" ? "Dictating…"
                        : root.state === "transcribing" ? "Transcribing…"
                        : root.panel ? "Dictation" : ""
                    color: "#cdd6f4"
                    font.pixelSize: 13
                    font.bold: root.active
                }
                Text {
                    text: "Super+Alt+D · click \u25B6 to start"
                    color: "#6c7086"
                    font.pixelSize: 10
                }
            }

            // Close (hide the panel).
            Rectangle {
                anchors.right: parent.right
                anchors.rightMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                width: 30
                height: 30
                radius: width / 2
                color: "transparent"

                Text {
                    anchors.centerIn: parent
                    text: "\u00D7"
                    color: "#6c7086"
                    font.pixelSize: 16
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.closePanel()
                }
            }
        }
    }
}
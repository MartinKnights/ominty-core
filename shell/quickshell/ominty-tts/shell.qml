// Ominty TTS document player control (docs/ai/11-voice-integration.md).
//
// Shown while a document is being spoken. It is presentation + control only:
// it polls the player's state file and sends next/prev/pause/resume/stop to
// the player's FIFO via `ominty tts ...`.
//
// State file: $XDG_RUNTIME_DIR/ominty-tts/state.json
//   {title, doc, total, current, status: synthesizing|playing|paused|done}

import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick

Scope {
    id: root

    readonly property string runtimeDir: Quickshell.env("XDG_RUNTIME_DIR") || "/tmp"
    readonly property string statePath: root.runtimeDir + "/ominty-tts/state.json"

    property string title: ""
    property int current: 0
    property int total: 0
    property string status: "none"
    readonly property bool active: root.status === "playing"
        || root.status === "paused" || root.status === "synthesizing"
    readonly property bool shown: root.active

    function refresh() {
        try {
            const data = JSON.parse(stateFile.text());
            root.title = data.title || "";
            root.current = data.current || 0;
            root.total = data.total || 0;
            root.status = data.status || "none";
        } catch (e) {
            root.status = "none";
        }
    }

    function ctrl(cmd) {
        ctrlProcess.exec(["ominty", "tts", cmd]);
    }

    FileView {
        id: stateFile
        path: root.statePath
        __preload: true
        printErrors: false
        onLoaded: root.refresh()
    }

    Timer {
        interval: 300
        running: true
        repeat: true
        onTriggered: stateFile.reload()
    }

    Process {
        id: ctrlProcess
        running: false
    }

    PanelWindow {
        id: popup
        visible: root.shown
        color: "transparent"

        implicitWidth: 360
        implicitHeight: 72
        width: 360
        height: 72

        anchors.top: true
        anchors.left: true
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.namespace: "ominty:tts"
        WlrLayershell.margins {
            top: 12
            left: popup.screen ? Math.round((popup.screen.width - 360) / 2) : 0
        }

        Rectangle {
            width: 360
            height: 72
            radius: 36
            color: "#181825"
            border.width: 1
            border.color: root.status === "playing" ? "#89b4fa" : "#313244"

            // Play / pause button (left).
            Rectangle {
                x: 8
                y: (parent.height - 46) / 2
                width: 46
                height: 46
                radius: 23
                color: root.status === "paused" ? "#89b4fa" : "#313244"

                Text {
                    anchors.centerIn: parent
                    text: root.status === "paused" ? "\u25B6" : "\u23F8"
                    color: root.status === "paused" ? "#11111b" : "#cdd6f4"
                    font.pixelSize: 15
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.ctrl(root.status === "paused" ? "resume" : "pause")
                }
            }

            // Document title + progress.
            Column {
                x: 62
                anchors.verticalCenter: parent.verticalCenter
                width: 360 - 62 - 112
                spacing: 3

                Text {
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideMiddle
                    text: root.title || "Document"
                    color: "#cdd6f4"
                    font.pixelSize: 12
                    font.bold: true
                }

                Text {
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    text: root.total > 0 ? (root.current + "/" + root.total) : ""
                    color: "#7f849c"
                    font.pixelSize: 10
                }
            }

            // Transport controls: previous | next | stop.
            Row {
                x: 360 - 8 - 26 * 3 - 6 * 2
                y: (parent.height - 26) / 2
                spacing: 6

                // prev
                Rectangle {
                    width: 26; height: 26; radius: 13; color: "#313244"
                    Text { anchors.centerIn: parent; text: "\u25C0"; color: "#cdd6f4"; font.pixelSize: 11 }
                    MouseArea { anchors.fill: parent; onClicked: root.ctrl("prev") }
                }
                // next
                Rectangle {
                    width: 26; height: 26; radius: 13; color: "#313244"
                    Text { anchors.centerIn: parent; text: "\u25B6"; color: "#cdd6f4"; font.pixelSize: 11 }
                    MouseArea { anchors.fill: parent; onClicked: root.ctrl("next") }
                }
                // stop
                Rectangle {
                    width: 26; height: 26; radius: 13; color: "#f38ba8"
                    Text { anchors.centerIn: parent; text: "\u25A0"; color: "#11111b"; font.pixelSize: 9 }
                    MouseArea { anchors.fill: parent; onClicked: root.ctrl("stop") }
                }
            }
        }
    }
}
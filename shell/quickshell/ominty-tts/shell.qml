// Ominty TTS document player control (docs/ai/11-voice-integration.md).
//
// Shown while a document is being read. Presentation + control only: it polls
// the player's state file and sends commands (next/prev/pause/resume/play/
// stop/quit) to the player FIFO via `ominty tts ...`; "open" opens the source
// document in its default application.
//
// State file: $XDG_RUNTIME_DIR/ominty-tts/state.json
//   {title, doc, total, current, status, ready, producing}

import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick

Scope {
    id: root

    readonly property string runtimeDir: Quickshell.env("XDG_RUNTIME_DIR") || "/tmp"
    readonly property string statePath: root.runtimeDir + "/ominty-tts/state.json"

    property string title: ""
    property string docPath: ""
    property int current: 0
    property int total: 0
    property int ready: 0
    property bool producing: false
    property string status: "none"
    property bool pulseOn: false

    readonly property bool active: root.status === "playing"
        || root.status === "paused" || root.status === "synthesizing"
        || root.status === "stopped" || root.status === "done"
    readonly property bool shown: root.active

    // The segment we're waiting on is still being synthesised.
    readonly property bool processing: root.producing && root.current > root.ready

    function refresh() {
        try {
            const data = JSON.parse(stateFile.text());
            root.title = data.title || "";
            root.docPath = data.doc || "";
            root.current = data.current || 0;
            root.total = data.total || 0;
            root.ready = data.ready || 0;
            root.producing = !!data.producing;
            root.status = data.status || "none";
        } catch (e) {
            root.status = "none";
        }
    }

    function ctrl(cmd) {
        ctrlProcess.exec(["ominty", "tts", cmd]);
    }

    function openDoc() {
        if (root.docPath) ctrlProcess.exec(["xdg-open", root.docPath]);
    }

    function playPause() {
        if (root.status === "playing") root.ctrl("pause");
        else root.ctrl("play");
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

    // Pulse the play button while a segment is still being generated.
    Timer {
        interval: 380
        running: root.processing
        repeat: true
        onTriggered: root.pulseOn = !root.pulseOn
    }

    Process {
        id: ctrlProcess
        running: false
    }

    PanelWindow {
        id: popup
        visible: root.shown
        color: "transparent"

        implicitWidth: 420
        implicitHeight: 72
        width: 420
        height: 72

        anchors.top: true
        anchors.left: true
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.namespace: "ominty:tts"
        WlrLayershell.margins {
            top: 12
            left: popup.screen ? Math.round((popup.screen.width - 420) / 2) : 0
        }

        Rectangle {
            width: 420
            height: 72
            radius: 36
            color: "#181825"
            border.width: 1
            border.color: root.status === "playing" ? "#89b4fa" : "#313244"

            // Play / pause button (left). Pulses orange while processing.
            Rectangle {
                id: playBtn
                x: 8
                y: (parent.height - 46) / 2
                width: 46
                height: 46
                radius: 23
                color: root.processing
                    ? (root.pulseOn ? "#f38ba8" : "#f38ba855")
                    : (root.status === "paused" || root.status === "stopped"
                       ? "#89b4fa" : "#313244")

                Text {
                    anchors.centerIn: parent
                    text: root.status === "playing" ? "\u23F8" : "\u25B6"
                    color: (root.processing || root.status === "paused"
                            || root.status === "stopped") ? "#11111b" : "#cdd6f4"
                    font.pixelSize: 16
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.playPause()
                }
            }

            // Centre: title above, transport row below.
            Column {
                x: 62
                anchors.verticalCenter: parent.verticalCenter
                width: 382 - 62 - 10
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

                Row {
                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: 8

                    // previous
                    Rectangle {
                        width: 24; height: 24; radius: 12; color: "#313244"
                        Text { anchors.centerIn: parent; text: "\u25C0"; color: "#cdd6f4"; font.pixelSize: 10 }
                        MouseArea { anchors.fill: parent; onClicked: root.ctrl("prev") }
                    }
                    // progress
                    Text {
                        width: 46
                        anchors.verticalCenter: parent.verticalCenter
                        horizontalAlignment: Text.AlignHCenter
                        text: root.total > 0 ? (root.current + "/" + root.total) : ""
                        color: root.processing ? "#f38ba8" : "#7f849c"
                        font.pixelSize: 11
                    }
                    // next
                    Rectangle {
                        width: 24; height: 24; radius: 12; color: "#313244"
                        Text { anchors.centerIn: parent; text: "\u25B6"; color: "#cdd6f4"; font.pixelSize: 10 }
                        MouseArea { anchors.fill: parent; onClicked: root.ctrl("next") }
                    }
                    // stop
                    Rectangle {
                        width: 24; height: 24; radius: 12; color: "#f38ba8"
                        Text { anchors.centerIn: parent; text: "\u25A0"; color: "#11111b"; font.pixelSize: 8 }
                        MouseArea { anchors.fill: parent; onClicked: root.ctrl("stop") }
                    }
                }
            }

            // Right: open in default app, and close (quit + hide).
            Column {
                x: 420 - 8 - 30
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6

                Rectangle {
                    width: 30; height: 30; radius: 15; color: "#313244"
                    Text { anchors.centerIn: parent; text: "\u29C9"; color: "#cdd6f4"; font.pixelSize: 12 }
                    MouseArea { anchors.fill: parent; onClicked: root.openDoc() }
                }
                Rectangle {
                    width: 30; height: 30; radius: 15; color: "#45475a"
                    Text { anchors.centerIn: parent; text: "\u00D7"; color: "#cdd6f4"; font.pixelSize: 14 }
                    MouseArea { anchors.fill: parent; onClicked: root.ctrl("quit") }
                }
            }
        }
    }
}
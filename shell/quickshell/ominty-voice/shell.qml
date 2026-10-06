// Ominty voice — recording indicator (docs/ai/11-voice-integration.md, ADR-007).
//
// A focused Quickshell popup shown while dictation is recording, with a live
// input level driven by the Pipewire peak monitor. It is *presentation only*:
// it owns no dictation state and invokes no engine. The adapter publishes the
// recording state to $XDG_RUNTIME_DIR/ominty-voice/status.json; this component
// watches that file and shows or hides the popup.
//
// Run with:  quickshell -p <this directory>

import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Services.Pipewire
import QtQuick

Scope {
    id: root

    readonly property string runtimeDir: Quickshell.env("XDG_RUNTIME_DIR") || "/tmp"
    readonly property string statusPath: root.runtimeDir + "/ominty-voice/status.json"

    // "idle" | "recording" | "transcribing"
    property string state: "idle"
    readonly property bool active: root.state === "recording" || root.state === "transcribing"

    // A short trailing history of peaks, for a simple waveform.
    property var history: []
    readonly property int historyLength: 28

    function refresh() {
        try {
            root.state = JSON.parse(statusFile.text()).state || "idle";
        } catch (e) {
            root.state = "idle";
        }
    }

    function pushPeak(value) {
        const next = root.history.slice(1);
        next.push(value);
        root.history = next;
    }

    FileView {
        id: statusFile
        path: root.statusPath
        watchChanges: true
        printErrors: false
        onLoaded: root.refresh()
        onFileChanged: root.refresh()
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

    PanelWindow {
        id: popup
        visible: root.active

        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        WlrLayershell.namespace: "ominty:voice"

        anchors {
            top: true
            left: true
        }

        readonly property int popupWidth: 260
        readonly property int popupHeight: 64
        readonly property int popupMargin: popup.screen
            ? Math.round((popup.screen.width - popup.popupWidth) / 2) : 0

        WlrLayershell.margins {
            top: 12
            left: popup.popupMargin
        }

        implicitWidth: popup.popupWidth
        implicitHeight: popup.popupHeight
        color: "transparent"

        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: "#1e1e2e"
            border.width: 1
            border.color: root.state === "recording" ? "#f38ba8" : "#89b4fa"

            Row {
                id: bars
                anchors.left: parent.left
                anchors.leftMargin: 18
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                Repeater {
                    model: root.history

                    Rectangle {
                        required property var modelData
                        width: 3
                        height: 4 + 32 * Math.max(0.04, Math.min(1, modelData))
                        radius: 1.5
                        anchors.verticalCenter: parent.verticalCenter
                        color: root.state === "recording" ? "#f38ba8" : "#89b4fa"
                    }
                }
            }

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 18 + bars.width + 14
                anchors.verticalCenter: parent.verticalCenter
                text: root.state === "transcribing" ? "Transcribing…" : "Listening…"
                color: "#cdd6f4"
                font.pixelSize: 13
            }
        }
    }
}

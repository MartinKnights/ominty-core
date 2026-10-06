import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Services.Pipewire
import QtQuick

Scope {
    id: root

    readonly property string runtimeDir: Quickshell.env("XDG_RUNTIME_DIR") || "/tmp"
    readonly property string statusPath: root.runtimeDir + "/ominty-voice/status.json"

    property string state: "idle"
    property bool panel: false
    readonly property bool active: root.state === "recording" || root.state === "transcribing"
    readonly property bool shown: root.panel || root.active

    readonly property int panelW: 300
    readonly property int panelH: 56

    property var history: []

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

    function toggleDictation() {
        toggleProcess.exec(["ominty", "action", "run", "voice.dictate"]);
    }

    function closePanel() {
        panelProcess.exec(["ominty", "voice", "panel"]);
    }

    FileView {
        id: statusFile
        path: root.statusPath
        __preload: true
        printErrors: false
        onLoaded: root.refresh()
    }

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

    Process {
        id: toggleProcess
        running: false
    }

    Process {
        id: panelProcess
        running: false
    }

    PanelWindow {
        id: popup
        visible: root.shown
        color: "transparent"

        implicitWidth: root.panelW
        implicitHeight: root.panelH
        width: root.panelW
        height: root.panelH

        anchors.top: true
        anchors.left: true
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        WlrLayershell.exclusiveZone: -1
        WlrLayershell.namespace: "ominty:voice"
        WlrLayershell.margins {
            top: 12
            left: popup.screen ? Math.round((popup.screen.width - root.panelW) / 2) : 0
        }

        // One fixed-size clickable pill: click toggles dictation.
        // A fixed 300x56 pill; children are positioned with absolute offsets
        // so the layout cannot grow to the screen size.
        Rectangle {
            width: root.panelW
            height: root.panelH
            radius: root.panelH / 2
            color: "#181825"
            border.width: 1
            border.color: root.active ? "#f38ba8" : "#313244"

            // Toggle button (left).
            Rectangle {
                x: 8
                y: (parent.height - 44) / 2
                width: 44
                height: 44
                radius: 22
                color: root.active ? "#f38ba8" : "#89b4fa"

                Text {
                    anchors.centerIn: parent
                    text: root.active ? "\u25A0" : "\u25B6"
                    color: "#11111b"
                    font.pixelSize: 15
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.toggleDictation()
                }
            }

            // Level bars + state label.
            Row {
                x: 62
                y: (parent.height - 24) / 2
                spacing: 8

                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: root.active
                    spacing: 3
                    anchors.verticalCenterOffset: 0

                    Repeater {
                        model: root.history
                        Rectangle {
                            required property var modelData
                            width: 3
                            height: 8 + 28 * Math.max(0.05, Math.min(1, modelData))
                            radius: 1.5
                            anchors.verticalCenter: parent.verticalCenter
                            color: "#f38ba8"
                        }
                    }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.state === "recording" ? "Dictating\u2026"
                        : root.state === "transcribing" ? "Transcribing\u2026"
                        : "Dictation"
                    color: "#cdd6f4"
                    font.pixelSize: 13
                }
            }

            // Close (hide the panel).
            Rectangle {
                x: parent.width - 30
                y: (parent.height - 24) / 2
                width: 24
                height: 24
                radius: 12
                color: "transparent"

                Text {
                    anchors.centerIn: parent
                    text: "\u00D7"
                    color: "#6c7086"
                    font.pixelSize: 15
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.closePanel()
                }
            }
        }

        Component.onCompleted: {
            console.log("ominty-voice size=" + popup.width + "x" + popup.height
                + " screen=" + (popup.screen ? popup.screen.width : "none"));
        }
    }
}
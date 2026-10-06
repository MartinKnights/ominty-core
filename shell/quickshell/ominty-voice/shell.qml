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
    readonly property int panelH: 96

    // Live input level (smoothed) and a slowly advancing tick for the
    // equalizer's gentle undulation.
    property real level: 0
    property real tick: 0

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
        interval: 40
        running: root.active
        repeat: true
        onTriggered: {
            // smooth the peak a little to avoid flicker
            root.level = Math.max(root.level * 0.72, peakMonitor.peak);
            root.tick += 1;
        }
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

        Rectangle {
            width: root.panelW
            height: root.panelH
            radius: root.panelH / 2
            color: "#181825"
            border.width: 1
            border.color: root.active ? "#f38ba8" : "#313244"

            // Toggle button (left).
            Rectangle {
                x: 10
                y: (parent.height - 48) / 2
                width: 48
                height: 48
                radius: 24
                color: root.active ? "#f38ba8" : "#89b4fa"

                Text {
                    anchors.centerIn: parent
                    text: root.active ? "\u25A0" : "\u25B6"
                    color: "#11111b"
                    font.pixelSize: 16
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: root.toggleDictation()
                }
            }

            // Centre: state label ABOVE a stationary segmented equalizer.
            Column {
                x: 68
                anchors.verticalCenter: parent.verticalCenter
                width: root.panelW - 68 - 34
                spacing: 4

                Text {
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    text: root.state === "recording" ? "Dictating\u2026"
                        : root.state === "transcribing" ? "Transcribing\u2026"
                        : "Dictation"
                    color: "#cdd6f4"
                    font.pixelSize: 11
                }

                // Equalizer: 21 fixed lanes; each bar is centred vertically in
                // its lane, so the equalizer is symmetric around the middle.
                Item {
                    width: parent.width
                    height: 48
                    visible: root.active

                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 3

                        Repeater {
                            model: 21

                            Item {
                                id: lane
                                width: 6
                                height: 44
                                readonly property real env: Math.pow(Math.sin(Math.PI * index / 20), 1.3)
                                readonly property real wob: Math.sin(root.tick * 0.22 + index * 1.1)
                                readonly property real lvl: Math.max(0.03, Math.min(1, root.level))
                                readonly property real barH: Math.min(42, 3 + Math.round(38 * env * lvl * (1 + 0.22 * wob)))

                                Rectangle {
                                    width: parent.width
                                    height: lane.barH
                                    radius: 2
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    color: "#f38ba8"
                                }
                            }
                        }
                    }
                }
            }

            // Close (hide the panel).
            Rectangle {
                x: parent.width - 32
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
    }
}
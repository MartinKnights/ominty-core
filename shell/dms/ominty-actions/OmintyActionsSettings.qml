// Ominty Actions — DMS launcher plugin settings.
//
// Configuration for the Ominty Action Registry bridge. All values are
// stored by DMS via PluginSettings; the launcher component reads the same
// keys through pluginService.loadPluginData(...).

import QtQuick
import qs.Common
import qs.Services
import qs.Widgets
import qs.Modules.Plugins

PluginSettings {
    id: root
    pluginId: "omintyActions"

    StyledText {
        width: parent.width
        text: I18n.tr("Ominty Actions")
        font.pixelSize: Theme.fontSizeLarge
        font.weight: Font.Bold
        color: Theme.surfaceText
    }

    StyledText {
        width: parent.width
        text: I18n.tr("Search and run Ominty action registry entries from the DMS launcher.")
        font.pixelSize: Theme.fontSizeSmall
        color: Theme.surfaceVariantText
        wrapMode: Text.WordWrap
    }

    StyledRect {
        width: parent.width
        height: activationColumn.implicitHeight + Theme.spacingL * 2
        radius: Theme.cornerRadius
        color: Theme.surfaceContainerHigh

        Column {
            id: activationColumn
            anchors.fill: parent
            anchors.margins: Theme.spacingL
            spacing: Theme.spacingM

            StyledText {
                text: I18n.tr("Activation")
                font.pixelSize: Theme.fontSizeMedium
                font.weight: Font.Medium
                color: Theme.surfaceText
            }

            ToggleSetting {
                id: noTriggerToggle
                settingKey: "noTrigger"
                label: I18n.tr("Always Active")
                description: value ? I18n.tr("Ominty actions merge into all searches (universal palette)") : I18n.tr("Use a trigger prefix to activate")
                defaultValue: true
                onValueChanged: {
                    if (!isInitialized)
                        return;
                    if (value)
                        root.saveValue("trigger", "");
                    else
                        root.saveValue("trigger", triggerSetting.value || "!");
                }
            }

            StringSetting {
                id: triggerSetting
                visible: !noTriggerToggle.value
                settingKey: "trigger"
                label: I18n.tr("Trigger Prefix")
                description: I18n.tr("Type this prefix to search Ominty actions")
                placeholder: "!"
                defaultValue: "!"
            }
        }
    }

    StyledRect {
        width: parent.width
        height: connectionColumn.implicitHeight + Theme.spacingL * 2
        radius: Theme.cornerRadius
        color: Theme.surfaceContainerHigh

        Column {
            id: connectionColumn
            anchors.fill: parent
            anchors.margins: Theme.spacingL
            spacing: Theme.spacingM

            StyledText {
                text: I18n.tr("Registry Connection")
                font.pixelSize: Theme.fontSizeMedium
                font.weight: Font.Medium
                color: Theme.surfaceText
            }

            StringSetting {
                id: cliSetting
                settingKey: "cliPath"
                label: I18n.tr("Ominty CLI Path")
                description: I18n.tr("Executable used to read the registry and run actions")
                placeholder: "ominty"
                defaultValue: "ominty"
            }

            SelectionSetting {
                id: filterSetting
                settingKey: "filterMode"
                label: I18n.tr("Action Filter")
                description: I18n.tr("Which registry actions to surface")
                options: [
                    {label: I18n.tr("All actions"), value: "all"},
                    {label: I18n.tr("Discoverable (Super+K)"), value: "discoverable"},
                    {label: I18n.tr("Palette (Super+Space)"), value: "palette"}
                ]
                defaultValue: "all"
            }
        }
    }

    StyledRect {
        width: parent.width
        height: infoColumn.implicitHeight + Theme.spacingL * 2
        radius: Theme.cornerRadius
        color: Theme.surface

        Column {
            id: infoColumn
            anchors.fill: parent
            anchors.margins: Theme.spacingL
            spacing: Theme.spacingM

            Row {
                spacing: Theme.spacingM

                DankIcon {
                    name: "info"
                    size: Theme.iconSize
                    color: Theme.primary
                    anchors.verticalCenter: parent.verticalCenter
                }

                StyledText {
                    text: I18n.tr("Usage")
                    font.pixelSize: Theme.fontSizeMedium
                    font.weight: Font.Medium
                    color: Theme.surfaceText
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            StyledText {
                text: I18n.tr("Ominty actions merge into the launcher alongside applications (Super+Space). Type \"!!\" to open the interaction explorer (Super+K) showing every action and its canonical keybinding. Selecting an item runs it via `ominty action run <id>`.\n\nBindings are shown from the Action Registry, which remains authoritative.")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.surfaceVariantText
                wrapMode: Text.WordWrap
                width: parent.width
                lineHeight: 1.4
            }
        }
    }
}

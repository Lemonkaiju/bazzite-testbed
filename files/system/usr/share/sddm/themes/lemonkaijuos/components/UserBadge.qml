// UserBadge.qml
// Avatar circle + greeting name

import QtQuick 2.15
import QtQuick.Layouts 1.15

ColumnLayout {
    id: root

    property string realName: ""
    property string avatarPath: ""

    spacing: 14

    // Avatar
    Rectangle {
        Layout.alignment: Qt.AlignHCenter
        width: 88
        height: 88
        radius: 44
        color: "#0affffff"
        border.color: "#3daee9"
        border.width: 2
        clip: true

        Image {
            anchors.fill: parent
            source: root.avatarPath
            fillMode: Image.PreserveAspectCrop
            visible: root.avatarPath !== ""
        }

        // Fallback initials if no avatar
        Text {
            anchors.centerIn: parent
            visible: root.avatarPath === ""
            text: root.realName.length > 0 ? root.realName[0].toUpperCase() : "?"
            font.pixelSize: 34
            font.weight: Font.Light
            color: "#3daee9"
        }
    }

    // Greeting
    Text {
        Layout.alignment: Qt.AlignHCenter
        text: root.realName.length > 0 ? "Welcome back, " + root.realName : "Welcome back"
        color: "#eff0f1"
        font.pixelSize: 18
        font.weight: Font.Medium
    }
}

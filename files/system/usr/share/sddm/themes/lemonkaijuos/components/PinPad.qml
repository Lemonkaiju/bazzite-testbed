// PinPad.qml
// 3x4 numpad: 1-9, then backspace / 0 / confirm

import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    signal digitPressed(string digit)
    signal deletePressed()
    signal confirmPressed()

    implicitWidth: grid.implicitWidth
    implicitHeight: grid.implicitHeight

    readonly property var layout: [
        "1", "2", "3",
        "4", "5", "6",
        "7", "8", "9",
        "⌫", "0", "✓"
    ]

    GridLayout {
        id: grid
        columns: 3
        rowSpacing: 10
        columnSpacing: 10

        Repeater {
            model: root.layout

            Rectangle {
                id: btn

                property string label: modelData
                property bool isDelete:  label === "⌫"
                property bool isConfirm: label === "✓"

                implicitWidth:  72
                implicitHeight: 72
                radius: 10

                color: ma.pressed      ? "#3daee9"
                     : ma.containsMouse ? "#252c3a"
                     : "#1e2330"

                border.color: isConfirm ? "#3daee9"
                            : isDelete  ? "#6b7a8a"
                            : "#1fffffff"
                border.width: isConfirm ? 2 : 1

                Behavior on color { ColorAnimation { duration: 80 } }

                Text {
                    anchors.centerIn: parent
                    text: btn.label
                    font.pixelSize: btn.isDelete || btn.isConfirm ? 22 : 26
                    font.weight: Font.Medium
                    color: btn.isConfirm ? "#3daee9"
                         : btn.isDelete  ? "#9aaab4"
                         : "#eff0f1"
                }

                MouseArea {
                    id: ma
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (btn.isDelete)       root.deletePressed()
                        else if (btn.isConfirm) root.confirmPressed()
                        else                    root.digitPressed(btn.label)
                    }
                }
            }
        }
    }

    // Keyboard support
    Keys.onPressed: function(event) {
        if (event.key >= Qt.Key_0 && event.key <= Qt.Key_9) {
            root.digitPressed(String.fromCharCode(event.key))
            event.accepted = true
        } else if (event.key === Qt.Key_Backspace) {
            root.deletePressed()
            event.accepted = true
        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            root.confirmPressed()
            event.accepted = true
        }
    }
}

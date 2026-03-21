// PinDisplay.qml
// Renders N dots that fill with blue as digits are entered.
// Shakes on failed auth.

import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property int pinLength: 6
    property string pin: ""
    readonly property int count: pin.length

    signal submitted(string pin)

    width: row.implicitWidth
    height: row.implicitHeight

    function addDigit(d) {
        if (pin.length < pinLength) {
            pin += d
            if (pin.length === pinLength) {
                submitted(pin)
            }
        }
    }

    function removeDigit() {
        if (pin.length > 0)
            pin = pin.slice(0, -1)
    }

    function clear() {
        pin = ""
    }

    function shake() {
        shakeAnim.restart()
    }

    SequentialAnimation {
        id: shakeAnim
        loops: 1
        PropertyAnimation { target: root; property: "x"; to: root.x - 10; duration: 40 }
        PropertyAnimation { target: root; property: "x"; to: root.x + 10; duration: 40 }
        PropertyAnimation { target: root; property: "x"; to: root.x - 8;  duration: 40 }
        PropertyAnimation { target: root; property: "x"; to: root.x + 8;  duration: 40 }
        PropertyAnimation { target: root; property: "x"; to: root.x - 4;  duration: 40 }
        PropertyAnimation { target: root; property: "x"; to: root.x;      duration: 40 }
    }

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 14

        Repeater {
            model: root.pinLength

            Rectangle {
                width: 14
                height: 14
                radius: 7
                color: index < root.count ? "#3daee9" : "transparent"
                border.color: index < root.count ? "#3daee9" : "#40ffffff"
                border.width: 2

                Behavior on color {
                    ColorAnimation { duration: 80 }
                }
            }
        }
    }
}

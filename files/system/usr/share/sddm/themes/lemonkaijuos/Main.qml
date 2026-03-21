// LemonKaijuOS SDDM Theme — Main.qml
// Dark PIN-pad login screen for family-friendly secure boot.
//
// Auth flow (PIN mode):
//   PinDisplay auto-submits at 6 digits → sddm.login(user, pin, session)
//   sddm.loginFailed → shake dots, clear, show error message
//
// Auth flow (password mode):
//   User types password, presses Enter or ✓ button → sddm.login(user, pass, session)
//
// Toggle: "Use password instead" / "Use PIN instead" link under the numpad.
// Background: user wallpaper blurred + dark overlay (frosted glass effect).
// PAM must be configured to accept the PIN as the password.

import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15 as QQC2
import Qt5Compat.GraphicalEffects

import "components"

Item {
    id: root
    width:  1920
    height: 1080

    // ── State ────────────────────────────────────────────────────────────────

    property bool pinMode: true

    // ── Helpers ─────────────────────────────────────────────────────────────

    function currentUser() {
        return userModel.data(userModel.index(0, 0), Qt.UserRole + 1) ?? ""
    }

    function currentRealName() {
        return userModel.data(userModel.index(0, 0), Qt.UserRole + 2) ?? ""
    }

    function currentAvatar() {
        return userModel.data(userModel.index(0, 0), Qt.UserRole + 4) ?? ""
    }

    function currentSession() {
        for (var i = 0; i < sessionModel.rowCount(); i++) {
            var name = sessionModel.data(sessionModel.index(i, 0), Qt.UserRole + 1) ?? ""
            if (name.toLowerCase().includes("wayland")) return name
        }
        return sessionModel.data(sessionModel.index(0, 0), Qt.UserRole + 1) ?? ""
    }

    function doLogin(secret) {
        statusText.text = ""
        sddm.login(currentUser(), secret, currentSession())
    }

    function switchMode(wantPin) {
        pinMode = wantPin
        pinDisplay.clear()
        passwordField.text = ""
        statusText.text = pinMode ? "Enter your PIN" : "Enter your password"
        statusText.color = "#484f58"
        if (pinMode)
            pinPad.forceActiveFocus()
        else
            passwordField.forceActiveFocus()
    }

    // ── SDDM signals ─────────────────────────────────────────────────────────

    Connections {
        target: sddm

        function onLoginFailed() {
            if (pinMode) {
                pinDisplay.shake()
                pinDisplay.clear()
            } else {
                passwordField.text = ""
                passwordField.forceActiveFocus()
            }
            statusText.text = "Incorrect " + (pinMode ? "PIN" : "password") + " — try again"
            statusText.color = "#f85149"
        }
    }

    // ── Background — blurred wallpaper + frosted glass overlay ──────────────

    Image {
        id: wallpaperSource
        anchors.fill: parent
        source: config.background !== "" ? config.background : "assets/background.png"
        fillMode: Image.PreserveAspectCrop
        visible: false
        cache: true
    }

    FastBlur {
        anchors.fill: parent
        source: wallpaperSource
        radius: 56
    }

    Rectangle {
        anchors.fill: parent
        color: "#b2000000"
    }

    // ── Clock (top-right) ────────────────────────────────────────────────────

    Column {
        anchors {
            top: parent.top
            right: parent.right
            margins: 32
        }
        spacing: 4

        Text {
            id: clockTime
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#8b949e"
            font.pixelSize: 48
            font.weight: Font.Light
        }

        Text {
            id: clockDate
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#484f58"
            font.pixelSize: 16
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            triggeredOnStart: true
            onTriggered: {
                var now = new Date()
                clockTime.text = Qt.formatTime(now, "hh:mm")
                clockDate.text = Qt.formatDate(now, "dddd, d MMMM")
            }
        }
    }

    // ── Centre card ──────────────────────────────────────────────────────────

    Rectangle {
        id: card
        anchors.centerIn: parent
        width: 320
        height: col.implicitHeight + 64
        radius: 20
        color: "#161b22"
        border.color: "#30363d"
        border.width: 1

        layer.enabled: true
        layer.effect: DropShadow {
            radius: 32
            samples: 33
            color: "#263fb950"
            transparentBorder: true
        }

        ColumnLayout {
            id: col
            anchors {
                top: parent.top
                left: parent.left
                right: parent.right
                margins: 32
            }
            spacing: 28

            // User avatar + greeting
            UserBadge {
                Layout.alignment: Qt.AlignHCenter
                realName: currentRealName()
                avatarPath: currentAvatar()
            }

            // PIN dots (PIN mode only)
            PinDisplay {
                id: pinDisplay
                Layout.alignment: Qt.AlignHCenter
                visible: pinMode
                pinLength: 6
                onSubmitted: function(pin) { doLogin(pin) }
            }

            // Password field (password mode only)
            QQC2.TextField {
                id: passwordField
                Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: true
                visible: !pinMode
                echoMode: TextInput.Password
                placeholderText: "Password"
                color: "#e6edf3"
                font.pixelSize: 16
                horizontalAlignment: TextInput.AlignHCenter

                background: Rectangle {
                    color: "#21262d"
                    border.color: passwordField.activeFocus ? "#3fb950" : "#30363d"
                    border.width: 1
                    radius: 8
                }

                Keys.onReturnPressed: { if (text.length > 0) doLogin(text) }
                Keys.onEnterPressed:  { if (text.length > 0) doLogin(text) }
            }

            // Status / error message
            Text {
                id: statusText
                Layout.alignment: Qt.AlignHCenter
                text: "Enter your PIN"
                color: "#484f58"
                font.pixelSize: 13
            }

            // PIN pad (PIN mode only)
            PinPad {
                id: pinPad
                Layout.alignment: Qt.AlignHCenter
                visible: pinMode
                focus: pinMode

                onDigitPressed:   function(d) { pinDisplay.addDigit(d) }
                onDeletePressed:  pinDisplay.removeDigit()
                onConfirmPressed: {
                    if (pinDisplay.count > 0) doLogin(pinDisplay.pin)
                }
            }

            // Password confirm button (password mode only)
            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                visible: !pinMode
                width: 72
                height: 44
                radius: 10
                color: pwBtn.pressed ? "#3fb950" : pwBtn.containsMouse ? "#21262d" : "#161b22"
                border.color: "#3fb950"
                border.width: 2

                Behavior on color { ColorAnimation { duration: 80 } }

                Text {
                    anchors.centerIn: parent
                    text: "Sign in"
                    color: "#3fb950"
                    font.pixelSize: 13
                    font.weight: Font.Medium
                }

                MouseArea {
                    id: pwBtn
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: { if (passwordField.text.length > 0) doLogin(passwordField.text) }
                }
            }

            // Mode toggle link
            Text {
                id: modeToggle
                Layout.alignment: Qt.AlignHCenter
                text: pinMode ? "Use password instead" : "Use PIN instead"
                color: "#484f58"
                font.pixelSize: 12

                Behavior on color { ColorAnimation { duration: 80 } }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: switchMode(!pinMode)
                    onContainsMouseChanged: modeToggle.color = containsMouse ? "#8b949e" : "#484f58"
                }
            }

            // Branding
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "LemonKaijuOS"
                color: "#3fb950"
                font.pixelSize: 11
                font.letterSpacing: 2
                opacity: 0.6
            }

            Item { height: 0 }  // bottom padding spacer
        }
    }
}

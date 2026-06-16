import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: window
    visible: true
    width: 360
    height: 640
    title: "Pixel Refine Mobile"

    // Properti Global untuk Workspace
    property string activeToolType: "Denoising"
    property int selectedImageCount: 0

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: welcomeView
    }

    // =========================================================================
    // 1. WELCOME VIEW / SPLASH SCREEN
    // =========================================================================
    Component {
        id: welcomeView
        Item {
            // Dihapus anchors.fill: parent untuk menghindari konflik dengan StackView

            Rectangle {
                anchors.fill: parent
                color: genericTheme.bgSecondary  // Mencontek warna dari Python

                Column {
                    anchors.centerIn: parent
                    spacing: 20
                    width: parent.width * 0.8

                    Rectangle {
                        width: 120
                        height: 120
                        radius: 60
                        color: "#E5E7EB"
                        anchors.horizontalCenter: parent.horizontalCenter

                        Text {
                            text: "📷"
                            font.pixelSize: 64
                            anchors.centerIn: parent
                        }
                    }

                    Text {
                        text: "PIXEL REFINE"
                        font.pixelSize: 28
                        font.bold: true
                        color: genericTheme.primary  // Mencontek warna primer hijau dari Python
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Computational\nPhotography Tools"
                        font.pixelSize: 16
                        color: genericTheme.textSecondary
                        horizontalAlignment: Text.AlignHCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Rectangle {
                        width: parent.width
                        height: 6
                        color: "#E5E7EB"
                        radius: 3
                        anchors.horizontalCenter: parent.horizontalCenter

                        Rectangle {
                            height: parent.height
                            width: parent.width * (appBridge.loadingProgress / 100)
                            color: genericTheme.primary
                            radius: 3
                            Behavior on width { NumberAnimation { duration: 80 } }
                        }
                    }

                    Text {
                        text: appBridge.loadingProgress < 100 ? "Loading..." : "Starting..."
                        font.pixelSize: 12
                        color: genericTheme.textMuted
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            Connections {
                target: appBridge
                function onLoadingProgressChanged(progress) {
                    if (progress >= 100) {
                        stackView.replace(homeView)
                    }
                }
            }
        }
    }

    // =========================================================================
    // 2. HOME VIEW (MENU UTAMA)
    // =========================================================================
    Component {
        id: homeView
        Item {
            // Dihapus anchors.fill: parent untuk menghindari konflik dengan StackView

            Rectangle {
                anchors.fill: parent
                color: genericTheme.bgSecondary

                Rectangle {
                    id: appBar
                    width: parent.width
                    height: 56
                    color: genericTheme.bgSecondary

                    Text {
                        text: "Pixel Refine"
                        font.pixelSize: 20
                        font.bold: true
                        color: genericTheme.textPrimary
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                    }
                }

                ScrollView {
                    anchors.top: appBar.bottom
                    anchors.bottom: parent.bottom
                    width: parent.width
                    clip: true

                    Column {
                        width: parent.width
                        spacing: 16
                        padding: 16

                        // Card: Denoising
                        Rectangle {
                            width: parent.width - 32
                            height: 110
                            color: genericTheme.bgPrimary
                            radius: genericTheme.radiusLg
                            border.color: genericTheme.borderColor
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 8

                                Text {
                                    text: "Denoising"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: genericTheme.textPrimary
                                }

                                Text {
                                    text: "Analyze burst images to remove noise and enhance detail"
                                    font.pixelSize: 13
                                    color: genericTheme.textSecondary
                                    wrapMode: Text.WordWrap
                                    width: parent.width
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                property bool isPressed: false
                                onPressed: isPressed = true
                                onReleased: {
                                    isPressed = false
                                    window.activeToolType = "Denoising"
                                    appBridge.openTool("Denoising")
                                    stackView.push(workspaceView)
                                }
                                onCanceled: isPressed = false
                                
                                Rectangle {
                                    anchors.fill: parent
                                    color: genericTheme.primary
                                    opacity: parent.isPressed ? 0.12 : 0
                                    radius: genericTheme.radiusLg
                                    Behavior on opacity { NumberAnimation { duration: 100 } }
                                }
                            }
                        }

                        // Card: HDR Stack
                        Rectangle {
                            width: parent.width - 32
                            height: 110
                            color: genericTheme.bgPrimary
                            radius: genericTheme.radiusLg
                            border.color: genericTheme.borderColor
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 8

                                Text {
                                    text: "HDR Stack"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: genericTheme.textPrimary
                                }

                                Text {
                                    text: "Combine multiple with different exposure settings"
                                    font.pixelSize: 13
                                    color: genericTheme.textSecondary
                                    wrapMode: Text.WordWrap
                                    width: parent.width
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                property bool isPressed: false
                                onPressed: isPressed = true
                                onReleased: {
                                    isPressed = false
                                    window.activeToolType = "HDR Stack"
                                    appBridge.openTool("HDR Stack")
                                    stackView.push(workspaceView)
                                }
                                onCanceled: isPressed = false

                                Rectangle {
                                    anchors.fill: parent
                                    color: genericTheme.primary
                                    opacity: parent.isPressed ? 0.12 : 0
                                    radius: genericTheme.radiusLg
                                    Behavior on opacity { NumberAnimation { duration: 100 } }
                                }
                            }
                        }

                        // Card: Panorama
                        Rectangle {
                            width: parent.width - 32
                            height: 110
                            color: genericTheme.bgPrimary
                            radius: genericTheme.radiusLg
                            border.color: genericTheme.borderColor
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 8

                                Text {
                                    text: "Panorama"
                                    font.pixelSize: 18
                                    font.bold: true
                                    color: genericTheme.textPrimary
                                }

                                Text {
                                    text: "Stitch multiple images to create a wide high-resolution view"
                                    font.pixelSize: 13
                                    color: genericTheme.textSecondary
                                    wrapMode: Text.WordWrap
                                    width: parent.width
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                property bool isPressed: false
                                onPressed: isPressed = true
                                onReleased: {
                                    isPressed = false
                                    window.activeToolType = "Panorama"
                                    appBridge.openTool("Panorama")
                                    stackView.push(workspaceView)
                                }
                                onCanceled: isPressed = false

                                Rectangle {
                                    anchors.fill: parent
                                    color: genericTheme.primary
                                    opacity: parent.isPressed ? 0.12 : 0
                                    radius: genericTheme.radiusLg
                                    Behavior on opacity { NumberAnimation { duration: 100 } }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // =========================================================================
    // 3. WORKSPACE / PROJECT VIEW
    // =========================================================================
    Component {
        id: workspaceView
        Item {
            // Dihapus anchors.fill: parent untuk menghindari konflik dengan StackView

            Rectangle {
                anchors.fill: parent
                color: genericTheme.bgSecondary

                // Navigation Top Bar
                Rectangle {
                    id: workspaceAppBar
                    width: parent.width
                    height: 56
                    color: genericTheme.bgPrimary
                    border.color: genericTheme.borderColor
                    border.width: 1

                    // Back Button (Chevron)
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 8

                        Text {
                            text: "◀"
                            font.pixelSize: 16
                            color: genericTheme.textPrimary
                            anchors.centerIn: parent
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: stackView.pop()
                        }
                    }

                    Text {
                        text: "Workspace (" + window.activeToolType + ")"
                        font.pixelSize: 18
                        font.bold: true
                        color: genericTheme.textPrimary
                        anchors.centerIn: parent
                    }
                }

                ScrollView {
                    anchors.top: workspaceAppBar.bottom
                    anchors.bottom: parent.bottom
                    width: parent.width
                    clip: true

                    Column {
                        width: parent.width
                        spacing: 16
                        padding: 16

                        // --- BURST GALLERY CARD ---
                        Rectangle {
                            width: parent.width - 32
                            height: 340
                            color: genericTheme.bgPrimary
                            radius: genericTheme.radiusXl
                            border.color: genericTheme.borderColor
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 12

                                Text {
                                    text: "Burst Gallery"
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: genericTheme.textPrimary
                                }

                                // --- AREA TOMBOL IMPORT GAMBAR ---
                                Rectangle {
                                    width: parent.width
                                    height: 180
                                    color: "#F9FAFB"
                                    radius: genericTheme.radiusLg
                                    border.color: genericTheme.borderColor
                                    border.width: 1

                                    Column {
                                        anchors.centerIn: parent
                                        spacing: 8

                                        Text {
                                            text: "➕"
                                            font.pixelSize: 44
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }

                                        Text {
                                            text: "Import Gambar"
                                            font.pixelSize: 16
                                            font.bold: true
                                            color: genericTheme.textPrimary
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }

                                        Text {
                                            text: "Ketuk untuk memilih dari galeri"
                                            font.pixelSize: 12
                                            color: genericTheme.textSecondary
                                            anchors.horizontalCenter: parent.horizontalCenter
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        property bool isPressed: false
                                        onPressed: isPressed = true
                                        onReleased: {
                                            isPressed = false
                                            window.selectedImageCount = (window.selectedImageCount === 0) ? 5 : 0
                                        }
                                        onCanceled: isPressed = false

                                        Rectangle {
                                            anchors.fill: parent
                                            color: genericTheme.primary
                                            opacity: parent.isPressed ? 0.08 : 0
                                            radius: genericTheme.radiusLg
                                        }
                                    }
                                }

                                // Thumbnails Grid Placeholder (seperti di Kivy)
                                Rectangle {
                                    width: parent.width
                                    height: 80
                                    color: "transparent"

                                    Text {
                                        text: window.selectedImageCount > 0 
                                            ? "Burst loaded (5 thumbnails simulated)" 
                                            : "No images loaded"
                                        font.pixelSize: 13
                                        font.italic: window.selectedImageCount === 0
                                        color: genericTheme.textSecondary
                                        anchors.centerIn: parent
                                    }
                                }
                            }
                        }

                        // --- ALGORITHM WORKFLOW CARD ---
                        Rectangle {
                            width: parent.width - 32
                            height: 150
                            color: genericTheme.bgPrimary
                            radius: genericTheme.radiusXl
                            border.color: genericTheme.borderColor
                            border.width: 1

                            Column {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 12

                                Text {
                                    text: "Algorithm Workflow"
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: genericTheme.textPrimary
                                }

                                Row {
                                    width: parent.width
                                    spacing: 12

                                    // Button: Alignment
                                    Rectangle {
                                        width: (parent.width - 44) / 2
                                        height: 40
                                        color: "#E5E7EB"
                                        radius: 20

                                        Text {
                                            text: "Alignment"
                                            color: genericTheme.textSecondary
                                            font.bold: true
                                            anchors.centerIn: parent
                                        }
                                    }

                                    Text {
                                        text: "➔"
                                        font.pixelSize: 18
                                        color: genericTheme.textSecondary
                                        anchors.verticalCenter: parent.verticalCenter
                                    }

                                    // Button: Active Tool (Denoise/HDR/etc)
                                    Rectangle {
                                        width: (parent.width - 44) / 2
                                        height: 40
                                        color: genericTheme.primary
                                        radius: 20

                                        Text {
                                            text: window.activeToolType
                                            color: "white"
                                            font.bold: true
                                            anchors.centerIn: parent
                                        }
                                    }
                                }

                                // Status Selected Images
                                Rectangle {
                                    height: 24
                                    width: parent.width
                                    color: "#F3F4F6"
                                    radius: 12
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    Text {
                                        text: window.selectedImageCount + " images selected"
                                        font.pixelSize: 11
                                        font.bold: true
                                        color: genericTheme.textSecondary
                                        anchors.centerIn: parent
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

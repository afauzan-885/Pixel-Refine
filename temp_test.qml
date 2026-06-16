
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    anchors.fill: parent
    color: genericTheme.bgSecondary

    ScrollView {
        anchors.fill: parent
        contentWidth: parent.width
        clip: true

        Column {
            width: parent.width
            spacing: 15
            leftPadding: 15
            rightPadding: 15
            topPadding: 15

            Text {
                text: "MOBILE (QML Engine Rendering)"
                font.bold: true
                font.pixelSize: 16
                color: "#34495E"
            }

        Column {
            spacing: 10
            width: parent.width
            leftPadding: 15
            rightPadding: 15
            topPadding: 15
            bottomPadding: 15
            Rectangle {
                width: parent.width
                height: 28
                color: genericTheme.primary // dynamic map
                radius: genericTheme.radiusMd
                Text {
                    text: 'Primary Button'
                    color: 'white'
                    font.bold: true
                    font.pointSize: 11
                    anchors.centerIn: parent
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: appBridge.openTool('Primary Button')
                }
            }
            Rectangle {
                width: parent.width
                height: 28
                color: genericTheme.success // dynamic map
                radius: genericTheme.radiusMd
                Text {
                    text: 'Success Button'
                    color: 'white'
                    font.bold: true
                    font.pointSize: 11
                    anchors.centerIn: parent
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: appBridge.openTool('Success Button')
                }
            }
            Rectangle {
                width: parent.width
                height: 28
                property bool checked: true
                color: checked ? genericTheme.primary : genericTheme.secondary
                radius: genericTheme.radiusMd
                Text {
                    text: 'Toggle Me'
                    color: 'white'
                    font.bold: true
                    font.pointSize: 11
                    anchors.centerIn: parent
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: parent.checked = !parent.checked
                }
            }
            Rectangle {
                width: 36
                height: 20
                radius: 10
                color: checked ? '#2ECC71' : '#BDC3C7'
                property bool checked: false
                Rectangle {
                    x: parent.checked ? 18 : 2
                    y: 2
                    width: 16
                    height: 16
                    radius: 8
                    color: '#FFFFFF'
                    Behavior on x { NumberAnimation { duration: 150 } }
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: parent.checked = !parent.checked
                }
            }
            TextField {
                width: parent.width
                height: 36
                placeholderText: 'Type something...'
                color: genericTheme.textPrimary
                background: Rectangle {
                    color: genericTheme.bgPrimary
                    border.color: genericTheme.borderColor
                    border.width: 1
                    radius: genericTheme.radiusSm
                }
            }
            ComboBox {
                width: parent.width
                height: 32
                model: ['Option A', 'Option B', 'Option C']
                currentIndex: 0
                background: Rectangle {
                    color: genericTheme.bgPrimary
                    border.color: genericTheme.borderColor
                    border.width: 1
                    radius: genericTheme.radiusSm
                }
            }
            CheckBox {
                text: 'Agree to terms'
                checked: true
            }
            Column {
                spacing: 5
                RadioButton { text: 'Vertical Mode'; checked: false }
                RadioButton { text: 'Horizontal Mode'; checked: false }
            }
            Column {
                width: parent.width
                spacing: 5
                Rectangle {
                    width: parent.width
                    height: 20
                    radius: 10
                    color: '#F5F8FA'
                    border.color: '#E8EDF2'
                    border.width: 1
                    Rectangle {
                        x: 1
                        y: 1
                        width: (parent.width - 2) * 0.75
                        height: parent.height - 2
                        radius: parent.radius - 1
                        color: '#3498db'
                    }
                }
                Text { text: '75%'; font.bold: true; color: '#666'; horizontalAlignment: Text.AlignHCenter; width: parent.width }
            }
            BusyIndicator {
                running: true
                width: 40
                height: 40
            }
            ListView {
                width: parent.width
                height: 200
                clip: true
                spacing: 2
                model: ListModel {
                    ListElement { text: 'Item 1 - Active' }
                    ListElement { text: 'Item 2 - Secondary' }
                }
                delegate: Rectangle {
                    width: ListView.view.width
                    height: 36
                    radius: genericTheme.radiusSm
                    color: genericTheme.bgPrimary
                    border.color: genericTheme.borderColor
                    border.width: 1
                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        spacing: 8
                        Text { text: model.text; anchors.verticalCenter: parent.verticalCenter; color: genericTheme.textPrimary; elide: Text.ElideRight }
                    }
                    MouseArea { anchors.fill: parent; onClicked: appBridge.openTool(model.text) }
                }
            }
            Rectangle {
                width: parent.width
                height: 104
                border.color: '#dee2e6'
                border.width: 1
                radius: 4
                clip: true
                Column {
                    anchors.fill: parent
                    spacing: 0
                    Rectangle {
                        width: parent.width
                        height: 44
                        color: '#f8f9fa'
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 2; color: '#dee2e6' }
                        Row {
                            anchors.fill: parent
                            Text { text: 'Name'; font.bold: true; width: parent.width / 2; color: '#495057'; verticalAlignment: Text.AlignVCenter; leftPadding: 8; anchors.verticalCenter: parent.verticalCenter }
                            Text { text: 'Status'; font.bold: true; width: parent.width / 2; color: '#495057'; verticalAlignment: Text.AlignVCenter; leftPadding: 8; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }
                    Rectangle {
                        width: parent.width
                        height: 30
                        color: '#ffffff'
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: '#f2f2f2' }
                        Row {
                            anchors.fill: parent
                            Text { text: 'User 1'; width: parent.width / 2; verticalAlignment: Text.AlignVCenter; leftPadding: 5; color: genericTheme.textPrimary; anchors.verticalCenter: parent.verticalCenter }
                            Text { text: 'Active'; width: parent.width / 2; verticalAlignment: Text.AlignVCenter; leftPadding: 5; color: genericTheme.textPrimary; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }
                    Rectangle {
                        width: parent.width
                        height: 30
                        color: '#f8f9fa'
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: '#f2f2f2' }
                        Row {
                            anchors.fill: parent
                            Text { text: 'User 2'; width: parent.width / 2; verticalAlignment: Text.AlignVCenter; leftPadding: 5; color: genericTheme.textPrimary; anchors.verticalCenter: parent.verticalCenter }
                            Text { text: 'Offline'; width: parent.width / 2; verticalAlignment: Text.AlignVCenter; leftPadding: 5; color: genericTheme.textPrimary; anchors.verticalCenter: parent.verticalCenter }
                        }
                    }
                }
            }
            Rectangle {
                width: parent.width
                height: contentCol.height + 14
                color: '#FFFFFF'
                radius: genericTheme.radiusLg
                border.color: '#E8EDF2'
                border.width: 1
                Column {
                    id: contentCol
                    x: 8
                    y: 6
                    width: parent.width - 16
                    spacing: 4
                    Row {
                        spacing: 8
                        Rectangle {
                            id: toggleCapsule
                            width: 36
                            height: 20
                            radius: 10
                            color: toggleCapsule.checked ? '#2ECC71' : '#BDC3C7'
                            property bool checked: false
                            anchors.verticalCenter: parent.verticalCenter
                            Rectangle {
                                x: toggleCapsule.checked ? 18 : 2
                                y: 2
                                width: 16
                                height: 16
                                radius: 8
                                color: '#FFFFFF'
                                Behavior on x { NumberAnimation { duration: 150 } }
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: parent.checked = !parent.checked
                            }
                        }
                        Text { text: 'Denoising Filter'; font.bold: true; font.pointSize: 11; color: '#2C3E50'; anchors.verticalCenter: parent.verticalCenter }
                    }
                    Text { text: 'Reduce noise using advanced bilateral filter algorithm.'; font.pointSize: 9.5; color: '#2C3E50'; wrapMode: Text.WordWrap; width: parent.width }
                    ComboBox {
                        model: ['Weak', 'Medium', 'Strong']
                        visible: false
                        width: parent.width
                    }
                }
            }
        }
        }
    }
}

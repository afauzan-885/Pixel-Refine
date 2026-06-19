"""
workspace_page.py
-----------------
Workspace Page — Dynamic QML page mapping to the user's prototype sketch.
"""

from PySide6.QtWidgets import QWidget

class WorkspaceContainer(QWidget):
    """
    Custom Workspace Container that overrides to_qml() to render
    the layout matching the hand-drawn mobile prototype sketch.
    """

    def __init__(self, bridge, parent=None):
        super().__init__(parent)
        self.bridge = bridge

    def to_qml(self, indent=0):
        tab = "    " * indent
        tool_name = self.bridge.current_tool if hasattr(self.bridge, "current_tool") else "MFDenoiser"
        
        qml = f"""{tab}Column {{
{tab}    id: workspaceColumn
{tab}    width: parent ? parent.width : 360
{tab}    spacing: 12
{tab}    leftPadding: 10
{tab}    rightPadding: 10
{tab}    topPadding: 10
{tab}    bottomPadding: 10

{tab}    // Status Bar & Header
{tab}    Rectangle {{
{tab}        width: parent.width - 20
{tab}        height: 60
{tab}        color: "transparent"

{tab}        // Time 12:30
{tab}        Text {{
{tab}            text: "12:30"
{tab}            font.pixelSize: 14
{tab}            font.bold: true
{tab}            color: genericTheme.textPrimary
{tab}            anchors.left: parent.left
{tab}            anchors.top: parent.top
{tab}        }}

{tab}        // Wifi/Battery Icons
{tab}        Row {{
{tab}            anchors.right: parent.right
{tab}            anchors.top: parent.top
{tab}            spacing: 4
{tab}            Text {{ text: "📶"; font.pixelSize: 12; color: genericTheme.textPrimary }}
{tab}            Text {{ text: "🔋"; font.pixelSize: 12; color: genericTheme.textPrimary }}
{tab}        }}

{tab}        // Back Button & Title
{tab}        Row {{
{tab}            anchors.bottom: parent.bottom
{tab}            anchors.left: parent.left
{tab}            spacing: 8

{tab}            Rectangle {{
{tab}                width: 32
{tab}                height: 32
{tab}                radius: 16
{tab}                color: genericTheme.bgPrimary
{tab}                border.color: genericTheme.borderColor
{tab}                border.width: 1

{tab}                Text {{
{tab}                    text: "◀"
{tab}                    font.pixelSize: 12
{tab}                    color: genericTheme.textPrimary
{tab}                    anchors.centerIn: parent
{tab}                }}

{tab}                MouseArea {{
{tab}                    anchors.fill: parent
{tab}                    onClicked: appBridge.openTool("Home")
{tab}                }}
{tab}            }}

{tab}            Text {{
{tab}                text: "Project Page"
{tab}                font.pixelSize: 20
{tab}                font.bold: true
{tab}                color: genericTheme.textPrimary
{tab}            }}
{tab}        }}
{tab}    }}

{tab}    // Horizontal Scrollable Batch Strip
{tab}    Flickable {{
{tab}        width: parent.width - 20
{tab}        height: 100
{tab}        contentWidth: batchRow.width
{tab}        contentHeight: height
{tab}        clip: true
{tab}        flickableDirection: Flickable.HorizontalFlick
{tab}        boundsBehavior: Flickable.StopAtBounds

{tab}        Row {{
{tab}            id: batchRow
{tab}            spacing: 8

{tab}            // New Batch Card
{tab}            Rectangle {{
{tab}                width: 90
{tab}                height: 90
{tab}                color: '#F0FDF4'
{tab}                radius: genericTheme.radiusLg
{tab}                border.color: '#2ECC71'
{tab}                border.width: 2

{tab}                Column {{
{tab}                    anchors.centerIn: parent
{tab}                    spacing: 4
{tab}                    Text {{
{tab}                        text: '+'
{tab}                        font.pixelSize: 24
{tab}                        font.bold: true
{tab}                        color: '#2ECC71'
{tab}                        anchors.horizontalCenter: parent.horizontalCenter
{tab}                    }}
{tab}                    Text {{
{tab}                        text: 'New Batch'
{tab}                        font.pixelSize: 10
{tab}                        font.bold: true
{tab}                        color: '#2ECC71'
{tab}                        anchors.horizontalCenter: parent.horizontalCenter
{tab}                    }}
{tab}                }}

{tab}                MouseArea {{
{tab}                    anchors.fill: parent
{tab}                    onClicked: {{
{tab}                        console.log("Create new batch tapped");
{tab}                    }}
{tab}                }}
{tab}            }}

{tab}            // Batch Cards (1 to 4)
{tab}            Repeater {{
{tab}                model: [
{tab}                    {{ name: "Batch 1", imgCount: 13 }},
{tab}                    {{ name: "Batch 2", imgCount: 8 }},
{tab}                    {{ name: "Batch 3", imgCount: 5 }},
{tab}                    {{ name: "Batch 4", imgCount: 12 }}
{tab}                ]

{tab}                delegate: Rectangle {{
{tab}                    width: 100
{tab}                    height: 90
{tab}                    color: genericTheme.bgPrimary
{tab}                    radius: genericTheme.radiusLg
{tab}                    border.color: genericTheme.borderColor
{tab}                    border.width: 1

{tab}                    Column {{
{tab}                        anchors.fill: parent
{tab}                        anchors.margins: 6
{tab}                        spacing: 4

{tab}                        Text {{
{tab}                            text: modelData.name
{tab}                            font.bold: true
{tab}                            font.pixelSize: 11
{tab}                            color: genericTheme.textPrimary
{tab}                        }}

{tab}                        // Mountains thumbnail preview using a simple Canvas
{tab}                        Canvas {{
{tab}                            width: parent.width
{tab}                            height: 40
{tab}                            onPaint: {{
{tab}                                var ctx = getContext("2d");
{tab}                                ctx.clearRect(0, 0, width, height);
{tab}                                ctx.strokeStyle = genericTheme.textSecondary;
{tab}                                ctx.lineWidth = 1.5;
{tab}                                ctx.beginPath();
{tab}                                // Left mountain
{tab}                                ctx.moveTo(0, height);
{tab}                                ctx.lineTo(width * 0.4, height * 0.2);
{tab}                                ctx.lineTo(width * 0.8, height);
{tab}                                // Right mountain
{tab}                                ctx.moveTo(width * 0.3, height);
{tab}                                ctx.lineTo(width * 0.75, height * 0.4);
{tab}                                ctx.lineTo(width, height);
{tab}                                ctx.stroke();
{tab}                            }}
{tab}                        }}

{tab}                        // Dropdown batch list indicator (triangle icon) at the bottom
{tab}                        Rectangle {{
{tab}                            width: parent.width
{tab}                            height: 12
{tab}                            color: "transparent"

{tab}                            Text {{
{tab}                                text: "▼"
{tab}                                font.pixelSize: 8
{tab}                                color: genericTheme.textSecondary
{tab}                                anchors.centerIn: parent
{tab}                            }}

{tab}                            MouseArea {{
{tab}                                anchors.fill: parent
{tab}                                onClicked: {{
{tab}                                    console.log("Dropdown batch list tapped for " + modelData.name);
{tab}                                }}
{tab}                            }}
{tab}                        }}
{tab}                    }}
{tab}                }}
{tab}            }}
{tab}        }}
{tab}    }}

{tab}    // Algorithm Method Segmented Tab (Align, SR/Denoise, Ake2A, Smart Merging)
{tab}    Rectangle {{
{tab}        width: parent.width - 20
{tab}        height: 40
{tab}        color: genericTheme.bgPrimary
{tab}        radius: genericTheme.radiusLg
{tab}        border.color: genericTheme.borderColor
{tab}        border.width: 1

{tab}        Row {{
{tab}            id: algoRow
{tab}            anchors.fill: parent
{tab}            property int activeIndex: 0

{tab}            Repeater {{
{tab}                model: ["Align", "SR/Denoise", "Ake2A", "Smart Merging"]

{tab}                delegate: Rectangle {{
{tab}                    width: parent.width / 4
{tab}                    height: parent.height
{tab}                    color: algoRow.activeIndex === index ? genericTheme.primary : "transparent"
{tab}                    radius: genericTheme.radiusLg

{tab}                    Text {{
{tab}                        text: modelData
{tab}                        color: algoRow.activeIndex === index ? "#FFFFFF" : genericTheme.textPrimary
{tab}                        font.bold: true
{tab}                        font.pixelSize: 10
{tab}                        anchors.centerIn: parent
{tab}                    }}

{tab}                    // Name Parameter Small Circle indicator on Smart Merging (top right)
{tab}                    Rectangle {{
{tab}                        visible: index === 3
{tab}                        width: 8
{tab}                        height: 8
{tab}                        radius: 4
{tab}                        color: "#E74C3C"
{tab}                        anchors.top: parent.top
{tab}                        anchors.right: parent.right
{tab}                        anchors.topMargin: 4
{tab}                        anchors.rightMargin: 4
{tab}                    }}

{tab}                    MouseArea {{
{tab}                        anchors.fill: parent
{tab}                        onClicked: {{
{tab}                            parent.parent.activeIndex = index;
{tab}                            console.log("Algorithm selected: " + modelData);
{tab}                        }}
{tab}                    }}
{tab}                }}
{tab}            }}
{tab}        }}
{tab}    }}

{tab}    // Image Reference Area (Large Viewer)
{tab}    Rectangle {{
{tab}        width: parent.width - 20
{tab}        height: 220
{tab}        color: genericTheme.bgPrimary
{tab}        radius: genericTheme.radiusLg
{tab}        border.color: genericTheme.borderColor
{tab}        border.width: 1
{tab}        clip: true

{tab}        // Mountain preview Canvas in main viewer (sun and mountains matching the sketch)
{tab}        Canvas {{
{tab}            anchors.fill: parent
{tab}            onPaint: {{
{tab}                var ctx = getContext("2d");
{tab}                ctx.clearRect(0, 0, width, height);

{tab}                // Draw Sun
{tab}                ctx.strokeStyle = "#F39C12";
{tab}                ctx.fillStyle = "#F39C12";
{tab}                ctx.lineWidth = 2;
{tab}                ctx.beginPath();
{tab}                ctx.arc(width * 0.5, height * 0.55, 20, Math.PI, 2 * Math.PI);
{tab}                ctx.fill();

{tab}                // Sun rays
{tab}                for (var angle = Math.PI; angle <= 2 * Math.PI; angle += Math.PI / 6) {{
{tab}                    var x1 = width * 0.5 + 23 * Math.cos(angle);
{tab}                    var y1 = height * 0.55 + 23 * Math.sin(angle);
{tab}                    var x2 = width * 0.5 + 32 * Math.cos(angle);
{tab}                    var y2 = height * 0.55 + 32 * Math.sin(angle);
{tab}                    ctx.beginPath();
{tab}                    ctx.moveTo(x1, y1);
{tab}                    ctx.lineTo(x2, y2);
{tab}                    ctx.stroke();
{tab}                }}

{tab}                // Draw Mountains
{tab}                ctx.strokeStyle = genericTheme.textPrimary;
{tab}                ctx.lineWidth = 3;
{tab}                ctx.beginPath();
{tab}                // Left mountain
{tab}                ctx.moveTo(width * 0.05, height * 0.8);
{tab}                ctx.lineTo(width * 0.45, height * 0.45);
{tab}                ctx.lineTo(width * 0.65, height * 0.7);
{tab}                // Right mountain
{tab}                ctx.moveTo(width * 0.4, height * 0.8);
{tab}                ctx.lineTo(width * 0.68, height * 0.4);
{tab}                ctx.lineTo(width * 0.95, height * 0.8);
{tab}                ctx.stroke();
{tab}            }}
{tab}        }}

{tab}        // Image Name (IMG_001)
{tab}        Rectangle {{
{tab}            anchors.left: parent.left
{tab}            anchors.top: parent.top
{tab}            anchors.margins: 10
{tab}            color: "#80000000"
{tab}            radius: 4
{tab}            width: 70
{tab}            height: 20

{tab}            Text {{
{tab}                text: "IMG_001"
{tab}                color: "#FFFFFF"
{tab}                font.pixelSize: 10
{tab}                font.bold: true
{tab}                anchors.centerIn: parent
{tab}            }}
{tab}        }}

{tab}        // Image Count (13 Images)
{tab}        Rectangle {{
{tab}            anchors.right: parent.right
{tab}            anchors.top: parent.top
{tab}            anchors.margins: 10
{tab}            color: "#80000000"
{tab}            radius: 4
{tab}            width: 75
{tab}            height: 20

{tab}            Text {{
{tab}                text: "📷 13 Images"
{tab}                color: "#FFFFFF"
{tab}                font.pixelSize: 10
{tab}                font.bold: true
{tab}                anchors.centerIn: parent
{tab}            }}
{tab}        }}

{tab}        // Centered Reference text at the bottom
{tab}        Text {{
{tab}            text: "Image (Reference)"
{tab}            color: genericTheme.textSecondary
{tab}            font.pixelSize: 11
{tab}            font.bold: true
{tab}            anchors.bottom: parent.bottom
{tab}            anchors.horizontalCenter: parent.horizontalCenter
{tab}            anchors.bottomMargin: 10
{tab}        }}
{tab}    }}

{tab}    // Swipe Batch Dot Indicators (• • • ● • • •)
{tab}    Row {{
{tab}        anchors.horizontalCenter: parent.horizontalCenter
{tab}        spacing: 6

{tab}        Repeater {{
{tab}            model: 7
{tab}            delegate: Rectangle {{
{tab}                width: index === 3 ? 10 : 6
{tab}                height: width
{tab}                radius: width / 2
{tab}                color: index === 3 ? genericTheme.primary : genericTheme.textMuted
{tab}            }}
{tab}        }}
{tab}    }}

{tab}    // Progress Bar / Notip ([i] |///////| 60%)
{tab}    Rectangle {{
{tab}        width: parent.width - 20
{tab}        height: 36
{tab}        color: genericTheme.bgPrimary
{tab}        radius: genericTheme.radiusLg
{tab}        border.color: genericTheme.borderColor
{tab}        border.width: 1

{tab}        Row {{
{tab}            anchors.fill: parent
{tab}            anchors.margins: 8
{tab}            spacing: 8

{tab}            // Info Icon
{tab}            Text {{
{tab}                text: "ℹ️"
{tab}                font.pixelSize: 14
{tab}                anchors.verticalCenter: parent.verticalCenter
{tab}            }}

{tab}            // Progress Bar Container
{tab}            Rectangle {{
{tab}                width: parent.width - 70
{tab}                height: 12
{tab}                color: genericTheme.bgSecondary
{tab}                radius: 6
{tab}                anchors.verticalCenter: parent.verticalCenter
{tab}                clip: true

{tab}                // Progress Fill
{tab}                Rectangle {{
{tab}                    width: parent.width * 0.6
{tab}                    height: parent.height
{tab}                    color: genericTheme.primary
{tab}                    radius: 6

{tab}                    // Diagonal animated stripes
{tab}                    Canvas {{
{tab}                        anchors.fill: parent
{tab}                        onPaint: {{
{tab}                            var ctx = getContext("2d");
{tab}                            ctx.fillStyle = "rgba(255,255,255,0.15)";
{tab}                            for (var x = -10; x < width; x += 15) {{
{tab}                                ctx.beginPath();
{tab}                                ctx.moveTo(x, 0);
{tab}                                ctx.lineTo(x + 10, 0);
{tab}                                ctx.lineTo(x + 5, height);
{tab}                                ctx.lineTo(x - 5, height);
{tab}                                ctx.fill();
{tab}                            }}
{tab}                        }}
{tab}                    }}
{tab}                }}
{tab}            }}

{tab}            // Progress Percent
{tab}            Text {{
{tab}                text: "60%"
{tab}                color: genericTheme.textPrimary
{tab}                font.bold: true
{tab}                font.pixelSize: 11
{tab}                anchors.verticalCenter: parent.verticalCenter
{tab}            }}
{tab}        }}
{tab}    }}

{tab}    // Bottom Navigation / Action Bar
{tab}    Rectangle {{
{tab}        width: parent.width - 20
{tab}        height: 60
{tab}        color: genericTheme.bgPrimary
{tab}        radius: genericTheme.radiusLg
{tab}        border.color: genericTheme.borderColor
{tab}        border.width: 1

{tab}        Row {{
{tab}            anchors.fill: parent
{tab}            anchors.margins: 6
{tab}            spacing: 8

{tab}            // Left navigation tabs (scrollable)
{tab}            Flickable {{
{tab}                width: parent.width - 80
{tab}                height: parent.height
{tab}                contentWidth: navItemsRow.width
{tab}                contentHeight: height
{tab}                clip: true
{tab}                flickableDirection: Flickable.HorizontalFlick

{tab}                Row {{
{tab}                    id: navItemsRow
{tab}                    spacing: 12
{tab}                    anchors.verticalCenter: parent.verticalCenter

{tab}                    // Home
{tab}                    Item {{
{tab}                        width: 50
{tab}                        height: 40
{tab}                        Column {{
{tab}                            anchors.fill: parent
{tab}                            spacing: 2
{tab}                            Text {{ text: "🏠"; font.pixelSize: 16; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                            Text {{ text: "Home"; font.pixelSize: 10; color: genericTheme.textPrimary; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                        }}
{tab}                        MouseArea {{
{tab}                            anchors.fill: parent
{tab}                            onClicked: appBridge.openTool("Home")
{tab}                        }}
{tab}                    }}

{tab}                    // Denoiser
{tab}                    Column {{
{tab}                        spacing: 2
{tab}                        Text {{ text: "🖼️"; font.pixelSize: 16; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                        Text {{ text: "Denoiser"; font.pixelSize: 10; color: genericTheme.primary; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                    }}

{tab}                    // MFResolution
{tab}                    Column {{
{tab}                        spacing: 2
{tab}                        Text {{ text: "🌟"; font.pixelSize: 16; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                        Text {{ text: "MFResolution"; font.pixelSize: 10; color: genericTheme.textPrimary; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                    }}
{tab}                }}
{tab}            }}

{tab}            // Start / Stop Circular Floating Button
{tab}            Rectangle {{
{tab}                width: 52
{tab}                height: 52
{tab}                radius: 26
{tab}                color: "#E74C3C"
{tab}                anchors.verticalCenter: parent.verticalCenter
{tab}                border.color: "#FFFFFF"
{tab}                border.width: 2

{tab}                Column {{
{tab}                    anchors.centerIn: parent
{tab}                    spacing: 1
{tab}                    Text {{ text: "Start"; color: "#FFFFFF"; font.pixelSize: 10; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                    Text {{ text: "Stop"; color: "#FFFFFF"; font.pixelSize: 8; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }}
{tab}                }}

{tab}                MouseArea {{
{tab}                    anchors.fill: parent
{tab}                    onClicked: {{
{tab}                        console.log("Start/Stop action button clicked!");
{tab}                    }}
{tab}                }}
{tab}            }}
{tab}        }}
{tab}    }}
{tab}}}"""
        return qml

def build_workspace_page(bridge) -> WorkspaceContainer:
    """Build the Workspace Page layout matching the prototype sketch."""
    return WorkspaceContainer(bridge)

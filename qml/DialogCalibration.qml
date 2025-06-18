// -*- coding: utf-8; -*-
//
// Copyright (C) 2025 Lionel Ott
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

import QtQuick.Controls.Universal

import Gremlin.Device


Window {
    minimumWidth: 850
    maximumWidth: 850
    minimumHeight: 600
    color: Universal.background
    title: "Calibration"

    DeviceListModel {
        id: _deviceData

        deviceType: "physical"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 10

        RowLayout {
            Layout.bottomMargin: 15

            Label {
                Layout.preferredWidth: 150
                text: "Device to calibrate"
            }

            ComboBox {
                id: _deviceSelection

                model: _deviceData
                textRole: "name"
                valueRole: "guid"
                implicitContentWidthPolicy: ComboBox.WidestText

                onActivated: () => {
                    if (currentValue !== undefined) {
                        _axisView.model.guid = currentValue
                    }
                }
                Component.onCompleted: () => {
                    if (count > 0) {
                        activated(0)
                    }
                }
            }
        }

        ListView {
            id: _axisView

            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            model: AxisCalibration {}
            clip: true

            delegate: CalibrationItem {
                width: ListView.view.width
            }

            // Make it behave like a sensible scrolling container
            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AlwaysOn
            }
            flickableDirection: Flickable.VerticalFlick
            boundsBehavior: Flickable.StopAtBounds
        }
    }


    component CalibrationItem : ColumnLayout {

        // Specify all properties we need from the model
        required property int index
        required property string identifier
        required property int calibratedValue
        required property int rawValue
        required property int low
        required property int centerLow
        required property int centerHigh
        required property int high
        required property bool withCenter
        required property bool unsavedChanges
        required property var model


        // Display axis name and current raw value and axis type
        RowLayout {
            Layout.rightMargin: 20

            Text {
                Layout.fillWidth: true

                text: identifier
                wrapMode: Text.Wrap
            }

            Text {
                Layout.preferredWidth: 75
                Layout.rightMargin: 5

                text: "Raw"
                horizontalAlignment: Text.AlignRight
            }

            TextField {
                Layout.preferredWidth: 100

                text: rawValue
            }

            Text {
                Layout.preferredWidth: 100

                text: "With center"
                horizontalAlignment: Text.AlignRight
            }
            Switch {
                Layout.preferredWidth: 100

                text: checked ? "Yes" : "No"
                checked: model.withCenter
                onToggled: {
                    model.withCenter = checked
                }
            }
        }


        RowLayout {

            Layout.rightMargin: 20

            // Show live axis sliders and calibration values
            ColumnLayout {
                Layout.fillWidth: true

                BetterProgressBar {
                    id: _progressRaw

                    Layout.preferredHeight: 30
                    Layout.fillWidth: true

                    value: rawValue
                    from: -32768
                    to: 32767
                }
                BetterProgressBar {
                    id: _progressCalibrated

                    Layout.preferredHeight: 30
                    Layout.fillWidth: true

                    value: calibratedValue
                    from: -32768
                    to: 32767
                }

                Rectangle {
                    Layout.fillHeight: true
                }

                // Show calibration values
                RowLayout {
                    CalibrationSpinBox {
                        id: _sbLow

                        value: low
                        to: 0

                        onValueModified: model.low = Qt.binding(() => value)
                    }
                    LayoutHorizontalSpacer {
                    }
                    CalibrationSpinBox {
                        id: _sbCLow

                        visible: model.withCenter
                        value: centerLow
                        to: 0

                        onValueModified: model.centerLow = Qt.binding(() => value)
                    }
                    CalibrationSpinBox {
                        id: _sbCHigh

                        visible: model.withCenter
                        value: centerHigh
                        from: 0

                        onValueModified: model.centerHigh = Qt.binding(() => value)
                    }
                    LayoutHorizontalSpacer {
                    }
                    CalibrationSpinBox {
                        id: _sbHigh

                        value: high
                        from: 0

                        onValueModified: model.high = Qt.binding(() => value)
                    }
                }
            }

            // Buttons to control calibration
            ColumnLayout {
                Layout.preferredWidth: 150
                Layout.alignment: Qt.AlignBottom

                RowLayout {
                    Button {
                        Layout.fillWidth: true

                        text: bsi.icons.reload
                        font.pixelSize: 20
                        font.bold: true

                        onClicked: () => _axisView.model.reset(index)
                    }
                    Button {
                        Layout.fillWidth: true

                        text: bsi.icons.save
                        font.pixelSize: 20

                        onClicked: () => _axisView.model.save(index)


                        Rectangle {
                            anchors.fill: parent
                            color: unsavedChanges ? "#F6BE00" : "transparent"
                        }
                    }
                }

                Button {
                    id: _btnCenterCalibration

                    Layout.preferredWidth: 150
                    text: "Calibrate center"
                    visible: model.withCenter

                    checkable: true
                    onToggled: () => {
                        _axisView.model.calibrateCenter(index, checked)
                        _btnExtremaCalibration.checked = false
                    }
                }
                LayoutVerticalSpacer {
                    visible: !model.withCenter
                }
                Button {
                    id: _btnExtremaCalibration

                    Layout.preferredWidth: 150
                    text: "Calibrate extrema"

                    checkable: true
                    onToggled: {
                        _axisView.model.calibrateExtrema(index, checked)
                        _btnCenterCalibration.checked = false
                    }
                }
            }
        }

        // Spacer at the bottom to leave some empty space below the ListView
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 10
        }
    }

    component CalibrationSpinBox : SpinBox {
        from: -32768
        to: 32767
        value: 0

        editable: true
    }
}
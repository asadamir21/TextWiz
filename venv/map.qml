import QtQuick 2.11
import QtPositioning 5.11
import QtLocation 5.11

Rectangle {
    id:rectangle
    width: 800
    height: 600
    Plugin {
        id: osmPlugin
        name: "osm"
    }
    property variant locationTC: QtPositioning.coordinate(44.951, -93.192)
    Map {
        id: map
        anchors.fill: parent
        plugin: osmPlugin
        center: locationTC
        zoomLevel: 3
        MapItemView{
            model: markermodel
            delegate: MapQuickItem {
                coordinate: model.position_marker
                anchorPoint.x: image.width
                anchorPoint.y: image.height
                sourceItem:
                    Image { id: image; source: model.source_marker }
            }
        }
    }
}
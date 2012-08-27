<html>
  <head>
    <style type="text/css">.spacer { margin-left: 10px; margin-right: 10px; }</style>
    <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAVNOfpLX6KdByplQxeMH1kuPZcYWBmz3c&sensor=false"></script>
    <script type="text/javascript">

var map;
var overlays = {};
var lat = 40.183;
var lng = 94.312;
var z = 8;

var stats;

Number.prototype.pad = function(size) {
    if (typeof(size) !== "number") { size = 2; }
    var s = String(this);
    while (s.length < size) {
        s = "0" + s;
    }
    return s;
}

Array.prototype.inclusiveRange = function(low, high) {
    var i, j;
    for (i = low, j = 0;  i <= high;  i++, j++) {
        this[j] = i;
    }
    return this;
}

function tileIndex(depth, longitude, latitude) {
    if (Math.abs(latitude) > 90.0) { alert("one"); }
    longitude += 180.0;
    latitude += 90.0;
    while (longitude <= 0.0) { longitude += 360.0; }
    while (longitude > 360.0) { longitude -= 360.0; }
    longitude = Math.floor(longitude/360.0 * Math.pow(2, depth+1));
    latitude = Math.min(Math.floor(latitude/180.0 * Math.pow(2, depth+1)), Math.pow(2, depth+1) - 1);
    return [depth, longitude, latitude];
}

function tileName(depth, longIndex, latIndex, layer) {
    return "T" + depth.pad(2) + "-" + longIndex.pad(5) + "-" + latIndex.pad(5) + "-" + layer;
}

function tileCorners(depth, longIndex, latIndex) {
    var longmin = longIndex*360.0/Math.pow(2, depth+1) - 180.0;
    var longmax = (longIndex + 1)*360.0/Math.pow(2, depth+1) - 180.0;
    var latmin = latIndex*180.0/Math.pow(2, depth+1) - 90.0;
    var latmax = (latIndex + 1)*180.0/Math.pow(2, depth+1) - 90.0;
    return new google.maps.LatLngBounds(
        new google.maps.LatLng(latmin, longmin),
        new google.maps.LatLng(latmax, longmax));
}

function initialize() {
    var latLng = new google.maps.LatLng(lat, lng);
    var options = {zoom: z, center: latLng, mapTypeId: google.maps.MapTypeId.SATELLITE};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);
    google.maps.event.addListener(map, "bounds_changed", getOverlays);

    stats = document.getElementById("stats");
}

function getOverlays() {
    var bounds = map.getBounds();
    if (!bounds) { return; }

    var depth = map.getZoom() - 2;
    if (depth > 10) { depth = 10; }

    var longmin = bounds.getSouthWest().lng();
    var longmax = bounds.getNorthEast().lng();
    var latmin = bounds.getSouthWest().lat();
    var latmax = bounds.getNorthEast().lat();

    [depth, longmin, latmin] = tileIndex(depth, longmin, latmin);
    [depth, longmax, latmax] = tileIndex(depth, longmax, latmax);

    var depthPad = depth.pad(2);
    var numDeleted = 0;
    for (var key in overlays) {
        if ((key[1] + key[2]) != depthPad) {
            overlays[key].setMap(null);
            delete overlays[key];
            numDeleted++;
        }
    }

    var numVisible = 0;
    var numAdded = 0;
    for (var longIndex = longmin;  longIndex <= longmax;  longIndex++) {
        for (var latIndex = latmin;  latIndex <= latmax;  latIndex++) {
            var key = tileName(depth, longIndex, latIndex, "RGB");
            if (!(key in overlays)) {
                var overlay = new google.maps.GroundOverlay("../TileServer/getTile?key=" + key, tileCorners(depth, longIndex, latIndex));
                overlay.setMap(map);
                overlays[key] = overlay;
                numAdded++;
            }
            numVisible++;
        }
    }

    var numInMemory = 0;
    for (var key in overlays) {
        numInMemory++;
    }

    stats.innerHTML = "<span class='spacer'>Zoom depth: " + depth + "</span><span class='spacer'>Tiles visible: " + numVisible + "</span><span class='spacer'>Tiles in your browser's memory: " + numInMemory + "</span><span class='spacer'>(counting empty tiles)</span>";
}

    </script>
  </head>
  <body onload="initialize();">

  <div id="map_canvas" style="width: 100%; height: 97%;"></div>

  <div id="stats" style="text-align: center;"></div>

  </body>
</html>

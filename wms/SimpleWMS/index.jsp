<html>
  <head>
    <meta http-equiv="content-type" content="text/html;charset=UTF-8" />
    <title>SimpleWMS</title>
    <style type="text/css">
      .spacer { margin-left: 10px; margin-right: 10px; }
      .layer_checkbox { margin-left: 20px; margin-top: 2px; margin-bottom: 2px; }
      table { table-layout: fixed; } 
      .header { font-weight: bold; border-bottom: solid 2px grey; }
      .row { max-width: 200px; overflow: hidden; padding-left: 5px; padding-right: 5px; }
      .even { background: #e7e7e7; }
      .odd { background: #f3f3f3; }
      .cell { text-align: center; }
    </style>
    <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAVNOfpLX6KdByplQxeMH1kuPZcYWBmz3c&sensor=false"></script>
    <script type="text/javascript">
// <![CDATA[

var map;
var circle;

var overlays = {};
var lat = 40.183;
var lng = 94.312;
var z = 9;
var layers = ["RGB"];

var points = {};
var oldsize;
var crossover = 4;
var showPoints = true;

var alldata;

var stats;
var stats_depth = -1;
var stats_numVisible = 0;
var stats_numInMemory = 0;
var stats_numPoints = 0;

var map_canvas;
var sidebar;

Number.prototype.pad = function(size) {
    if (typeof(size) !== "number") { size = 2; }
    var s = String(this);
    while (s.length < size) {
        s = "0" + s;
    }
    return s;
}

// Array.prototype.inclusiveRange = function(low, high) {
//     var i, j;
//     for (i = low, j = 0;  i <= high;  i++, j++) {
//         this[j] = i;
//     }
//     return this;
// }

Object.size = function(obj) {
    var size = 0;
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) { size++; }
    }
    return size;
};

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

function doresize() {
    map_canvas.style.width = window.innerWidth - sidebar.offsetWidth - 20;
    var height = window.innerHeight - stats.offsetHeight - 20;
    map_canvas.style.height = height;
    sidebar.style.height = height - 10;
}

window.onresize = doresize;

function initialize() {
    getTable();

    var latLng = new google.maps.LatLng(lat, lng);
    var options = {zoom: z, center: latLng, mapTypeId: google.maps.MapTypeId.SATELLITE};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);
    google.maps.event.addListener(map, "bounds_changed", getEverything);

    circle = new google.maps.MarkerImage("http://192.168.15.14/pivarski/matsu-wms-test/circle.png", new google.maps.Size(18, 18), new google.maps.Point(0, 0), new google.maps.Point(9, 9), new google.maps.Size(18, 18));
    oldsize = 0;

    stats = document.getElementById("stats");
    map_canvas = document.getElementById("map_canvas");
    sidebar = document.getElementById("sidebar");
    doresize();
    sidebar.addEventListener("DOMAttrModified", doresize);
}

function getTable() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
	    alldata = JSON.parse(xmlhttp.responseText)["data"];
	    drawTable();
	}
    }
}

function drawTable() {
    var table = "<table>";
    
    




    document.getElementById("table-here").innerHTML = "<table> \
<tr class=\"row header\"><td class=\"cell\">time</td><td class=\"cell\">latitude</td><td class=\"cell\">longitude</td></tr> \
<tr class=\"row even\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
<tr class=\"row odd\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
<tr class=\"row even\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
<tr class=\"row odd\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
<tr class=\"row even\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
<tr class=\"row odd\"><td class=\"cell\">1</td><td class=\"cell\">2</td><td class=\"cell\">3</td></tr> \
</table>";


}

function getEverything() {
    getOverlays();
    if (showPoints) { getLngLatPoints(); }
    else { updateStatus(); }
}

function toggleState(name, objname) {
    var obj = document.getElementById(objname);
    var newState = !(obj.checked);
    obj.checked = newState;

    var i = layers.indexOf(name);

    if (newState  &&  i == -1) {
	layers.push(name);
    }
    else if (!newState  &&  i != -1) {
	layers.splice(i, 1);

	for (var key in overlays) {
	    if (key.substring(16) == name) {
		overlays[key].setMap(null);
		delete overlays[key];
	    }
	}
    }

    getOverlays();
}

function togglePoints(objname) {
    var obj = document.getElementById(objname);
    showPoints = !(obj.checked);
    obj.checked = showPoints;

    if (showPoints) {
	getLngLatPoints();
    }
    else {
	for (var key in points) {
	    points[key].setMap(null);
	    delete points[key];
	}
	points = {};
	oldsize = -2;
	stats_numPoints = 0;
	updateStatus();
    }
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
    for (var key in overlays) {
        if ((key[1] + key[2]) != depthPad) {
            overlays[key].setMap(null);
            delete overlays[key];
        }
    }

    stats_depth = depth;

    stats_numVisible = 0;
    var numAdded = 0;
    for (var i in layers) {
	for (var longIndex = longmin;  longIndex <= longmax;  longIndex++) {
            for (var latIndex = latmin;  latIndex <= latmax;  latIndex++) {
		var key = tileName(depth, longIndex, latIndex, layers[i]);
		if (!(key in overlays)) {
                    var overlay = new google.maps.GroundOverlay("../TileServer/getTile?key=" + key, tileCorners(depth, longIndex, latIndex));
                    overlay.setMap(map);
                    overlays[key] = overlay;
                    numAdded++;
		}
		stats_numVisible++;
            }
	}
    }

    stats_numInMemory = 0;
    for (var key in overlays) {
        stats_numInMemory++;
    }
}

function getLngLatPoints() {
    var bounds = map.getBounds();
    if (!bounds) { return; }

    var depth = map.getZoom() - 2;
    var size = 0;
    if (depth <= 9) {
	circle.size = new google.maps.Size(18, 18);
	circle.scaledSize = new google.maps.Size(18, 18);
	circle.anchor = new google.maps.Point(9, 9);
	if (depth <= crossover) {
	    size = -1;
	}
    }
    else {
	size = Math.pow(2, depth - 10);
	circle.size = new google.maps.Size(36 * size, 36 * size);
	circle.scaledSize = new google.maps.Size(36 * size, 36 * size);
	circle.anchor = new google.maps.Point(18 * size, 18 * size);
    }

    if (oldsize != size) {
	for (var key in points) {
	    points[key].setMap(null);
	    delete points[key];
	}
	points = {};
    }
    oldsize = size;

    var longmin = bounds.getSouthWest().lng();
    var longmax = bounds.getNorthEast().lng();
    var latmin = bounds.getSouthWest().lat();
    var latmax = bounds.getNorthEast().lat();

    [depth, longmin, latmin] = tileIndex(10, longmin, latmin);
    [depth, longmax, latmax] = tileIndex(10, longmax, latmax);

    var url;
    if (size != -1) {
	url = "../TileServer/getTile?command=points&longmin=" + longmin + "&longmax=" + longmax + "&latmin=" + latmin + "&latmax=" + latmax;
    }
    else {
	url = "../TileServer/getTile?command=points&longmin=" + longmin + "&longmax=" + longmax + "&latmin=" + latmin + "&latmax=" + latmax + "&groupdepth=" + crossover;
    }

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
	    var data = JSON.parse(xmlhttp.responseText)["data"];
	    for (var i in data) {
		var identifier = data[i]["identifier"];
		if (!(identifier in points)) {
		    points[identifier] = new google.maps.Marker({"position": new google.maps.LatLng(data[i]["latitude"], data[i]["longitude"]), "map": map, "flat": true, "icon": circle});
		}
	    }

	    stats_numPoints = Object.size(points);
	    updateStatus();
	}
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function updateStatus() {
    stats.innerHTML = "<span class='spacer'>Zoom depth: " + stats_depth + "</span><span class='spacer'>Tiles visible: " + stats_numVisible + "</span><span class='spacer'>Tiles in your browser's memory: " + stats_numInMemory + " (counting empty tiles)</span><span class='spacer'>Points: " + stats_numPoints + "</span>";
}

// ]]>
    </script>
  </head>
  <body onload="initialize();" style="width: 100%; margin: 0px;">

  <div id="map_canvas" style="position: fixed; top: 5px; right: 5px; width: 100px; height: 100px; float: right; border: 1px solid black;"></div>
  <div id="sidebar" style="position: fixed; top: 5px; left: 5px; width: 400px; height: 100px; vertical-align: top; resize: horizontal; float: left; background: white; border: 1px solid black; padding: 5px; overflow-x: hidden; overflow-y: scroll;">

<h3 style="margin-top: 0px;">Layers</h3>
<form onsubmit="return false;">
<p class="layer_checkbox" onclick="toggleState('RGB', 'layer-RGB');"><label for="layer-RGB"><input id="layer-RGB" type="checkbox" checked="true"> Canonical RGB</label>
<p class="layer_checkbox" onclick="toggleState('CO2', 'layer-CO2');"><label for="layer-CO2"><input id="layer-CO2" type="checkbox"> Carbon dioxide</label>
</form>

<h3 style="margin-bottom: 0px;">Points</h3>
<form onsubmit="return false;">
<p class="layer_checkbox" onclick="togglePoints('show-points');"><label for="show-points"><input id="show-points" type="checkbox" checked="true"> Show points</label>
<p id="table-here" class="layer_checkbox" style="margin-top: 10px;"></p>

</form>

</div>

  <div id="stats" style="position: fixed; bottom: 5px; width: 100%; text-align: center;"><span style="color: white;">No message</span></div>

  </body>
</html>

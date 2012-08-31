<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
      #map_canvas { height: 100% }
    </style>
    <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAVNOfpLX6KdByplQxeMH1kuPZcYWBmz3c&sensor=false"></script>
    <link rel="stylesheet" href="css/black-tie/jquery-ui-1.8.23.custom.css">
    <script type="text/javascript" src="js/jquery-1.8.0.min.js"></script>
    <script type="text/javascript" src="js/jquery-ui-1.8.23.custom.min.js"></script>
    <script type="text/javascript">

<%!
public String giveMeSomething(String name, HttpServletRequest request) {
    String x = request.getParameter(name);
    if (x == null) { return "0"; }
    else { return x; }
}
%>


var centerLat = <%= giveMeSomething("centerLat", request) %>;
var centerLong = <%= giveMeSomething("centerLong", request) %>;
var radius = <%= giveMeSomething("radius", request) %>;

var map;
var hyperion;
var ali;

var minRadiance = null;
var maxRadiance = null;
var minTime = null;
var maxTime = null;

var minUserRadiance = null;
var maxUserRadiance = null;
var minUserTime = null;
var maxUserTime = null;

var radianceRange;
var timeRange;
var polygons = [];

function showTime(t) {
    var d = new Date(1000 * t);
    d.setMinutes(d.getMinutes() + d.getTimezoneOffset());  // get rid of any local timezone correction on the client's machine!
    return (d.getMonth() + 1) + "/" + (d.getYear() - 100);
}

function aliRadiance(row) {
    var r = 0.0;
    for (var key in {"radiance_B02": null, "radiance_B03": null, "radiance_B04": null, "radiance_B05": null, "radiance_B06": null, "radiance_B07": null, "radiance_B08": null, "radiance_B09": null, "radiance_B10": null}) {
	var rr = row[key];
	if (typeof rr != "undefined") { r += rr; }
    }
    return r;
}

function initialize() {
    if (radius == 0) {
	document.getElementById("map_canvas").style.height = "100%";
	document.getElementById("list_of_directories").style.height = "0%";
    }
    
    var latLng = new google.maps.LatLng(centerLat, centerLong);
    var options = {zoom: <%= (request.getParameter("radius") == null) ? 2 : 8 %>, center: latLng, mapTypeId: google.maps.MapTypeId.HYBRID};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "available_hyperion.json", false);
    xmlhttp.send();
    hyperion = JSON.parse(xmlhttp.responseText)["data"];

    for (var i in hyperion) {
	var r = hyperion[i]["radiance"];
	if (minRadiance == null  ||  r < minRadiance) { minRadiance = r; }
	if (maxRadiance == null  ||  r > maxRadiance) { maxRadiance = r; }

	var t = hyperion[i]["acquisition_start"];
	if (minTime == null  ||  t < minTime) { minTime = t; }
	if (maxTime == null  ||  t > maxTime) { maxTime = t; }
    }

    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "available_ali.json", false);
    xmlhttp.send();
    ali = JSON.parse(xmlhttp.responseText)["data"];

    for (var i in ali) {
	var r = aliRadiance(ali[i]);
	if (minRadiance == null  ||  r < minRadiance) { minRadiance = r; }
	if (maxRadiance == null  ||  r > maxRadiance) { maxRadiance = r; }

	var t = ali[i]["acquisition_start"];
	if (minTime == null  ||  t < minTime) { minTime = t; }
	if (maxTime == null  ||  t > maxTime) { maxTime = t; }
    }

    minRadiance = Math.min(minRadiance, 0.0);

    minUserRadiance = minRadiance;
    maxUserRadiance = maxRadiance;
    minUserTime = minTime;
    maxUserTime = maxTime;

    $(function() {
	$( "#slider-radiance" ).slider({
	    range: true,
	    min: minRadiance,
	    max: maxRadiance,
	    values: [minUserRadiance, maxUserRadiance],
	    slide: function( event, ui ) {
		minUserRadiance = ui.values[0];
		maxUserRadiance = ui.values[1];
		radianceRange.innerHTML = Math.round(minUserRadiance) + " - " + Math.round(maxUserRadiance);
	    }
	});
    });

    $(function() {
	$( "#slider-time" ).slider({
	    range: true,
	    min: minTime,
	    max: maxTime,
	    values: [minUserTime, maxUserTime],
	    slide: function( event, ui ) {
		minUserTime = ui.values[0];
		maxUserTime = ui.values[1];
		timeRange.innerHTML = showTime(minUserTime) + " - " + showTime(maxUserTime);
	    }
	});
    });

    radianceRange = document.getElementById("radiance-range");
    timeRange = document.getElementById("time-range");
    radianceRange.innerHTML = Math.round(minUserRadiance) + " - " + Math.round(maxUserRadiance);
    timeRange.innerHTML = showTime(minUserTime) + " - " + showTime(maxUserTime);

    drawData();
}

function clearData() {
    for (var i in polygons) {
	polygons[i].setMap(null);
	delete polygons[i];
    }
    polygons = [];
}

function drawData() {
    var list_of_directories = "<p style=\"margin-left: 10px; margin-top: 10px;\"><b>Hyperion:</b> ";

    var infowindow = new google.maps.InfoWindow({"content": "<p>hello"});

    for (var i in hyperion) {
	var r = hyperion[i]["radiance"];
	var t = hyperion[i]["acquisition_start"];
	if (r < minUserRadiance  ||  r > maxUserRadiance  ||  t < minUserTime  ||  t > maxUserTime) { continue; }

	var corners = hyperion[i]["corners"];
	
	var coordinates = [];
	var sumlat = 0.0;
	var sumlng = 0.0;
	var sum1 = 0.0;
	for (var j in corners) {
	    coordinates.push(new google.maps.LatLng(corners[j][1], corners[j][0]));
	    sumlat += corners[j][1];
	    sumlng += corners[j][0];
	    sum1 += 1.0;
	}
	var latitude = sumlat / sum1;
	var longitude = sumlng / sum1;

	var inball = false;
	if (Math.sqrt(Math.pow(latitude - centerLat, 2) + Math.pow(longitude - centerLong, 2)) < radius) { inball = true; }

	if (inball  ||  radius == 0) {
	    var polygon = new google.maps.Polygon({"paths": coordinates, "strokeColor": "#8d0ecc", "strokeWeight": 2., "fillOpacity": 0.0, "clickable": true});
	    polygon.setMap(map);

	    google.maps.event.addListener(polygon, "rightclick", function(lat, lng) {
		return function() {
		    window.location.href = "available.jsp?centerLat=" + lat + "&centerLong=" + lng + "&radius=1";
		};
	    }(latitude, longitude));

	    polygons.push(polygon);

	    list_of_directories += hyperion[i]["directory"] + " ";
        }
    }

    list_of_directories += "\n<p style=\"margin-left: 10px; margin-top: 10px;\"><b>ALI:</b> ";

    for (var i in ali) {
	var r = aliRadiance(ali[i]);
	var t = ali[i]["acquisition_start"];
	if (r < minUserRadiance  ||  r > maxUserRadiance  ||  t < minUserTime  ||  t > maxUserTime) { continue; }

	var corners = ali[i]["corners"];
	
	var coordinates = [];
	var sumlat = 0.0;
	var sumlng = 0.0;
	var sum1 = 0.0;
	for (var j in corners) {
	    coordinates.push(new google.maps.LatLng(corners[j][1], corners[j][0]));
	    sumlat += corners[j][1];
	    sumlng += corners[j][0];
	    sum1 += 1.0;
	}
	var latitude = sumlat / sum1;
	var longitude = sumlng / sum1;

	var inball = false;
	if (Math.sqrt(Math.pow(latitude - centerLat, 2) + Math.pow(longitude - centerLong, 2)) < radius) { inball = true; }

	if (inball  ||  radius == 0) {
	    var polygon = new google.maps.Polygon({"paths": coordinates, "strokeColor": "#f52b0c", "strokeWeight": 2., "fillOpacity": 0.0, "clickable": true});
	    polygon.setMap(map);

	    google.maps.event.addListener(polygon, "rightclick", function(lat, lng) {
		return function() {
		    window.location.href = "available.jsp?centerLat=" + lat + "&centerLong=" + lng + "&radius=1";
		};
	    }(latitude, longitude));

	    polygons.push(polygon);

	    list_of_directories += ali[i]["directory"] + " ";
        }
    }

    if (radius != 0) {
	document.getElementById("list_of_directories").innerHTML = list_of_directories;
    }
}

    </script>
    
  </head>
  <body onload="initialize();" style="width: 100%; margin: 0px;">
    
    <div id="map_canvas" style="position: fixed; top: 0px; left: 0px; width: 100%; height: 90%;"></div>
    
    <div id="list_of_directories" style="position: fixed; bottom: 0px; left: 0px; width: 100%; height: 10%; overflow-y: scroll; overflow-x: hidden;"></div>
    
    <div style="position: fixed; background: white; top: 50px; right: 10px; overflow: hidden; width: 175px; height: 205px; border: 2px solid black;">
      <div style="padding: 5px;"><b>Legend:</b></div>
      <div style="padding: 5px;"><div style="float: left; width: 30px; height: 15px; border: 2px solid #f52b0c; margin-right: 5px;"></div> ALI</div>
      <div style="padding: 5px;"><div style="float: left; width: 30px; height: 15px; border: 2px solid #8d0ecc; margin-right: 5px;"></div> Hyperion</div>
      
      <div style="padding: 5px;">
	<p style="margin-top: 2px; margin-bottom: 2px;"><b>Radiance:</b> <span id="radiance-range"></span>
	  <div style="padding: 5px;"><div id="slider-radiance"></div></div>
	<p style="margin-top: 0px; margin-bottom: 2px;"><b>Time:</b> <span id="time-range"></span>
	  <div style="padding: 5px;"><div id="slider-time"></div></div>
	  <div style="text-align: center;"><button onclick="clearData(); drawData();">Update</button></div>
      </div>
    </div>
    
  </body>
</html>

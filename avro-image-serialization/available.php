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
    <script type="text/javascript">

var map;

function initialize() {
    var centerLat = <?php if (isset($_GET["centerLat"])) { echo $_GET["centerLat"]; } else { echo 0; } ?>;
    var centerLong = <?php if (isset($_GET["centerLong"])) { echo $_GET["centerLong"]; } else { echo 0; } ?>;
    var radius = <?php if (isset($_GET["radius"])) { echo $_GET["radius"]; } else { echo 0; } ?>;

    if (radius == 0) {
       document.getElementById("map_canvas").style.height = "100%";
       document.getElementById("list_of_directories").style.height = "0%";
    }

    var latLng = new google.maps.LatLng(centerLat, centerLong);
    var options = {zoom: <?php if (isset($_GET["radius"])) { echo "8"; } else { echo "2"; } ?>, center: latLng, mapTypeId: google.maps.MapTypeId.HYBRID};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "just_polylines.json", false);
    xmlhttp.send();
    data = JSON.parse(xmlhttp.responseText);

    var flags = {}

    var list_of_directories = "<p>";

    for (var i in data["data"]) {
	  var corners = data["data"][i]["corners"];

	  var inball = false;
	  var coordinates = [];
	  for (var j in corners) {
	      coordinates.push(new google.maps.LatLng(corners[j][1], corners[j][0]));

	      if (Math.sqrt(Math.pow(corners[j][1] - centerLat, 2) + Math.pow(corners[j][0] - centerLong, 2)) < radius) { inball = true; }
	  }

	  if (inball  ||  radius == 0) {
              flags[[Math.round(corners[0][1]), Math.round(corners[0][0])]] = true;

	      var polygon = new google.maps.Polygon({paths: coordinates, strokeWeight: 0., fillColor: "#FF0000", fillOpacity: 0.35});
	      polygon.setMap(map);

	      list_of_directories += data["data"][i]["directory"] + " ";
          }
    }

    for (var i in flags) {
        var coord = i.split(",");
        var marker = new google.maps.Marker({position: new google.maps.LatLng(coord[0], coord[1]), map: map, title: ("" + i[0] + i[1]), flat: true});
    }

    if (radius != 0) {
       document.getElementById("list_of_directories").innerHTML = list_of_directories;
    }
}

    </script>
    
  </head>
  <body onload="initialize();">

<div id="map_canvas" style="width: 100%; height: 90%;"></div>

<div id="list_of_directories" style="width: 100%; height: 10%; padding-left: 5px; padding-right: 5px;"></div>

  </body>
</html>

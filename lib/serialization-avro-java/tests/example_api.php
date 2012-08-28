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
    var latLng = new google.maps.LatLng(<?php echo file_get_contents("L1G-centerLat.txt"); ?>, <?php echo file_get_contents("L1G-centerLong.txt"); ?>);
    var options = {zoom: 10, center: latLng, mapTypeId: google.maps.MapTypeId.SATELLITE};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);

    var bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(<?php echo file_get_contents("L1G-bottomrightLat.txt"); ?>, <?php echo file_get_contents("L1G-topleftLong.txt"); ?>),
        new google.maps.LatLng(<?php echo file_get_contents("L1G-topleftLat.txt"); ?>, <?php echo file_get_contents("L1G-bottomrightLong.txt"); ?>));
    var overlay = new google.maps.GroundOverlay("L1G-overlay.png", bounds);
    overlay.setMap(map);

    var coordinates = [
        new google.maps.LatLng(<?php echo file_get_contents("L1G-p1lat.txt"); ?>, <?php echo file_get_contents("L1G-p1long.txt"); ?>),
        new google.maps.LatLng(<?php echo file_get_contents("L1G-p2lat.txt"); ?>, <?php echo file_get_contents("L1G-p2long.txt"); ?>),
        new google.maps.LatLng(<?php echo file_get_contents("L1G-p3lat.txt"); ?>, <?php echo file_get_contents("L1G-p3long.txt"); ?>),
        new google.maps.LatLng(<?php echo file_get_contents("L1G-p4lat.txt"); ?>, <?php echo file_get_contents("L1G-p4long.txt"); ?>),
        new google.maps.LatLng(<?php echo file_get_contents("L1G-p1lat.txt"); ?>, <?php echo file_get_contents("L1G-p1long.txt"); ?>)];
    var path = new google.maps.Polyline({path: coordinates, strokeColor: "#FF0000", strokeOpacity: 1.0, strokeWeight: 2});
    path.setMap(map);
}

    </script>
    
  </head>
  <body onload="initialize();">

<div id="map_canvas" style="width: 100%; height: 100%;"></div>

  </body>
</html>

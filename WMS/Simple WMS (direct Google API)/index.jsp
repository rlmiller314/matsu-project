<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
    </style>
    <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?key=AIzaSyAVNOfpLX6KdByplQxeMH1kuPZcYWBmz3c&sensor=false"></script>
    <script type="text/javascript">

var map;

function initialize() {
    var latLng = new google.maps.LatLng(31.6237151437, 130.677470179);
    var options = {zoom: 10, center: latLng, mapTypeId: google.maps.MapTypeId.SATELLITE};
    map = new google.maps.Map(document.getElementById("map_canvas"), options);

    var bounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(31.1739723317, 130.539438107),
        new google.maps.LatLng(32.0733256687, 130.814275415));
    var overlay = new google.maps.GroundOverlay("L1G-overlay.png", bounds);
    overlay.setMap(map);

    google.maps.event.addListener(map, "bounds_changed", function() {
        var x = 3;
    });
}

    </script>
    
  </head>
  <body onload="initialize();">

<div id="map_canvas" style="width: 100%; height: 100%;"></div>

  </body>
</html>

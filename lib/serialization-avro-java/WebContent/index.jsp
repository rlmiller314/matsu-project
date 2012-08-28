<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=UTF-8" />
<link rel="stylesheet" type="text/css" href="css/imgareaselect-default.css" />
<script type="text/javascript" src="scripts/jquery.min.js"></script>
<script type="text/javascript" src="scripts/jquery.imgareaselect.pack.js"></script>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>

<script type="text/javascript">
// <![CDATA[

var bandNames = [];
var dimensions = [];

google.load("visualization", "1", {packages:["corechart"]});

function initialize() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "../GeoPictureServlet/getData?command=bandNames", false);
    xmlhttp.send();
    bandNames = JSON.parse(xmlhttp.responseText);

    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", "../GeoPictureServlet/getData?command=dimensions", false);
    xmlhttp.send();
    dimensions = JSON.parse(xmlhttp.responseText);

    var defaultRed = bandNames.indexOf("B029");
    var defaultGreen = bandNames.indexOf("B023");
    var defaultBlue = bandNames.indexOf("B016");

    var selectRed = "";
    var selectGreen = "";
    var selectBlue = "";
    for (var i in bandNames) {
        if (defaultBlue == -1) { defaultBlue = i; }
        else if (defaultGreen == -1) { defaultGreen = i; }
        else if (defaultRed == -1) { defaultRed = i; }

        if (defaultRed == i) {
            selectRed += "<option selected=\"true\">" + bandNames[i] + "</option>";
        }
        else {
            selectRed += "<option>" + bandNames[i] + "</option>";
        }

        if (defaultGreen == i) {
            selectGreen += "<option selected=\"true\">" + bandNames[i] + "</option>";
        }
        else {
            selectGreen += "<option>" + bandNames[i] + "</option>";
        }

        if (defaultBlue == i) {
            selectBlue += "<option selected=\"true\">" + bandNames[i] + "</option>";
        }
        else {
            selectBlue += "<option>" + bandNames[i] + "</option>";
        }
    }

    document.getElementById("selectRed").innerHTML = selectRed;
    document.getElementById("selectGreen").innerHTML = selectGreen;
    document.getElementById("selectBlue").innerHTML = selectBlue;

    updateImage();

    $(document).ready(function () {
        $("img#image").imgAreaSelect({
            handles: true,
            onSelectEnd: resizeSelection
        });
    });

    document.getElementById("horiz").value = bandNames[defaultRed];
    document.getElementById("vert").value = bandNames[defaultBlue];

    document.getElementById("red").value = bandNames[defaultRed];
    document.getElementById("green").value = bandNames[defaultGreen];
    document.getElementById("blue").value = bandNames[defaultBlue];
}

function updateImage() {
    var red = document.getElementById("selectRed").value;
    var green = document.getElementById("selectGreen").value;
    var blue = document.getElementById("selectBlue").value;

    var image = document.getElementById("image");
    var image_working = document.getElementById("image_working");
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
            image.src = "data:image/png;base64," + xmlhttp.responseText;
            image.style.display = "block";
            image_working.style.display = "none";
        }
    }

    image.style.display = "none";
    image_working.style.display = "block";
    xmlhttp.open("GET", "../GeoPictureServlet/getData?command=image&red=" + red + "&green=" + green + "&blue=" + blue + "&base64", true);
    xmlhttp.send();
}

function dblclickSelection(event) {
    var x = event.clientX - event.target.offsetLeft;
    var y = event.clientY - event.target.offsetTop;

    var ias = $("#image").imgAreaSelect({instance: true});

    ias.setSelection(x - 50, y - 50, x + 50, y + 50, true);
    ias.setOptions({show: true});
    ias.update();

    document.getElementById("x1").value = x - 50;
    document.getElementById("y1").value = y - 50;
    document.getElementById("x2").value = x + 50;
    document.getElementById("y2").value = y + 50;
}

function resizeSelection(img, selection) {
    document.getElementById("x1").value = selection.x1;
    document.getElementById("y1").value = selection.y1;
    document.getElementById("x2").value = selection.x2;
    document.getElementById("y2").value = selection.y2;
}

function updateRegion() {
    var x1 = parseInt(document.getElementById("x1").value);
    var y1 = parseInt(document.getElementById("y1").value);
    var x2 = parseInt(document.getElementById("x2").value);
    var y2 = parseInt(document.getElementById("y2").value);

    if (x1 >= 0  &&  x1 < dimensions[0]  &&  x2 > x1  &&  x2 < dimensions[0]  &&  y1 >= 0  &&  y1 < dimensions[1]  &&  y2 > y1  &&  y2 < dimensions[1]) {
        var ias = $("#image").imgAreaSelect({instance: true});

        ias.setSelection(x1, y1, x2, y2, true);
        ias.setOptions({show: true});
        ias.update();

        document.getElementById("x1").value = x1;
        document.getElementById("y1").value = y1;
        document.getElementById("x2").value = x2;
        document.getElementById("y2").value = y2;
    }
}

function drawFalseColor() {
    var x1 = parseInt(document.getElementById("x1").value);
    var y1 = parseInt(document.getElementById("y1").value);
    var x2 = parseInt(document.getElementById("x2").value);
    var y2 = parseInt(document.getElementById("y2").value);

    var red = encodeURIComponent(document.getElementById("red").value);
    var green = encodeURIComponent(document.getElementById("green").value);
    var blue = encodeURIComponent(document.getElementById("blue").value);

    var manual = document.getElementById("manual").checked;
    var min = parseFloat(document.getElementById("min").value);
    var max = parseFloat(document.getElementById("max").value);
    if (!manual  ||  !(min >= 0.0)  ||  !(max >= 0.0)) {
        min = 0.0;
        max = 0.0;
    }
    min = encodeURIComponent(min);
    max = encodeURIComponent(max);

    if (x1 >= 0  &&  x1 < dimensions[0]  &&  x2 > x1  &&  x2 < dimensions[0]  &&  y1 >= 0  &&  y1 < dimensions[1]  &&  y2 > y1  &&  y2 < dimensions[1]) {
        var subimage = document.getElementById("subimage");
        var subimage_working = document.getElementById("subimage_working");
    	var xmlhttp = new XMLHttpRequest();
    	xmlhttp.onreadystatechange = function() {
    	    if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
    	        subimage.src = "data:image/png;base64," + xmlhttp.responseText;
                subimage.style.display = "block";
                subimage_working.style.display = "none";
    	    }
        }

        subimage.style.display = "none";
	subimage_working.style.display = "block";
    	xmlhttp.open("GET", "../GeoPictureServlet/getData?command=image&red=" + red + "&green=" + green + "&blue=" + blue + "&min=" + min + "&max=" + max + "&x1=" + x1 + "&y1=" + y1 + "&x2=" + x2 + "&y2=" + y2 + "&base64", true);
    	xmlhttp.send();
    }
}

function drawSpectrum() {
    var x1 = parseInt(document.getElementById("x1").value);
    var y1 = parseInt(document.getElementById("y1").value);
    var x2 = parseInt(document.getElementById("x2").value);
    var y2 = parseInt(document.getElementById("y2").value);

    var logarithmic = document.getElementById("logarithmic").checked;

    if (x1 >= 0  &&  x1 < dimensions[0]  &&  x2 > x1  &&  x2 < dimensions[0]  &&  y1 >= 0  &&  y1 < dimensions[1]  &&  y2 > y1  &&  y2 < dimensions[1]) {
        var spectrum_plot = document.getElementById("spectrum_plot");
        var spectrum_working = document.getElementById("spectrum_working");
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
        	var spectrumData = xmlhttp.responseText;

        	document.getElementById("spectrum_output").innerHTML = spectrumData;

        	spectrumData = JSON.parse(spectrumData);
        	if (logarithmic) {
        	    spectrumData.unshift(["band", "log(radiance)"]);
        	}
        	else {
        	    spectrumData.unshift(["band", "radiance"]);
        	}
        	spectrumData = google.visualization.arrayToDataTable(spectrumData);

		spectrum_plot.style.display = "block";
        	var spectrum_plotter = new google.visualization.ColumnChart(spectrum_plot);
        	if (logarithmic) {
        	    spectrum_plotter.draw(spectrumData, {"hAxis": {"title": "band names"}, "vAxis": {"title": "log(radiance)"}, "legend": "none"});
        	}
        	else {
        	    spectrum_plotter.draw(spectrumData, {"hAxis": {"title": "band names"}, "vAxis": {"title": "radiance", "minValue": 0.0}, "legend": "none"});
        	}
		spectrum_working.style.display = "none";
            }
        }

	spectrum_plot.style.display = "none";
	spectrum_working.style.display = "block";
        if (logarithmic) {
            xmlhttp.open("GET", "../GeoPictureServlet/getData?command=spectrum&x1=" + x1 + "&y1=" + y1 + "&x2=" + x2 + "&y2=" + y2 + "&log", true);
        }
        else {
            xmlhttp.open("GET", "../GeoPictureServlet/getData?command=spectrum&x1=" + x1 + "&y1=" + y1 + "&x2=" + x2 + "&y2=" + y2, true);
        }
        xmlhttp.send();
    }
}

function drawScatter() {
    var x1 = parseInt(document.getElementById("x1").value);
    var y1 = parseInt(document.getElementById("y1").value);
    var x2 = parseInt(document.getElementById("x2").value);
    var y2 = parseInt(document.getElementById("y2").value);

    var horiz = document.getElementById("horiz").value;
    var vert = document.getElementById("vert").value;

    if (x1 >= 0  &&  x1 < dimensions[0]  &&  x2 > x1  &&  x2 < dimensions[0]  &&  y1 >= 0  &&  y1 < dimensions[1]  &&  y2 > y1  &&  y2 < dimensions[1]) {
        var scatter_plot = document.getElementById("scatter_plot");
        var scatter_working = document.getElementById("scatter_working");
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState == 4  &&  xmlhttp.status == 200) {
        	var scatterData = xmlhttp.responseText;

        	document.getElementById("scatter_output").innerHTML = scatterData;

        	scatterData = JSON.parse(scatterData);
        	scatterData.unshift([horiz, vert]);
        	scatterData = google.visualization.arrayToDataTable(scatterData);

		scatter_plot.style.display = "block";
        	var scatter_plotter = new google.visualization.ScatterChart(scatter_plot);
        	scatter_plotter.draw(scatterData, {"hAxis": {"title": horiz, "minValue": 0.0}, "vAxis": {"title": vert, "minValue": 0.0}, "legend": "none"});
		scatter_working.style.display = "none";
            }
        }

	scatter_plot.style.display = "none";
	scatter_working.style.display = "block";
        xmlhttp.open("GET", "../GeoPictureServlet/getData?command=scatter&x1=" + x1 + "&y1=" + y1 + "&x2=" + x2 + "&y2=" + y2 + "&horiz=" + encodeURIComponent(horiz) + "&vert=" + encodeURIComponent(vert), true);
        xmlhttp.send();
    }
}

// ]]>
</script>
</head>
<body style="width: 100%; margin: 0px;" onload="initialize();">

<div style="float: right; margin-right: 10px; margin-bottom: 10px;">
<form onsubmit="updateImage(); return false;" style="display: block; float: right;">
<p><b>Red:</b> <select id="selectRed"></select>
<b>Green:</b> <select id="selectGreen"></select>
<b>Blue:</b> <select id="selectBlue"></select>
<input type="submit" value="Update">
</form>
<br style="clear: right;">
<div><div id="image_working" style="display: none; text-align: center; color: red;">Working...</div><img id="image" src="space.png" ondblclick="dblclickSelection(event);" style="margin: 10px; border: 1px solid black; padding: 1px;"></div>
</div>

<div style="position: fixed; background: white; border-right: 1px solid black; padding-left: 10px; overflow: hidden; resize: horizontal; width: 750px; min-width: 520px; max-width: 95%; height: 100%; overflow-y: scroll;">

<form onsubmit="updateRegion(); return false;" style="border-bottom: 1px dashed grey; margin-right: 10px;">
<p><b>Selection:</b>
<p><b>x1:</b> <input id="x1" type="text" autocomplete="off" size="5" value="">
<b>y1:</b> <input id="y1" type="text" autocomplete="off" size="5" value="">
<b>x2:</b> <input id="x2" type="text" autocomplete="off" size="5" value="">
<b>y2:</b> <input id="y2" type="text" autocomplete="off" size="5" value="">
<input type="submit" value="Update">
</form>

<form onsubmit="drawFalseColor(); return false;" style="border-bottom: 1px dashed grey; margin-right: 10px;">
<p><b>False color:</b>
<p><b>red:</b> <input id="red" type="text" autocomplete="off" style="position: absolute; left: 80px; width: 250px;" value=""><br>
<b>green:</b> <input id="green" type="text" autocomplete="off" style="position: absolute; left: 80px; width: 250px;" value=""><br>
<b>blue:</b> <input id="blue" type="text" autocomplete="off" style="position: absolute; left: 80px; width: 250px;" value="">
<input type="submit" value="Update" style="position: absolute; left: 350px;">
<p><label for="manual"><input id="manual" type="checkbox">&nbsp;manual&nbsp;range</label>&nbsp;from
<input id="min" type="text" autocomplete="off" size="5">
to <input id="max" type="text" autocomplete="off" size="5">
<div style="width: 100%; height: 300px; padding-top: 10px; padding-bottom: 10px;"><div id="subimage_working" style="display: none; text-align: center; color: red;">Working...</div><img id="subimage" src="image.png" style="display: block; height: 100%; width: auto; margin-left: auto; margin-right: auto;"></div>
</form>

<form onsubmit="drawSpectrum(); return false;" style="border-bottom: 1px dashed grey; margin-right: 10px;">
<p><b>Spectrum:</b>
<textarea id="spectrum_output" style="width: 370px; max-width: 370px; float: right; margin-right: 10px; resize: vertical; min-height: 31px;" rows="1" cols="20" readonly="readonly"></textarea>
<br style="clear: right;">
<label for="logarithmic"><input id="logarithmic" type="checkbox">&nbsp;logarithmic</label>
<input type="submit" value="Update">
<div id="spectrum_working" style="display: none; text-align: center; color: red; height: 300px;">Working...</div><div id="spectrum_plot" style="width: 100%; height: 300px;"></div>
</form>

<form onsubmit="drawScatter(); return false;" style="margin-right: 10px;">
<p><b>Distribution:</b>
<textarea id="scatter_output" style="width: 370px; max-width: 370px; float: right; margin-right: 10px; resize: vertical; min-height: 31px;" rows="1" cols="20" readonly="readonly"></textarea>
<br style="clear: right;">
<b>horiz:</b> <input id="horiz" type="text" autocomplete="off" style="position: absolute; left: 80px; width: 250px;" value=""><br>
<b>vert:</b> <input id="vert" type="text" autocomplete="off" style="position: absolute; left: 80px; width: 250px;" value="">
<input type="submit" value="Update" style="position: absolute; left: 350px;">
<div id="scatter_working" style="display: none; text-align: center; color: red; height: 300px;">Working...</div><div id="scatter_plot" style="width: 100%; height: 300px;"></div>
</form>

</div>

</body>
</html>

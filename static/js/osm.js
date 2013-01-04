var map;
var layer_mapnik;
var layer_tah;
var layer_markers;
var PI = Math.PI;
var latfield = '';
var lonfield = '';
var latfield_id='';
var lonfield_id='';
var centerlon = 10;
var centerlat = 52;
var zoom = 6;

function lon2merc(lon) {
    return 20037508.34 * lon / 180;
}

function lat2merc(lat) {
	lat = Math.log(Math.tan( (90 + lat) * PI / 360)) / PI;
	return 20037508.34 * lat;
}

function merc2lon(lon) {
	return lon*180/20037508.34;
};

function merc2lat(lat) {
	return Math.atan(Math.exp(lat*PI/20037508.34))*360/PI-90;
};

OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {
	defaultHandlerOptions: {
		'single': true,
		'double': false,
		'pixelTolerance': 0,
		'stopSingle': false,
		'stopDouble': false
	},

	initialize: function(options) {
		this.handlerOptions = OpenLayers.Util.extend(
			{}, this.defaultHandlerOptions
		);
		OpenLayers.Control.prototype.initialize.apply(
			this, arguments
		);
			this.handler = new OpenLayers.Handler.Click(
				this, {
					'click': this.trigger
			}, this.handlerOptions
		);
	}, 

	trigger: function(e) {
		var lonlat = map.getLonLatFromViewPortPx(e.xy);	
		lat=merc2lat(lonlat.lat);
		lon=merc2lon(lonlat.lon);
		latfield=document.getElementById('imageconf_latitude');
		lonfield=document.getElementById('imageconf_longitude');
		latfield.value = lat;
		lonfield.value = lon;								
	}
});

function init(){			
	var field = window.name.substring(0, window.name.lastIndexOf("."));
	if(document.getElementById("imageconf_latitude")!=null){
		centerlat =parseFloat(document.getElementById("imageconf_latitude").value);
	}
	if(document.getElementById("imageconf_longitude")!=null){
		centerlon = parseFloat(document.getElementById("imageconf_longitude").value);
	}
	zoom = '13';
}

function drawmap() {
	OpenLayers.Lang.setCode('de'); 
	mapdiv=document.getElementById('map');
	mapdiv.style.height='450px';
	mapdiv.style.width='100%';
	map = new OpenLayers.Map('map', {
		projection: new OpenLayers.Projection("EPSG:900913"),
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
		controls: [
			new OpenLayers.Control.Navigation(),
			new OpenLayers.Control.PanZoomBar()],
		maxExtent:
			new OpenLayers.Bounds(-20037508.34,-20037508.34, 20037508.34, 20037508.34),
		numZoomLevels: 18,
		maxResolution: 156543,
		units: 'meters'
	});

	layer_mapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");

	map.addLayers([layer_mapnik]);
	var y =lat2merc(centerlat);
	var x =lon2merc(centerlon);
	map.setCenter(new OpenLayers.LonLat(x, y), zoom);
	
	var click = new OpenLayers.Control.Click();
	map.addControl(click);
	click.activate();
}

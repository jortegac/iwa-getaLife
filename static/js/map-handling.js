var map;
var facetSearchData = [];

function initialize() {
	var mapOptions = {
	  center: new google.maps.LatLng(52.365957,4.894009),
	  zoom: 13
	  };
	map = new google.maps.Map(document.getElementById("map-canvas"),
		mapOptions);
}

function getFacetName(item){
	var terms = item.match(/([A-Z]?[^A-Z]*)/g).slice(0,-1);
	return terms[terms.length-1];
}

function sendSearchRequest() {
	data = facetSearchData.join("&");
	alert(data);
	//$.get('/show', data=data, function(json){	
	//}
}

// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
	setAllMap(null);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
	clearMarkers();
	markers = [];
}
// Set all markers on the map 
function setAllMap(map) {
	for (var i = 0; i < markers.length; i++) {
		markers[i].setMap(map);
	}
}

// Processes the venue data and puts them on the map
function processVenues(json) {
	// Process each venue in the response
	$.each(json.response.venues, function(i, item) {
		
		// Create a point using the lat and lng of the venue
		var point = new google.maps.LatLng(item.location.lat,item.location.lng);
		// Create the information to be displayed for each venue
		var html = createHtml(item);
		// Create the marker using the coordinates and the display information
		createMarker(point, html);
	});	
	
	// Put all the markers on the map
	setAllMap(map)
	
	// Center the map on the first marker in the response
	centerMap(markers[0]);
	
	// Trigger the click event on the first marker to bring up the display information for that venue
	google.maps.event.trigger(markers[0], 'click'); 
}

// Create the information to be displayed for this venue
function createHtml(item){
	var div = $('<div style="width:240px"></div>');
	var br = $('<br/>');
	
	// Venue name
	div.append(item.name);
	
	// Venue category name
	if(!jQuery.isEmptyObject(item.categories)){
		div.append(br);
		var p = $('<p></p>');
		p.append(item.categories[0].name);
		div.append(p);
	}
	
	// Venue URL
	if(!jQuery.isEmptyObject(item.url)){
		var p = $('<p></p>');
		var a = $('<a></a>');
		a.attr("href", item.url);
		a.attr("target", "_blank");
		a.append("Visit website");
		
		p.append(a);
		div.append(p);
	}
	
	// Venue contact phone
	if(!jQuery.isEmptyObject(item.contact.phone)){
		var p = $('<p></p>');
		p.append(item.contact.phone);
		div.append(p);
	}
	
	return div[0].outerHTML;
}

// Zoom in and center the map on the marker
function centerMap(marker) {
	
	map.setCenter(marker.position);	
	map.setZoom(16);
}

// Create marker
function createMarker(point, html) {
	// Create marker using the coordinates in the point
	var marker = new google.maps.Marker({
		position: point
	});
	
	// Add display information to the marker's info window
	google.maps.event.addListener(marker, "click", function() {
		infowindow.setContent(html); 
        infowindow.open(map,marker);
	});
	
	// Put marker in the global markers structure
	markers.push(marker);
}

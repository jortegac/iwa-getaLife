
var currentGeolocation;
var currentCity = "";
var currentCountry = "";
var locationBoundS = "";
var locationBoundW = "";
var locationBoundN = "";
var locationBoundE = "";
var autocomplete;

$( document ).ready(function() {
	
	// Where the spinner animation will be placed 
	target = document.getElementById('modal');

	initializeSearchButton();
	
	initializeMap();
	initializeLocationAutocomplete();
	initializeDatePicker();
	initializeGeolocation();

	initializeDropdowns();
	getGenreRDF();
	getVenueTypeRDF();
	
	$("#geolocate").change(function(){
		if(this.checked) {
			$('#locationTextField').val(currentCity + ", " + currentCountry);
			google.maps.event.trigger(autocomplete, 'place_changed');
			document.getElementById('locationTextField').disabled = true;
		} else {
			document.getElementById('locationTextField').disabled = false;
		}
	});
	
	$("#closebutton").click(function(){
		$(".panel").toggle("fast");
		visible = false;
		var myNode = document.getElementById("panelText");
		while (myNode.firstChild) {
			myNode.removeChild(myNode.firstChild);
		}
    });
});

function initializeLocationAutocomplete(){
	// Code for the autocomplete location input text field
	var input = (document.getElementById('locationTextField'));
	
	// Limit the autocompletion to city names of the netherlands
	var autocompleOptions = {
		types: ['(cities)'],
		componentRestrictions: {country: 'nl'}
	};
	autocomplete = new google.maps.places.Autocomplete(input, autocompleOptions);
	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		
		reverseGeocodeLocation($("#locationTextField").val());
	});
	
	// Initial options for the map
	var myOptions = {
		zoom: 13,
		// Center on Amsterdam
		center: new google.maps.LatLng(52.3731, 4.8922),
		mapTypeControl: true,
		mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
		navigationControl: true,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	}
}

function initializeDropdowns(){
	$("#genreDropDown").dropdownCheckbox({
			data: [{id:1, label: "Waiting for data..."}],
			title: "Select genres",
			btnClass: "btn btn-primary",
			autosearch: true,
			hideHeader: false,
	});
	
	$("#typeDropDown").dropdownCheckbox({
			data: [{id:1, label: "Waiting for data..."}],
			title: "Select venue type",
			btnClass: "btn btn-primary",
			autosearch: true,
			hideHeader: false,
	});	
}

function initializeSearchButton(){
	console.log("initializeSearchButton");
	// Define behaviour for the submit event in the search form
	$("#searchForm").submit(function( event ) {
		// Prevent default behaviour from the search button
		event.preventDefault();
		
		search();
	});
}

// Perform search
function search(){
	console.log("Searching...");
	
	startLoadingAnimation();
	
	// Get selected genres
	var genres = $("#genreDropDown").dropdownCheckbox("checked");
	// Get selected venue types
	var types = $("#typeDropDown").dropdownCheckbox("checked");
	
	// Build genres query string
	var genresQueryString = "";	
	for (genre in genres){
		genresQueryString = genresQueryString + "&genre=" + genres[genre].id;
	}
	
	// Build venue types query string
	var typesQueryString = "";
	for (type in types){
		typesQueryString = typesQueryString + "&type=" + types[type].id;
	}
	 
	// Build date range query string
	var start = $("#date-start").val();
	var datesQueryString = "";
	if ( start != "") {
		datesQueryString = datesQueryString + "&start=" + start;
	}
	
	var end = $("#date-end").val();
	if (end != ""){
		datesQueryString = datesQueryString + "&end=" + end;
	}
	
	// Build location query string
	var location = $("#locationTextField").val();
	var locationQueryString = "";
	
	if (location!= "" && locationBoundS != "" && locationBoundW != "" && locationBoundN != "" && locationBoundE != ""){
		locationQueryString = "&s=" + locationBoundS + "&w=" + locationBoundW + "&n=" + locationBoundN + "&e=" + locationBoundE;
	}
	
	// Build full query string
	var endpoint = "/events?" + genresQueryString + typesQueryString + datesQueryString + locationQueryString;

    centerOnSearchedLocation(location);	

	console.log(endpoint);
	
	$.getJSON(endpoint).done(function(json) {
		console.log(json);		
		var venues = json.results.bindings;
		
		if (venues.length != 0){
			processVenues(venues);
		} else {
			// No info to display
			BootstrapDialog.alert({title:"Information", message:"No results found. Try a different combination"});
		}
		
		stopLoadingAnimation();
	});
}

// center the map on a certain location (for example, a city name)
function centerOnSearchedLocation(location) {
    // FIXME: maybe this code is a bit duplicated to reverseGeocodeLocation?
    var query = {'address': location};
	geocoder.geocode(query, function(results, status) {
		if (status !== google.maps.GeocoderStatus.OK) {
            console.warn("problems with geocoder; query was:", query);
            return;
        }
		console.log(results);
        var geometry = results[0].geometry;
		if(geometry.bounds !== undefined){
            var newCenter = geometry.bounds.getCenter();
        } else {
            var newCenter = geometry.location;
        }
        map.setCenter(newCenter);
    });
}

// This function takes a location and finds the bounding box that emcompases the location
function reverseGeocodeLocation(location) {
	console.log("reverseGeocodeLocation"); 
	// Start loading animation while data loads
	startLoadingAnimation();
	// Disable search button while geocoding happens
	$("search-venue").attr('disabled','disabled');
	geocoder.geocode({'address': location}, function(results, status) {			
		if (status == google.maps.GeocoderStatus.OK) {
			console.log(results);
			if(results[0].geometry.bounds){
			
			var bounds = results[0].geometry.bounds;
				//north
				locationBoundN = bounds.Aa.j;
				//south 
				locationBoundS = bounds.Aa.k; 			
				//west
				locationBoundW = bounds.qa.j; 
				//east
				locationBoundE = bounds.qa.k; 	
			}			
		}
		// Reactivate search button
		$("search-venue").removeAttr('disabled');
		// Stop animation
		stopLoadingAnimation();
	});
}

// Initialize the date picking UI elements
function initializeDatePicker(){
	var nowTemp = new Date();
    var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);

	var startDate = $('#date-start').datepicker({
		format:"yyyy-mm-dd",
		onRender: function(date) {
			return date.valueOf() < now.valueOf() ? 'disabled' : '';
		}
	}).on('changeDate', function(ev) {
		if (ev.date.valueOf() > endDate.date.valueOf()) {
			var newDate = new Date(ev.date)
			newDate.setDate(newDate.getDate() + 1);
			endDate.setValue(newDate);
		}
		startDate.hide();
		$('#dpd2')[0].focus();
	}).data('datepicker');
	
	var endDate = $('#date-end').datepicker({
		format:"yyyy-mm-dd",
		onRender: function(date) {
			return date.valueOf() <= startDate.date.valueOf() ? 'disabled' : '';
		}
	}).on('changeDate', function(ev) {
		endDate.hide();
	}).data('datepicker');
}

// Initialize Google map
function initializeMap(){
	google.maps.event.addDomListener(window, 'load', initialize);
}

// Retrieves a list of genres from the RDF store
function getGenreRDF(){
	var genres = [];
	var service = '/genres';

	$.getJSON(service).done(function(json) {
		
		$.each(json.results.bindings, function(i, binding) {			
			var canonicalName = binding.genre.value;
			var displayValue = binding.genre_name.value;			
			var tmp = canonicalName.lastIndexOf("/");
			
			shortName = canonicalName.substring(tmp+1);
			displayName = shortName.replace("Genre","");
			
			var item = {id: "ah:" + shortName, label:displayName}			
			genres.push(item)
			
		});	
		
		$("#genreDropDown").dropdownCheckbox("reset", genres);
	});
}

// Retrieve a list of venue types from the RDF store
function getVenueTypeRDF(){
	var venueTypes = [];
	var service = '/venueTypes';

	$.getJSON(service).done(function(json) {
		
		$.each(json.results.bindings, function(i, binding) {			
			var canonicalName = binding.venue_type.value;
					
			var tmp = canonicalName.lastIndexOf("/");
			
			shortName = canonicalName.substring(tmp+1);
			displayName = shortName.replace("VenueType","");
			
			var item = {id: "ah:" + shortName, label:displayName}			
			venueTypes.push(item)
		});	
		
		$("#typeDropDown").dropdownCheckbox("reset", venueTypes);
	});
}

// Request access to the user's location
function initializeGeolocation(){
	// Function that allows the user to select their current position as a location for the events. 
	// Note: it requires the user's permission
	if(navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(geolocationSuccess,  null,  {timeout:5000});
	} else {
		// Browser doesn't support Geolocation
	}
}

// Get users current geolocation, and the city/country where that is
function geolocationSuccess(position){
	var geoCheck = document.getElementById("geoCheck");
	geoCheck.style.display = "inline";

	currentGeolocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude); 
	
	geocoder.geocode({'latLng': currentGeolocation}, function(results, status) {			
		if (status == google.maps.GeocoderStatus.OK) {
			console.log(results);
			
			var arrAddress = results[0].address_components;
			var locality = "";
			var country = "";
            for (ac = 0; ac < arrAddress.length; ac++) {
                
                if (arrAddress[ac].types[0] == "locality") { 
					currentCity = arrAddress[ac].long_name ;
				}
				if (arrAddress[ac].types[0] == "country") { 
					currentCountry = arrAddress[ac].long_name ;
				}
            }
		}
	});
}

function getDBPediaInfos(title, city){
	$.getJSON('/dbpedia').done(function(json) {

	});
	
}

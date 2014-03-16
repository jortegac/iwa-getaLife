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
	
	//please don't touch this stuff
	//TODO: associate the toggling with markers activity
	//$(".panel").toggle("fast");
	
	$("#geolocate").change(function(){
		if(this.checked) {
			$('#locationTextField').val("");
			document.getElementById('locationTextField').disabled = true;
		} else {
			document.getElementById('locationTextField').disabled = false;
		}
	});
	
	$("#closebutton").click(function(){
		$(".panel").toggle("fast");
    });
});

function initializeLocationAutocomplete(){
	// Code for the autocomplete location input text field
	var input = (document.getElementById('locationTextField'));
	var autocomplete = new google.maps.places.Autocomplete(input);
	// Limit the autocompletion to city names
	autocomplete.setTypes(['(cities)']);
	google.maps.event.addListener(autocomplete, 'place_changed', function() {});
	
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

function search(){
	console.log("Searching...");
	
	startLoadingAnimation();
	
	var genres = $("#genreDropDown").dropdownCheckbox("checked");
	var types = $("#typeDropDown").dropdownCheckbox("checked");
	
	var genresQueryString = "";	
	for (genre in genres){
		genresQueryString = genresQueryString + "&genre=" + genres[genre].id;
	}
	
	var typesQueryString = "";
	for (type in types){
		typesQueryString = typesQueryString + "&type=" + types[type].id;
	}
	
	var endpoint = "/events?" + genresQueryString + typesQueryString;
	
	$.getJSON(endpoint).done(function(json) {
		console.log(json);		
		var venues = json.results.bindings;
		
		processVenues(venues);
		stopLoadingAnimation();
		
	});
	
	
}

function initializeDatePicker(){
	var nowTemp = new Date();
    var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);

	var startDate = $('#date-start').datepicker({
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
		onRender: function(date) {
			return date.valueOf() <= startDate.date.valueOf() ? 'disabled' : '';
		}
	}).on('changeDate', function(ev) {
		endDate.hide();
	}).data('datepicker');
}

function initializeMap(){
	google.maps.event.addDomListener(window, 'load', initialize);
}

function init_genrepicker(){

	var genres = [];
	genres.push("ah:GenreMovie");
	genres.push("ah:GenreDance");
	genres.push("ah:GenreCabaret");
	createGenres(genres);
}

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

function createGenres(genres) {
	$.each(genres, function(index, item) {
		$( "#genre" ).append( "<input type='checkbox' name='"+item+"' value='"+item+"'> "+getFacetName(item)+"<br/>" );
	});
	
	$("#genre input").click(function() {
		var parent = $(this).parent().attr('id');
		var searchParameter = parent+"="+this.value;
		if (this.checked) {
			facetSearchData.push(searchParameter);
			sendSearchRequest();
		} else {
			var index = $.inArray(searchParameter, facetSearchData);
			if (index > -1) {
				facetSearchData.splice(index, 1);
				sendSearchRequest();
			}
		}
	});
}

function initializeGeolocation(){
	// Function that allows the user to select their current position as a location for the events. 
	// Note: it requires the user's permission
	if(navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(geolocationSuccess,  null,  {timeout:5000});
	} else {
		// Browser doesn't support Geolocation
	}
}

function geolocationSuccess(position){
	var geoCheck = document.getElementById("geoCheck");
	geoCheck.style.display = "inline";

	var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude); 
	//TODO make the new LatLng available to the request
}


function dbpediaSearch(venueTitle, location) {

	var dbpediaDiv = $('#dbpedia-info');

	var url = "/dbpedia?&venue="+ venueTitle +"&city=" + location;
	var dbpedia = document.createElement('div');
	$.getJSON(url).done(function(json) {
	
		if (json.venue == undefined){
			$.each(json.city, function(index, info){
				dbpedia = createDBPediaHTML(location, info);
			});
		}
		else {
			$.each(json.venue, function(index, info){
				dbpedia = createDBPediaHTML(marker.getTitle(), info);
			});
		}
		
		dbpediaDiv.empty();
		dbpediaDiv.html(dbpedia.outerHTML);
	});
}

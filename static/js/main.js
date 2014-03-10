$( document ).ready(function() {
	
	init_map();
	init_datepicker();
	init_genrepicker();
});

function init_datepicker(){
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

function init_map(){
	google.maps.event.addDomListener(window, 'load', initialize);
}

function init_genrepicker(){

	var genres = [];
	genres.push("ah:GenreMovie");
	genres.push("ah:GenreDance");
	genres.push("ah:GenreCabaret");

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
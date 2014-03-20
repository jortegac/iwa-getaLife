var TWITTER = "http://twitter.com/"

function twitterSearch(searchTerm, position) {
	var tweetsDiv = $('#tweets');
	tweetsDiv.empty();
	console.log(position);
	var endpoint = "/twitter?search=" + searchTerm + "&geocode=" + position.k + "," + position.A + ",1km";
	console.log(endpoint);
	
	$.getJSON(endpoint).done(function(json) {
		console.log(json);		
		var tweets = json.statuses;
		
		$.each(tweets, function(i, tweet) {			
			var user = tweet.user.screen_name;
			var tweet_id = tweet.id;
			var text = tweet.text;
			var date = tweet.created_at;
			
			var a = $('<a class="list-group-item"></a>').attr("href", TWITTER + user + "/status/" + tweet_id).attr("target", "_blank").html("<span class='badge'>"+ user + "</span><p>" + text + "</p><p>" + date + "</p></a>");
			
			tweetsDiv.append(a);
		});	
	});
}

statsvars = {};

function enableStatsPanel(json) {
    // make stats checkbox invisible, for now
    $("#showStats_div").hide();
    $("#stats").hide();
    $("#showStats").click(function(){
        if($(this).is(":checked")){
            console.log("is checked");
            $("input[value=\"stacked\"]").click();
            $("#stats").fadeIn();
        } else {
            console.log("is NOT checked");
            $("input[value=\"grouped\"]").click();
            $("#stats").fadeOut();
        }
    });

    console.log("length of binding is:",json.results.bindings.length);
    var aggregates_by_type = createAggregates(json.results.bindings);
    var types = Object.keys(aggregates_by_type);
    var aggregates_by_genre = aggregatesByGenre(aggregates_by_type);
    var genres = Object.keys(aggregates_by_genre);
    var entries = stackableEntries(aggregates_by_genre,types);
	
	if (entries.length != 0){
		console.log("entries",entries);
		var friendlyTypes = genFriendlyTypes(types);
		var friendlyGenres = genFriendlyGenres(genres);
		initStats(entries,friendlyTypes,friendlyGenres);
	}
}

function genFriendlyGenres(types) {
    var ret = [];
    for(var i in types){
        var t = types[i];
        var tmp = t.replace(/.*\//,"");
        tmp = tmp.replace(/Genre/,"");
        ret.push(tmp);
    }
    return ret;
}

function genFriendlyTypes(types) {
    var ret = [];
    for(var i in types){
        var t = types[i];
        var tmp = t.replace(/.*\//,"");
        tmp = tmp.replace(/Type/,"");
        tmp = tmp.replace(/Venue/,"");
        ret.push(tmp);
    }
    return ret;
}

function aggregatesByGenre(aggregates_by_type) {
  var ret = {};
  for(var curr_type in aggregates_by_type) {
    var curr_venue = aggregates_by_type[curr_type];
    for(var curr_genre in curr_venue) {
      if(ret[curr_genre] === undefined) {
        ret[curr_genre] = {};
      }
      if(ret[curr_genre][curr_type] == undefined) {
        ret[curr_genre][curr_type] = curr_venue[curr_genre];
      } 
    }
  }
  return ret;
}


function createAggregates(data) {
    console.log('data, should be a list',data);

    var ret = {};
    for(var venue_i in data) {
        var venue = data[venue_i];
        var venue_title = venue.venue_title.value;
        console.log('venue_title', venue_title);
        var venue_type = venue.venue_type.value;
        console.log('venue_type', venue_type);
        var venue_type = venue.venue_type.value;
        if(ret[venue_type] === undefined) {
            var venue_entry = {};
        } else {
            var venue_entry = ret[venue_type];
        }
        for(var ev_i in venue.events) {
            var tmp = venue.events[ev_i];
            for(var ev_j in tmp) {
                var ev = tmp[ev_j];
                var genre_uri = ev.genre;
                if(venue_entry[genre_uri] === undefined) {
                    console.log('this was undefined', genre_uri);
                    venue_entry[genre_uri] = 0;
                }
                venue_entry[genre_uri] += 1;
            }
        }
        ret[venue_type] = venue_entry;
    }
    console.log('ret',ret);
    return ret;
}

function stackableEntries(aggregates, types) {

  var entries = [];

  for(var curr_genre in aggregates) {
    var curr_layer = [];
    var aggregates_genre = aggregates[curr_genre];
    var x = 0;
    for(var t_i in types){
      var curr_venue_type = types[t_i];
      var curr = aggregates_genre[curr_venue_type];
      if(curr === undefined) {
        curr = 0;
      }
      curr_layer.push({
        'x':x,
        'y':curr
      });
      x+=1;
    }
    console.log("adding curr_layer", curr_layer);
    entries.push(curr_layer);
  }
  return entries;
}

function initStats(entries,friendlyTypes, friendlyGenres) {

  $("#showStats_div").fadeIn();

  statsvars.statsTimeout = setTimeout(function() {
    d3.select("input[value=\"grouped\"]").property("checked", true).each(statsChange);
  }, 2000);

  statsvars.n = entries.length; // number of layers (genres)
  var m = entries[0].length, // number of samples per layer (venue types)
      stack = d3.layout.stack(),
      layers = stack(entries);
  statsvars.yGroupMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y; }); });
  statsvars.yStackMax = d3.max(layers, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); });

  var margin = {top: 40, right: 100, bottom: 20, left: 10},
      width = 500 - margin.left - margin.right;
  statsvars.height = 250 - margin.top - margin.bottom;

  statsvars.x = d3.scale.ordinal()
      .domain(d3.range(m))
      .rangeRoundBands([0, width], .08);

  statsvars.y = d3.scale.linear()
      .domain([0, statsvars.yStackMax])
      .range([statsvars.height, 0]);

  var color = d3.scale.category20();
  /*var color = d3.scale.linear()
      .domain([0, statsvars.n - 1])
      .range(["#aad", "#556"]); */




  var axislabels = d3.scale.ordinal()
    .domain(friendlyTypes)
    .rangeRoundBands([0, width], .08);

  var xAxis = d3.svg.axis()
      .scale(axislabels)
      .tickSize(0)
      .tickPadding(6)
      .orient("bottom");

  $("#stats").find('svg').remove();

  var svg = d3.select("#stats").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", statsvars.height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var w = 500;
  // add legend   
  var legend = svg.append("g")
      .attr("class", "legend")
      .attr("x", w - 100)
      .attr("y", 25)
      .attr("height", 100)
      .attr("width", 100);

  legend.selectAll('g').data(friendlyGenres)
    .enter()
    .append('g')
    .each(function(d, i) {
      var g = d3.select(this);
      g.append("rect")
        .attr("x", w - 110)
        .attr("y", i*25)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function(d) { return color(i); });
        
      g.append("text")
        .attr("x", w - 95)
        .attr("y", i * 25 + 8)
        .attr("height",30)
        .attr("width",100)
        .style("fill", function(dd) {return color(i); })
        .text(function(dd){return d;});
     });

  var layer = svg.selectAll(".layer")
      .data(layers)
    .enter().append("g")
      .attr("class", "layer")
      .style("fill", function(d, i) { return color(i); });

  statsvars.rect = layer.selectAll("rect")
      .data(function(d) { return d; })
    .enter().append("rect")
      .attr("x", function(d) { return statsvars.x(d.x); })
      .attr("y", statsvars.height)
      .attr("width", statsvars.x.rangeBand())
      .attr("height", 0);

  //layer.append("text")
  //    .text(function(d){ return d.x });

  statsvars.rect.transition()
      .delay(function(d, i) { return i * 10; })
      .attr("y", function(d) { return statsvars.y(d.y0 + d.y); })
      .attr("height", function(d) { return statsvars.y(d.y0) - statsvars.y(d.y0 + d.y); });

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + statsvars.height + ")")
      .call(xAxis);

  d3.selectAll(".stats_input").on("change", statsChange);

}

function statsChange() {
  clearTimeout(statsvars.statsTimeout);
  if (this.value === "grouped") statsTransitionGrouped();
  else statsTransitionStacked();
}

function statsTransitionGrouped() {
  statsvars.y.domain([0, statsvars.yGroupMax]);

  statsvars.rect.transition()
      .duration(500)
      .delay(function(d, i) { return i * 10; })
      .attr("x", function(d, i, j) { return statsvars.x(d.x) + statsvars.x.rangeBand() / statsvars.n * j; })
      .attr("width", statsvars.x.rangeBand() / statsvars.n)
    .transition()
      .attr("y", function(d) { return statsvars.y(d.y); })
      .attr("height", function(d) { return statsvars.height - statsvars.y(d.y); });
}

function statsTransitionStacked() {
  statsvars.y.domain([0, statsvars.yStackMax]);

  statsvars.rect.transition()
      .duration(500)
      .delay(function(d, i) { return i * 10; })
      .attr("y", function(d) { return statsvars.y(d.y0 + d.y); })
      .attr("height", function(d) { return statsvars.y(d.y0) - statsvars.y(d.y0 + d.y); })
    .transition()
      .attr("x", function(d) { return statsvars.x(d.x); })
      .attr("width", statsvars.x.rangeBand());
}

// Inspired by Lee Byron's test data generator.
function statsBumpLayer(n, o) {

  function bump(a) {
    var x = 1 / (.1 + Math.random()),
        y = 2 * Math.random() - .5,
        z = 10 / (.1 + Math.random());
    for (var i = 0; i < n; i++) {
      var w = (i / statsvars.n - y) * z;
      a[i] += x * Math.exp(-w * w);
    }
  }

  var a = [], i;
  for (i = 0; i < n; ++i) a[i] = o + o * Math.random();
  for (i = 0; i < 5; ++i) bump(a);
  return a.map(function(d, i) { return {x: i, y: Math.max(0, d)}; });
}


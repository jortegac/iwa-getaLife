from flask import Flask, render_template, url_for, request, jsonify, Response, json
from SPARQLWrapper import SPARQLWrapper, RDF, JSON, XML, N3
from StringIO import StringIO
import requests
import json
import urllib2
import logging

app = Flask(__name__)
app.logger.addHandler(logging.FileHandler("app.log"))

#Local endpoint
SPARQL_ENDPOINT = 'http://localhost:8080/openrdf-sesame/repositories/IWA-AH'

#ArtsHolland sparql endpoint
AH_ENDPOINT = 'http://api.artsholland.com/sparql'
#DBpedia sparql endpoint
DBP_ENDPOINT = 'http://nl.dbpedia.org/sparql'

#Prefixes needed for dbpedia
DBP_PREFIX = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
				PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
				PREFIX dbpediaowl: <http://dbpedia.org/ontology/>
				PREFIX nldbpedia:  <http://nl.dbpedia.org/property/>"""

PREFIX = """PREFIX dc:<http://purl.org/dc/terms/>
			PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
			PREFIX foaf:<http://xmlns.com/foaf/0.1/>
			PREFIX vcard:<http://www.w3.org/2006/vcard/ns#>
			PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
			PREFIX time:<http://www.w3.org/2006/time#>
			PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
			PREFIX owl:<http://www.w3.org/2002/07/owl#>
			PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX ah:<http://purl.org/artsholland/1.0/>"""
			
@app.route('/')
def index():
    return render_template('index.html')
    
# REST Endpoint wrapper for the runQuery function
@app.route('/sparql', methods=['GET'])
def sparql():
    # app.logger.debug('You arrived at ' + url_for('sparql'))
    # app.logger.debug('I received the following arguments' + str(request.args) )
	
    query = request.args.get('query', None)    
    return_format = request.args.get('format','JSON')
    
    return runQuery(query, return_format)
		
# Runs the sparql query asking for the results in the specified format
def runQuery(query, return_format, endpoint=SPARQL_ENDPOINT, jsoni=True):
    if endpoint and query :
        sparql = SPARQLWrapper(endpoint)
        
        sparql.setQuery(query)
        
        if return_format == 'RDF':
            sparql.setReturnFormat('RDF')
        else :
            sparql.setReturnFormat('JSON')
            sparql.addCustomParameter('Accept','application/sparql-results+json')
        
        #app.logger.debug('Query:\n{}'.format(query))
        #app.logger.debug('Querying endpoint {}'.format(endpoint))
        
        try :
            response = sparql.query().convert()
            
            # app.logger.debug('Results were returned, yay!')
            
            # app.logger.debug(response)
            
            if return_format == 'RDF':
                # app.logger.debug('Serializing to Turtle format')
                return response.serialize(format='turtle')
            else :
                # app.logger.debug('Directly returning JSON format')
                if jsoni == True:
					return jsonify(response)
                else:
					return json.dumps(response)
        except Exception as e:
            app.logger.error('Something went wrong')
            app.logger.error(e)
            return jsonify({'result': 'Error'})
            
        
    else :
        return jsonify({'result': 'Error'})

# Get a list of all the genres
@app.route('/genres', methods=['GET'])
def getGenres():
	sparql = PREFIX + "SELECT DISTINCT ?genre ?genre_name WHERE { ?production ah:genre ?genre. ?genre rdfs:label ?genre_name} ORDER BY ASC(?genre)"

	# Run the query
   	return runQuery(sparql, 'JSON') 
	
# Get a list of all venue types
@app.route('/venueTypes', methods=['GET'])
def getVenueTypes():
	sparql = PREFIX + "SELECT DISTINCT ?venue_type WHERE {?venue ah:venueType ?venue_type. } ORDER BY ASC(?venue_type )"

	# Run the query
   	return runQuery(sparql, 'JSON')

@app.route('/venues', methods=['GET'])
def getVenues():

	filter = ""
	
	if 'type' in request.args:
		type = request.args.getlist('type', None)
		filter = filter + " FILTER(?venue_type IN ("
		for item in type:
			filter = filter + item + ","
		filter = filter[:-1]
		filter = filter + "))"
		
	sparql = PREFIX + """SELECT DISTINCT ?venue ?venue_type ?venue_title ?venue_description ?venue_shortDescription ?venue_openingHours ?venue_locationAdress ?venue_latitude ?venue_longitude ?venue_email ?venue_homepage ?venue_geometry WHERE {
					?venue a ah:Venue .
					?venue ah:venueType ?venue_type .
					?venue dc:title ?venue_title .
					?event ah:venue ?venue.
					OPTIONAL {?venue dc:description ?venue_description .}
					OPTIONAL {?venue ah:shortDescription ?venue_shortDescription .}
					OPTIONAL {?venue ah:openingHours ?venue_openingHours .}
					OPTIONAL {?venue ah:locationAddress ?venue_locationAdress .}			   			   
					OPTIONAL {?venue geo:lat ?venue_latitude .}
					OPTIONAL {?venue geo:long ?venue_longitude .}
					OPTIONAL {?venue vcard:email ?venue_email .}
					OPTIONAL {?venue foaf:homepage ?venue_homepage .}
					OPTIONAL {?venue geo:geometry ?venue_geometry .}""" + filter + "}" 
	# Run the query
   	return runQuery(sparql, 'JSON') 	

@app.route('/events', methods=['GET'])
def getEvents():

	type_filter = ""
	
	# Get all the 'type' params for venues
	if 'type' in request.args:
		type = request.args.getlist('type', None)
		type_filter = type_filter + " FILTER(?venue_type IN ("
		for item in type:
			type_filter = type_filter + item + ","
		type_filter = type_filter[:-1]
		type_filter = type_filter + ")) ."
	
	print type_filter
	
	genre_filter = ""
	
	# Get all the 'genre' params for venues
	if 'genre' in request.args:
		genre = request.args.getlist('genre', None)
		genre_filter = genre_filter + " FILTER(?event_genre IN ("
		for item in genre:
			genre_filter = genre_filter + item + ","
		genre_filter = genre_filter[:-1]
		genre_filter = genre_filter + ")) ."
		
	print genre_filter
	
	dateFilter = ""
	
	if 'start' in request.args and 'end' in request.args:
		
		start = request.args.get('start')
		end = request.args.get('end')
		
		dateFilter = dateFilter + "FILTER (?event_beg_time <= \"%sT00:00:00Z\"^^xsd:dateTime) . \n FILTER(?event_end_time >= \"%sT00:00:00Z\"^^xsd:dateTime)." % (end, start)
		
	locationFilter = ""
	
	if 's' in request.args and 'w' in request.args and 'n' in request.args and 'e' in request.args:
		south = request.args.get('s')
		west = request.args.get('w')
		north = request.args.get('n')
		east = request.args.get('e')
		
		locationFilter = " FILTER ( ?venue_latitude >= %s && ?venue_latitude <= %s &&  ?venue_longitude >= %s && ?venue_longitude <= %s) ." % (south, north, west, east)
		
	
	#Get all the venues
	sparql = PREFIX + """SELECT DISTINCT ?venue ?venue_type ?venue_title ?venue_description ?venue_shortDescription ?venue_openingHours ?venue_locationAdress ?venue_latitude ?venue_longitude ?venue_email ?venue_homepage ?venue_geometry WHERE {
					?venue a ah:Venue .
					?venue ah:venueType ?venue_type .
					?venue dc:title ?venue_title .
					?event ah:venue ?venue.
					?event ah:production ?event_production .
					?event_production ah:genre ?event_genre .
					?event time:hasBeginning ?event_beg_time .
					?event time:hasEnd ?event_end_time .
					OPTIONAL {?venue dc:description ?venue_description .}
					OPTIONAL {?venue ah:shortDescription ?venue_shortDescription .}
					OPTIONAL {?venue ah:openingHours ?venue_openingHours .}
					OPTIONAL {?venue ah:locationAddress ?venue_locationAdress .}			   			   
					OPTIONAL {?venue geo:lat ?venue_latitude .}
					OPTIONAL {?venue geo:long ?venue_longitude .}
					OPTIONAL {?venue vcard:email ?venue_email .}
					OPTIONAL {?venue foaf:homepage ?venue_homepage .}
					OPTIONAL {?venue geo:geometry ?venue_geometry .}""" + type_filter + genre_filter + dateFilter + locationFilter + "}" 
	
	print sparql
	
	# Run the query
	response = runQuery(sparql, 'JSON', jsoni=False)
	venues = json.loads(response)
	
	# Indices of duplicate venues
	venuesToRemove = []
	# Venue homepages of checked venues
	venuesVisited = []
	for binding in venues["results"]["bindings"]:
		venueURI = binding["venue"]["value"]
		
		# Try to get the venue homepage, to uniquely identify it
		# Additional venues with the same homepage will be removed
		try:
			if "venue_homepage" in binding: 
				venueHomePage = binding["venue_homepage"]["value"]		
				# print 'venue homepage: ' + venueHomePage
				
				# Check if venue is known
				if venueHomePage not in venuesVisited:
					# Add venue to the list of known venues
					venuesVisited.append(venueHomePage)
					
					# Get the events for this venue										
					events_data = json.loads(getEventsByVenue(venueURI, genre_filter, dateFilter))
					records = processEventData(events_data)					
					# Add the events data to the response
					binding["events"] = [record for record in records]	
				else:
					# Find the index of the duplicate venue
					ind = venues["results"]["bindings"].index(binding)
					# Add it to be removed
					venuesToRemove.append(ind)
			# In case the venue does not have a homepage key
			else:
				# Get the events for this venue										
				events_data = json.loads(getEventsByVenue(venueURI, genre_filter, dateFilter))
				records = processEventData(events_data)					
				# Add the events data to the response
				binding["events"] = [record for record in records]
		
		except Exception as e:
			app.logger.error('Something went wrong')
			app.logger.error(e)
			
	# Remove all venue duplicates
	for i in sorted(venuesToRemove, reverse=True):
		del venues["results"]["bindings"][i]
			
	return jsonify(venues)
	
def processEventData(events_data):
	
	records = []
	
	try:	
		events = events_data["results"]["bindings"]
		
		for event in events:
			record = []					

			title = event["event_title"]["value"]
			description = event["event_description"]["value"]
			beginning = event["event_beg_time"]["value"]
			end = event["event_end_time"]["value"]
			genre = event["event_genre"]["value"]
			
			record.append({
				"title":title,
				"description":description,
				"beginning":beginning,
				"end":end,
				"genre":genre
				})			
			records.append(record)
	except Exception as e:
			app.logger.error('Something went wrong')
			app.logger.error(e)
	return records
	
def getEventsByVenue(venueURI, genre_filter="", dateFilter=""):
	sparql = PREFIX + """SELECT DISTINCT ?event_title ?event_genre ?event_status ?event_description ?event_beg_time ?event_end_time WHERE {
			?event a ah:Event .
			?event dc:title ?event_title .
			?event ah:production ?event_production .
			?event_production ah:genre ?event_genre .
			OPTIONAL {?event ah:venue ?event_venue .}
			OPTIONAL {?event ah:eventStatus ?event_status .}			
			OPTIONAL {?event ah:room ?event_room .}
			OPTIONAL {?event dc:description ?event_description .}
			OPTIONAL {?event ah:cidn ?event_cidn .}
			OPTIONAL {?event time:hasBeginning ?event_beg_time}
			OPTIONAL {?event time:hasEnd ?event_end_time}
			FILTER(?event_venue = <%s>)""" % (venueURI,) + genre_filter + dateFilter + "}" 
			
	return runQuery(sparql, 'JSON', jsoni=False)

#Get infos from dbpedia on venues/city
@app.route('/dbpedia', methods=['GET'])
def getDBPediaInfos():
	venue = request.args.get('venue')
	city = request.args.get('city')
	sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
	venueQuery = DBP_PREFIX + """SELECT ?abstract ?link ?location ?architect_name ?current_use
							WHERE {
							  ?sub dbpediaowl:name '"""+ venue +"""' @nl;
								dbpediaowl:abstract ?abstract;
								dbpediaowl:wikiPageExternalLink ?link.
							  OPTIONAL {
								?sub nldbpedia:locatie ?location.
							  }
							  OPTIONAL {
								?sub dbpedia-owl:currentlyUsedFor ?current_use.
							  }
							  OPTIONAL {
								?sub dbpedia-owl:architect ?architect.
								?architect nldbpedia:naam ?architect_name .
							  }
							} LIMIT 1"""
	sparql.setQuery(venueQuery)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	infos = results["results"]["bindings"]
	if infos == []:
		cityQuery = DBP_PREFIX + """SELECT ?abstract ?link
									WHERE {
									  ?city rdf:type dbpedia-owl:Municipality; 
										rdfs:label ?name;
										dbpedia-owl:abstract ?abstract;
										dbpedia-owl:wikiPageExternalLink ?link.
										FILTER contains(?name, '"""+ city +"""').
									} LIMIT 1"""
		sparql.setQuery(cityQuery)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		infos = results["results"]["bindings"]
		return json.dumps({"city" : processCityData(infos)})	
	
	return json.dumps({"venue" : processVenueData(infos)})

def processVenueData(venueInfo):
	record = []
	for venue in venueInfo:
		abstract = venue["abstract"]["value"]
		link = venue["link"]["value"]
		if venue["location"]["type"] == "literal" or venue["location"]["type"] == "typed-literal":
			location = venue["location"]["value"]
		else:
			location = ""
		if venue["architect_name"]["type"] == "literal" or venue["architect_name"]["type"] == "typed-literal":
			architect = venue["architect_name"]["value"]
		else:
			architect = ""
		current_use = venue["current_use"]["value"]
			
		record.append({
			"abstract": abstract,
			"link": link,
			"location":location,
			"architect":architect,
			"current_use":current_use
			})
	return record
	
def processCityData(cityInfo):
	record = []
	for city in cityInfo:
		abstract = city["abstract"]["value"]
		link = city["link"]["value"]
		record.append({
			"abstract": abstract,
			"link": link
			})
	return record
    
if __name__ == '__main__':    
    app.run(debug=True)

from flask import Flask, render_template, url_for, request, jsonify, Response, json
from SPARQLWrapper import SPARQLWrapper, RDF, JSON, XML, N3
from StringIO import StringIO
import requests
import json
import urllib2

app = Flask(__name__)

#Local endpoint
SPARQL_ENDPOINT = 'http://localhost:8080/openrdf-sesame/repositories/IWA-AH'

#ArtsHolland sparql endpoint
AH_ENDPOINT = 'http://api.artsholland.com/sparql'

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
    app.logger.debug('You arrived at ' + url_for('sparql'))
    app.logger.debug('I received the following arguments' + str(request.args) )
	
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
            
            app.logger.debug('Results were returned, yay!')
            
            #app.logger.debug(response)
            
            if return_format == 'RDF':
                app.logger.debug('Serializing to Turtle format')
                return response.serialize(format='turtle')
            else :
                app.logger.debug('Directly returning JSON format')
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
	sparql = PREFIX + "SELECT DISTINCT ?genre ?genre_name WHERE { ?genre rdf:type ah:Genre. ?genre rdfs:label ?genre_name} ORDER BY ASC(?genre_name)"

	# Run the query
   	return runQuery(sparql, 'JSON') 
	
# Get a list of all venue types
@app.route('/venueTypes', methods=['GET'])
def getVenueTypes():
	sparql = PREFIX + "SELECT DISTINCT ?venue_type ?venue_type_name WHERE {?venue ah:venueType ?venue_type. ?venue_type rdfs:label ?venue_type_name}"

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

	filter = ""
	
	if 'type' in request.args:
		type = request.args.getlist('type', None)
		filter = filter + " FILTER(?venue_type IN ("
		for item in type:
			filter = filter + item + ","
		filter = filter[:-1]
		filter = filter + "))"
	
	#Get all the venues
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
	response = runQuery(sparql, 'JSON', jsoni=False)
	venues = json.loads(response)
	toRemove = []
	for binding in venues["results"]["bindings"]:
		venueURI = binding["venue"]["value"]
		events_data = json.loads(getEventsByVenue(venueURI))
		
		events = events_data["results"]["bindings"]
		records = []
		for event in events:
			records.append(event["event"]["value"])

		binding["events"] = [dict(event=record) for record in records]	
			
	return jsonify(venues)
	
def getEventsByVenue(venueURI):
	sparql = PREFIX + """SELECT DISTINCT * WHERE {
			?event a ah:Event .
			?event dc:title ?event_title .
			OPTIONAL {?event ah:venue ?event_venue .}
			OPTIONAL {?event ah:eventStatus ?event_status .}
			OPTIONAL {?event ah:production ?event_production .}
			OPTIONAL {?event ah:room ?event_room .}
			OPTIONAL {?event dc:description ?event_description .}
			OPTIONAL {?event ah:cidn ?event_cidn .}
			OPTIONAL {?event time:hasBeginning ?event_beg_time}
			OPTIONAL {?event time:hasEnd ?event_end_time}
			FILTER(?event_venue = <%s>)
			}""" % (venueURI,)
			
	return runQuery(sparql, 'JSON', jsoni=False)	
    
if __name__ == '__main__':    
    app.run(debug=True)
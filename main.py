from flask import Flask, render_template, url_for, request, jsonify
from SPARQLWrapper import SPARQLWrapper, RDF, JSON
import requests
import json
import urllib2

app = Flask(__name__)

SPARQL_ENDPOINT = 'http://localhost:8080/openrdf-sesame/repositories/IWA-AH'

PREFIX = """PREFIX dc:<http://purl.org/dc/terms/>
		PREFIX onto:<http://www.ontotext.com/>
		PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#>
		PREFIX foaf:<http://xmlns.com/foaf/0.1/>
		PREFIX vcard:<http://www.w3.org/2006/vcard/ns#>
		PREFIX gn:<http://www.geonames.org/ontology#>
		PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
		PREFIX time:<http://www.w3.org/2006/time#>
		PREFIX search:<http://rdf.opensahara.com/search#>
		PREFIX osgeo:<http://rdf.opensahara.com/type/geo/>
		PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
		PREFIX owl:<http://www.w3.org/2002/07/owl#>
		PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
		PREFIX sesame:<http://www.openrdf.org/schema/sesame#>
		PREFIX gr:<http://purl.org/goodrelations/v1#>
		PREFIX fn:<http://www.w3.org/2005/xpath-functions#>
		PREFIX ah:<http://purl.org/artsholland/1.0/>
		PREFIX bd:<http://www.bigdata.com/rdf/search#>"""


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
def runQuery(query, return_format, endpoint=SPARQL_ENDPOINT):
    if endpoint and query :
        sparql = SPARQLWrapper(endpoint)
        
        sparql.setQuery(query)
        
        if return_format == 'RDF':
            sparql.setReturnFormat(RDF)
        else :
            sparql.setReturnFormat('JSON')
            sparql.addCustomParameter('Accept','application/sparql-results+json')
        
        app.logger.debug('Query:\n{}'.format(query))
        
        app.logger.debug('Querying endpoint {}'.format(endpoint))
        
        try :
            response = sparql.query().convert()
            
            app.logger.debug('Results were returned, yay!')
            
            #app.logger.debug(response)
            
            if return_format == 'RDF':
                app.logger.debug('Serializing to Turtle format')
                return response.serialize(format='turtle')
            else :
                app.logger.debug('Directly returning JSON format')
                return jsonify(response)
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
		
	sparql = PREFIX + """SELECT DISTINCT * WHERE {
					?venue a ah:Venue .
					?venue ah:venueType ?venue_type .
					?venue dc:title ?venue_title .
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
    
if __name__ == '__main__':    
    app.run(debug=True)
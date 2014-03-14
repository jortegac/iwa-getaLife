from flask import Flask, render_template, url_for, request, jsonify, Response, json
from SPARQLWrapper import SPARQLWrapper, RDF, JSON, XML, N3
from StringIO import StringIO
import requests
import json
import urllib2

#ArtsHolland sparql endpoint
AH_ENDPOINT = 'http://api.artsholland.com/sparql'

#Very shitty way to deal with output file
#Change my value 
OUTPUT = "c:\Users\jortega\Documents\Personal\Vu\IntelligentWebApplications\Final Project\iwa-getaLife\extra\AH RDF data\dump.n3"

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

# Test method to dump AH data to a file
# Tries to get all the data available from ArtsHolland but for only those things that are relevant for events that are beyond 2014-03-12. 
# Doesn't really make sense to have data that won't be used.
def test():
	response = ""
	for i in range(0, 200):
		print i
		offset = 50*i
		query = PREFIX + """CONSTRUCT {
						?Venue ah:locationAddress ?LocationAdress ;
						ah:openingHours ?OpeningHours ;
						ah:shortDescription ?VenueShortDescription ;
						ah:venueType ?VenueType ;
						dc:description ?VenueDescription ;
						dc:title ?VenueTitle ;
						a ah:Venue ;
						geo:geometry ?Geometry ;
						geo:lat ?Latitude ;
						geo:long ?Longitude ;
						vcard:email ?Email ;
						foaf:homepage ?Homepage .
						?Event ah:eventStatus ?Status ;
						ah:production ?Production ;
						ah:room ?Room ;
						ah:venue ?Venue ;
						dc:description ?Description ;
						dc:title ?Title ;
						a ah:Event ;
						time:hasBeginning ?BeginningTime ;
						time:hasEnd ?EndTime ;
						owl:sameAs ?SameAs .
						?Production ah:genre ?Genre ;
						ah:languageNoProblem ?LangProblem ;
						ah:shortDescription ?ProductionShortDescription ;
						dc:description ?ProductionDescription ;
						dc:title ?ProductionTitle ;
						a ah:Production ;
						owl:sameAs ?ProductionSameAs .
						?Genre rdfs:label ?Label .					
						}
						WHERE
						{
						{
						?Event ah:venue ?Venue ;
						ah:production ?Production ;
						dc:description ?Description ;
						dc:title ?Title ;
						a ah:Event ;					
						ah:venue ?Venue ;
						dc:description ?Description ;
						a ah:Event ;
						time:hasBeginning ?BeginningTime ;
						time:hasEnd ?EndTime ;
						owl:sameAs ?SameAs .
						OPTIONAL {?Event ah:room ?Room } .
						?Production ah:genre ?Genre ;
						ah:languageNoProblem ?LangProblem ;
						ah:shortDescription ?ProductionShortDescription ;
						dc:description ?ProductionDescription ;
						dc:title ?ProductionTitle ;
						a ah:Production ;
						owl:sameAs ?ProductionSameAs .
						?Venue dc:title ?VenueTitle .
						?Venue a ah:Venue .
						OPTIONAL {?Venue ah:locationAddress ?LocationAdress }.
						OPTIONAL {?Venue ah:openingHours ?OpeningHours }.
						OPTIONAL {?Venue ah:shortDescription ?VenueShortDescription }.
						OPTIONAL {?Venue ah:venueType ?VenueType }.
						OPTIONAL {?Venue dc:description ?VenueDescription }.
						OPTIONAL {?Venue owl:sameAs ?VenueSameAs }.
						OPTIONAL {?Venue geo:lat ?Latitude }.
						OPTIONAL {?Venue geo:long ?Longitude }.
						OPTIONAL {?Venue vcard:email ?Email .}
						OPTIONAL {?Venue foaf:homepage ?Homepage }.
						OPTIONAL {?Venue geo:geometry ?Geometry }.
						?Genre rdfs:label ?Label.
						FILTER (?EndTime > "2014-03-12T00:00:00Z"^^xsd:dateTime)
						}	
						} LIMIT 50 OFFSET %d """ % (offset,)
		
		sparql = SPARQLWrapper(AH_ENDPOINT)        
		sparql.setQuery(query)        
		sparql.setReturnFormat(N3)
		
		response = response + sparql.query().convert()
	
	text_file = open(OUTPUT, "w")
	text_file.write(response)
	text_file.close()
	
	return "YEAH"
	
if __name__ == '__main__':    
    test()
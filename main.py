from flask import Flask, render_template, url_for, request, jsonify
import requests
import json
import urllib2

app = Flask(__name__)

TUTORIAL_REPOSITORY = 'http://localhost:8080/openrdf-sesame/repositories/IWA-AH'

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/sparql', methods=['GET'])
def sparql():
    app.logger.debug('You arrived at ' + url_for('sparql'))
    app.logger.debug('I received the following arguments' + str(request.args) )
    
    endpoint = request.args.get('endpoint', None)
    query = request.args.get('query', None)
    
    return_format = request.args.get('format','JSON')
    
    
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
            
            app.logger.debug(response)
            
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

    
if __name__ == '__main__':
    app.debug = False
    app.run()
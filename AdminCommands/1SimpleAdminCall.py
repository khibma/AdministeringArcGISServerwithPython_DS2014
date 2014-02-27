# Required imports
import urllib
import urllib2
import json

#http://arcola:6080/arcgis/admin/www/doc/index.html#/Stop_Service/02w00000006v000000/

def getToken(username, password, server, port, exp=60):        

    query_dict = {'username':   username,
                  'password':   password,
                  'expiration': str(exp),
                  'client':     'requestip',
                  'f': 'json'} 

    tokenURL = "http://{}:{}/arcgis/admin/generateToken".format(server, port)
    
    tokenResponse = urllib.urlopen(tokenURL, urllib.urlencode(query_dict))
    tokenOuput = json.loads(tokenResponse.read())
        
    if "token" not in tokenOuput:
        print tokenOuput['messages']
    else:
        # Return the token, expiry and URL            
        return tokenOuput['token']


    
    
# STARTS HERE #    

user = "myadminuser"
pass = "myadminpass"    
server = "myserver"
port = "6080"  
service = "Service.GPServer"  #MyMapService.MapServer

token = getToken(user, pass, server, port)
print token


URL = "http://{}:{}/arcgis/admin".format(server, port)


# Encode the query string
query_dict = {"token": token,
              "f" : "json"}
query_string = urllib.urlencode(query_dict) 

#Build up the URL
stopURL = URL + "/services/{0}/{1}".format(service, "start")
print stopURL


#Send the request
jsonResponse = urllib.urlopen(stopURL, urllib.urlencode(query_dict))


#Load the JSON response
jsonOuput = json.loads(jsonResponse.read())
print jsonOuput


# Check to make sure we got the expected result
if jsonOuput['status'] == "success":
    print (str(service) + " was stopped")
else:            
    print status



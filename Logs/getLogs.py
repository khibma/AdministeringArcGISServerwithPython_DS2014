import urllib, urllib2, json


def gentoken(server, port, adminUser, adminPass, expiration=60):
    # function to get a token required for Admin connections
    #
    
    query_dict = {'username':   adminUser,
                  'password':   adminPass,
                  'expiration': str(expiration),
                  'client':     'requestip'}
    
    query_string = urllib.urlencode(query_dict)
    url = "http://{0}:{1}/arcgis/admin/generateToken".format(server, port)
    
    token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())
        
    if "token" not in token:        
        print token['messages']
        quit()
    else:
        return token['token']

    

def getLogAsJSON(server, port, adminUser, adminPass, starttime, endtime):
    # Based on a given service, starttime, and endtime, get the logs
    #
    
    token = gentoken(server, port, adminUser, adminPass)  
    
    logParams = {}
    logParams["token"] = token
    logParams["f"] = "json"  #pjson
    if endtime > 0: #this is oldest time, LIKE 8:00 AM          
        logParams["endTime"] = endtime
    if starttime > 0: # this is newest time, LIKE 8:15 AM         
        logParams["startTime"] = starttime
    logParams["level"] = "FINE"
    logParams["filterType"] = "json"
    logParams["pageSize"] = 5000
    logParams["filter"] = {"codes":[],
                           "processIds":[],
                           "server":"*",
                           "services":[],   #[service],
                           "machines":"*"}   

    query_string = urllib.urlencode(logParams)
    url = "http://{}:{}/arcgis/admin/logs/query".format(server, port)
        
    return json.loads(urllib.urlopen(url, query_string).read())
      
        

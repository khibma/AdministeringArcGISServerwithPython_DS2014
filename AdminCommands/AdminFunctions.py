'''
Date : Feb, 2014

This script provides functions used to administer ArcGIS Server 10.1+.
Most functions below make calls to the REST Admin, using specific URLS to perform an action.
The functions below DO NOT make use of arcpy, as such they can be run on any machine with Python 2.7.x installed
This list is not intended to be a complete list of functions to work with ArcGIS Server. It does provide the most common
actions and templates to extend or a place to start your own.
See the REST Admin API for comprehensive commands and explanation.
Examples on how the functions are called can be found at the bottom of this file.

These scripts provided as samples and are not supported through Esri Technical Support.
Please direct questions to either the Python user forum : http://forums.arcgis.com/forums/117-Python
or the ArcGIS Server General : http://forums.arcgis.com/forums/8-ArcGIS-Server-General

See the ArcGIS Server help for interactive scripts and further examples on using the REST Admin API through Python:
http://resources.arcgis.com/en/help/main/10.1/#/Scripting_ArcGIS_Server_administration/0154000005p3000000/

'''

# Required imports
import urllib
import urllib2
import json
import sys
import time


class ADMINCON(object):    
    
    def __init__(self, username, password, server, port):
        self.username = username
        self.password = password
        self.server   = server
        self.port     = port
        self.token, self.expires, self.URL = self.getToken(username, password, server, port)
        self.basicQ = "?f=pjson&token={}".format(self.token)
        
    def getToken(self, username, password, server, port, exp=60):        

        query_dict = {'username':   username,
                      'password':   password,
                      'expiration': str(exp),
                      'client':     'requestip',
                      'f': 'json'} 

        tokenURL = "http://{}:{}/arcgis/admin/generateToken".format(server, port)
        token = sendAGSReq(tokenURL, query_dict) 
            
        if "token" not in token:
            print token['messages']
            exit()
        else:
            # Return the token, expiry and URL            
            return token['token'], token['expires'], "http://{}:{}/arcgis/admin".format(server, port)
        
    def checkExpiredToken(self):
        # call to check if token time limit has elapsed, if so, request a new one
        # server time in epoch values        
        if (self.expires) < int(time.time() * 1000):
            self.token, self.expires, self.URL = self.getToken(self.username, self.password, self.server, self.port)
            print "Obtained new token"
        else:
            print "Token is still valid"

### helper functions ###      

def sendAGSReq(URL, query_dict):
    #
    # Takes a URL and a dictionary and sends the request, returns the JSON
    
    query_string = urllib.urlencode(query_dict)    
    
    jsonResponse = urllib.urlopen(URL, urllib.urlencode(query_dict))
    jsonOuput = json.loads(jsonResponse.read())
    
    return jsonOuput    
        
def checkMSG(jsonMSG):
    #
    # Takes JSON and checks if a success message was found
    
    try:
        if jsonMSG['status'] == "success":
            return True
        else:
            return False
    except:
        return False
    
### //helper functions ###     
    
def modifyLogs(clearLogs, logLevel):
    ''' Function to clear logs and modify log settings.
    clearLogs = True|False
    logLevel = SEVERE|WARNING|FINE|VERBOSE|DEBUG
    '''        
   
    # Clear existing logs
    if clearLogs:
        clearStatus = sendAGSReq(CON.URL + "/logs/clean" + CON.basicQ, '') 
        if checkMSG(clearStatus['status']):
            print "Cleared log files"
       
    # Get the current logDir, maxErrorReportsCount and maxLogFileAge as we dont want to modify those
    logSettings = sendAGSReq(CON.URL + "/logs/settings" + CON.basicQ, '') 
    logSettingProps = logSettings['settings']  
    
    # Place the current settings, along with new log setting back into the payload
    logLevel_dict = {"logDir": logSettingProps['logDir'],
                     "logLevel": logLevel,
                     "maxErrorReportsCount": logSettingProps['maxErrorReportsCount'],
                     "maxLogFileAge": logSettingProps['maxLogFileAge']                       
                    }
   
    # Modify the logLevel
    logStatus = sendAGSReq(CON.URL + "/logs/settings/edit" + CON.basicQ, logLevel_dict)     
    
    if checkMSG(logStatus):
        print "Successfully changed log level to {}".format(logLevel)        
    else:
        print "Log level not changed:\n" + logStatus
        
    return
        
        
def createFolder(folderName, folderDescription):
    ''' Function to create a folder
    folderName = String with a folder name
    folderDescription = String with a description for the folder
    '''     
    
    # Dictionary of properties to create a folder
    folderProp_dict = { "folderName": folderName,
                        "description": folderDescription
                      }
    
    folder_encode = urllib.urlencode(folderProp_dict)            
    folderStatus = sendAGSReq(CON.URL + "/services/createFolder" + CON.basicQ, folderProp_dict)  
    
    if checkMSG(folderStatus):
        print "Created folder: {}".format(folderName)
    else:
        print "Could not create folder:\n" + str(folderStatus)
        
    return
        

def getFolders():
    ''' Function to get all folders on a server     
    '''        

    foldersList = sendAGSReq(CON.URL + "/services" + CON.basicQ, '')      
    folders = foldersList["folders"]
    
    # Return a list of folders to the function which called for them
    return folders


def renameService(service, newName):
    ''' Function to rename a service
    service = String of existing service with type separated by a period <serviceName>.<serviceType>
    newName = String of new service name  
    '''       
    
    service = urllib.quote(service.encode('utf8'))  
    
    # Check the service name for a folder:
    if "//" in service:
        serviceName = service.split('.')[0].split("//")[1]
        folderName = service.split('.')[0].split("//")[0] + "/" 
    else:
        serviceName = service.split('.')[0]
        folderName = ""
    
    renameService_dict = { "serviceName": serviceName,
                           "serviceType": service.split('.')[1],
                           "serviceNewName" : urllib.quote(newName.encode('utf8')) 
                         }
     
    renameStatus = sendAGSReq(CON.URL + "/services/renameService" + CON.basicQ, renameService_dict)  
    
    if checkMSG(renameStatus):
        print "Successfully renamed service to : {}".format(newName)
    else:
        print "Could not rename service:\n" + renameStatus
        
    return

 
def stopStartServices(stopStart, serviceList):  
    ''' Function to stop, start or delete a service.
    stopStart = Stop|Start|Delete
    serviceList = List of services. A service must be in the <name>.<type> notation
    '''    
    
    # modify the services(s)    
    for service in serviceList:
        status = sendAGSReq(CON.URL + "/services/{}/{}".format(service, stopStart) + CON.basicQ, '')  
        
        if checkMSG(status):
            print (str(service) + " === " + str(stopStart))
        else:            
            print status
    
    return 
   


def getServiceList():
    ''' Function to get all services
    Note: Will not return any services in the Utilities or System folder
    '''      
    
    services = []    
    folder = ''        
    serviceList = sendAGSReq(CON.URL + "/services" + CON.basicQ, '')  

    # Build up list of services at the root level
    for single in serviceList["services"]:
        services.append(single['serviceName'] + '.' + single['type'])
     
    # Build up list of folders and remove the System and Utilities folder (we dont want anyone playing with them)
    folderList = serviceList["folders"]
    folderList.remove("Utilities")             
    folderList.remove("System")        

    for folder in folderList:                      
        fList = sendAGSReq(CON.URL + "/services/{}".format(folder) + CON.basicQ, '')  
        for single in fList["services"]:
            services.append(folder + "//" + single['serviceName'] + '.' + single['type'])                
    
    print services    
    return services


def getServerInfo():
    ''' Function to get and display a detailed report about a server    
    '''    
    
    report = ''
    report += "*-----------------------------------------------*\n\n"
    
    # Get Cluster and Machine info
    jCluster = sendAGSReq(CON.URL + "/clusters" + CON.basicQ, '')  
       
    if len(jCluster["clusters"]) == 0:        
        report += "No clusters found\n\n"
    else:    
        for cluster in jCluster["clusters"]:    
            report += "Cluster: {} is {}\n".format(cluster["clusterName"], cluster["configuredState"])            
            if len(cluster["machineNames"])     == 0:
                report += "    No machines associated with cluster\n"                
            else:
                # Get individual Machine info
                for machine in cluster["machineNames"]:       
                    jMachine = sendAGSReq(CON.URL + "/machines/{}".format(machine) + CON.basicQ, '')  
                    report += "    Machine: {} is {}. (Platform: {})\n".format(machine, jMachine["configuredState"],jMachine["platform"])                    
        
                    
    # Get Version and Build
    jInfo = sendAGSReq(CON.URL + "/info" + CON.basicQ, '') 
    report += "\nVersion: {}\nBuild:   {}\n\n".format(jInfo ["currentversion"], jInfo ["currentbuild"])
      

    # Get Log level   
    jLog = sendAGSReq(CON.URL + "/logs/settings" + CON.basicQ, '') 
    report += "Log level: {}\n\n".format(jLog["settings"]["logLevel"])
     
    
    #Get License information
    jLicense = sendAGSReq(CON.URL + "/system/licenses" + CON.basicQ, '') 
    report += "License is: {} / {}\n".format(jLicense["edition"]["name"], jLicense["level"]["name"])    
    if jLicense["edition"]["canExpire"] == True:
        import datetime
        d = datetime.date.fromtimestamp(jLicense["edition"]["expiration"] // 1000) #time in milliseconds since epoch
        report += "License set to expire: {}\n".format(datetime.datetime.strftime(d, '%Y-%m-%d'))        
    else:
        report += "License does not expire\n"        
    
        
    if len(jLicense["extensions"]) == 0:
        report += "No available extensions\n"        
    else:
        report += "Available Extensions........\n"   
        for name in jLicense["extensions"]:            
            report += "extension:  {}\n".format(name["name"])            
               
    
    report += "\n*-----------------------------------------------*\n"
    
    print report
    

def securityReport():
    ''' Get the security settings on the Server
    '''
    
    securityReport = sendAGSReq(CON.URL + "/security/config" + CON.basicQ, '')      

    print "\n  ==Security settings==\n"
    for k, v in securityReport.iteritems():
        if type(v) == dict:
            print "{0}...".format(k)
            for sK, sV in v.iteritems():
                print "{0:14}{1:13} : {2}".format(" ", sK, sV)
        else:
            print "{0:27} : {1}".format(k, v)    
    
    return
    

def listRoles():
    ''' List all the current roles on the Server
    '''
    
    roleList = sendAGSReq(CON.URL + "/security/roles/getRoles" + CON.basicQ, '')      
    
    if len(roleList['roles']) == 0:
        print "\nNo Roles found. Is security enabled?"
    else:
        print "\n___Roles___"
        for role in roleList['roles']:
            for k, v in role.iteritems():
                if k == 'rolename':
                    print v
                if k == 'description':
                    print " ... {0}".format(v)
    
    return


def listUsers():
    ''' List all the users in the server security store
    '''
    
    userList = sendAGSReq(CON.URL + "/security/users/getUsers" + CON.basicQ, '')      
    
    if len(userList['users']) == 0:
        print "No Users found. Is security enabled?"
    else:
        print "\n___Users___"
        for user in userList['users']:
            for k, v in user.iteritems():
                print "{0:11} : {1}".format(k, v)
    
    return

    
def listUsersInRole(role):
    ''' List all users that belong to a given role
    '''
   
    userList = sendAGSReq(CON.URL + "/security/roles/getUsersWithinRole" + CON.basicQ, {"rolename": role}) 
    if len(userList['users']) >0:
        print "Found these users in '{0}' role...".format(role)
        for user in userList['users']:
            print user
    else:
        print "No users found in '{0}' role".format(role)
    

def listRolesByUser(user):
    ''' List all roles that a given user belongs to
    '''
    
    roleList = sendAGSReq(CON.URL + "/security/roles/getRolesForUser" + CON.basicQ, {"username": user}) 
    if len(roleList['roles']) >0:
        print "Found these roles for '{0}'...".format(user)
        for role in roleList['roles']:
            print role
    else:
        print "No roles found for '{0}'".format(user)
    

def exportSite(pathToExport):
    ''' Export (make a backup) of the AGS Site.
    A directory is given, the file will be created with the date and suffix of .agssite
    '''
    
    exportJSON = sendAGSReq(CON.URL + "/exportSite" + CON.basicQ, {"location": pathToExport}) 
    if checkMSG(exportJSON):
        print "Exported site to {0}".format(exportJSON['location'])
    else:
        print exportJSON
        
    

##### EXAMPLE CALLS TO ABOVE FUNCTIONS #####

CON = ADMINCON('admin', 'admin', 'arcola', 6080)

# Clear log files and change to Debug:
modifyLogs(True, "DEBUG")

# Check on the token
CON.checkExpiredToken()

# Create a folder:
createFolder("testServices", "Folder for test services")

# Get a list of folders and assign to a variable:
serverFolders = getFolders()
print serverFolders

# Rename a service
renameService("Buffer.GPServer", "BufferPolys")

# Stop, start or delete a service
serviceList = ["PolyCover.GPServer","BufferPolys.GPServer"]
stopStartServices("Stop", serviceList)

# Get a list of services
serviceList = getServiceList()
for service in serviceList:
    print service

# Get information about the server
getServerInfo()

# Security...list users and roles
securityReport()
listRoles()
listUsers()
listUsersInRole("KevinUser")
listUsersInRole("RestrictedPublishers")
listRolesByUser("kevin")

# Backup the site to a directory
exportSite(r"c:\arcgisserver")


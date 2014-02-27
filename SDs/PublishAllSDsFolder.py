'''
This script looks in a given directory for "SD" (service definition) files.
These files are then published to a given server (.ags connection file).
Because the script requires arcpy, it must be run on a machine with ArcGIS installed.
'''

import arcpy
import os

SDdirectory = r"d:\demos\DS2014\REST_ADMIN_w_PYTHON\SDs"
Server = r"d:\demos\DS2014\REST_ADMIN_w_PYTHON\SDs\arcola6080.ags"

#Walk through a directory, looking for .SD files
for dirpath, dirname, filenames in os.walk(SDdirectory):
    for filename in filenames:
        if filename.endswith(".sd"):
            serviceName = os.path.splitext(filename)[0]
            sd = os.path.join(dirpath, filename)
            print "Publishing : {0}".format(sd)
            
            #Publish
            r = arcpy.UploadServiceDefinition_server(sd, Server, serviceName)
            msgs = r.getMessages()
            if "Succeeded" in msgs:
                print "Published: {0}".format(serviceName)
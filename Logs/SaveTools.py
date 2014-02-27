import csv
import os
import arcpy


def logToCSV(log, table):
    ''' turn the raw json into a raw csv log file on disk
    '''
    
    fieldNames = ["type", "message", "time", "source", "machine", "user",
                  "code", "elapsed", "process", "thread", "methodName"]  
     
    wfile  = open(table, 'wb')
    csvwriter = csv.writer(wfile)
    
    logMessages = log["logMessages"]
    rowIndex = 0
    fields = []
    csvwriter.writerow(fieldNames)
    
    for message in logMessages:
        row = []
        for field in fieldNames:
            row.append(str(message[field]))
        csvwriter.writerow(row)
        
    wfile.close()   

    return


def logToTable(log, outtable):
    
    fieldTypes = {"type": "TEXT",
                  "message": "TEXT",
                  "time": "TEXT",
                  "source": "TEXT",
                  "machine": "TEXT",
                  "user": "TEXT",
                  "code": "LONG",
                  "elapsed": "DOUBLE",
                  "process": "TEXT",
                  "thread": "TEXT",
                  "methodName": "TEXT"}
   
    arcpy.env.overwriteOutput = True

    outpath = os.path.dirname(outtable)
    outname = os.path.basename(outtable)
    arcpy.CreateTable_management(outpath, outname)

    arcpy.AddMessage(outtable)

    logMessages = log["logMessages"]
    
    rowIndex = 0
    fields = []
                       
    for message in logMessages:
        if rowIndex == 0:
            for field in message.keys():
                fields.append(field)
                fieldType = fieldTypes[field]
                arcpy.AddField_management(outtable, field, fieldType)
            tablerows = arcpy.da.InsertCursor(outtable, fields)
                    
        row = []
        for field in fields:
            fieldType = fieldTypes[field]
            if fieldType == "LONG":
                row.append(int(message[field]))
            elif fieldType == "DOUBLE":
                if len(str(message[field])) == 0:
                    row.append(0)
                else:
                    row.append(float(message[field]))
            else:
                row.append(str(message[field]))
            
        tablerows.insertRow(row)
        rowIndex = rowIndex + 1

    
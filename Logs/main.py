import os
import datetime, time

import getLogs
import SaveTools


def getTimeRanges(howOften):
    ''' Supports single integers representing a day
        can support more if more if-statements with multipler gets added
    '''
    
    # 60seconds * 60minutes * 24hours * 1000milliseconds * #of days
    backTrack = 60 * 60 * 24 * 1000 * int(howOften)    

    starttime = int(time.time() * 1000)    
    endtime= int((time.time() * 1000) - backTrack)

    return [starttime, endtime] 
   

if __name__ == "__main__":      

        
    # server connection information
    server = "arcola"
    port = "6080"
    adminUser = "admin"
    adminPass = "admin"
   
    # where to persist logs    
    tableDir = r"D:\Demos\DS2014\REST_ADMIN_w_Python\Logs\SaveLog"
    
    # Get how often logs are collected. This is used to calculate the date that many days in the past
    # to properly query the AGS Logs
    timeRange = 7     
    timeInfo = getTimeRanges(timeRange)
    
    # get logs.
    print "Getting logs from Server"
    log = getLogs.getLogAsJSON(server, port, adminUser, adminPass, timeInfo[0], timeInfo[1])		 
             
    # Write the raw file out
    theDate = time.strftime('%Y_%m_%d', time.localtime(timeInfo[1] / 1000)) 
    
    print "Writing logs to CSV"
    csvTable = os.path.join(tableDir, str(theDate) + "_raw.csv")                
    SaveTools.logToCSV(log, csvTable) 
    
    #Convert CSV into an ArcGIS fGDB table
    print "Writing logs to DBF"
    dbfbTable = os.path.join(tableDir, "log_" +str(theDate) + "_raw.dbf") 
    SaveTools.logToTable(log, dbfbTable)


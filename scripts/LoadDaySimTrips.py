#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Name:        LoadDaySimTrips
# Purpose:     Loads key info: otaz, dtaz, deptm, arrtm, mode, half, etrps to a sqlite database for running queries 
#              This function is useful for checking information coming out of DaySim.   
# Author:      Chetan Joshi, Portland OR
# Dependencies:csv, sqlite3, time 
# Created:     1/7/2016
#              
# Copyright:   (c) Chetan Joshi 2016
# Licence:     Permission is hereby granted, free of charge, to any person obtaining a copy
#              of this software and associated documentation files (the "Software"), to deal
#              in the Software without restriction, including without limitation the rights
#              to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#              copies of the Software, and to permit persons to whom the Software is
#              furnished to do so, subject to the following conditions:
#
#              The above copyright notice and this permission notice shall be included in all
#              copies or substantial portions of the Software.
#
#              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#              SOFTWARE.
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
import csv
import sqlite3
import time

def GetDaySimTripsDB1(daysimtripfilepath):
    '''usage: -> put the script in python site packages and then use as below
       import LoadDaySimTrips
       conn, trip_data = LoadDaySimTrips.GetDaySimTripsDB(daysimtripfilepath)
       
       daysimtripfilepath = full path and file name for the daysim trips file
       conn = connection to db
       trip_data = db table
       *the db is an in memory db
       
       For details on using sqlite and db queries, see: https://docs.python.org/2/library/sqlite3.html#
    '''
    start = time.time()
    print 'Start reading daysim trips...'
    #tripsfile = open(r'C:\Projects\DVRPC Model\Visum\PA\Output\_trip_2.dat', 'rb')  #Check this path...
    tripsfile = open(daysimtripfilepath, 'rb')
    reader = csv.DictReader(tripsfile, delimiter='\t')
    
    conn = sqlite3.connect(':memory:')
    trip_data = conn.cursor()
    trip_data.execute("CREATE TABLE trips(otaz INT, dtaz INT, deptm INT, arrtm INT, mode INT, half INT, etrps DOUBLE)")
    conn.commit()

    for row in reader:   #assuming data might have some issues
        try:
            otaz = int(row['otaz'])
            dtaz = int(row['dtaz'])
            deptm = int(row['deptm'])
            arrtm = int(row['arrtm'])
            mode = int(row['mode'])
            half = int(row['half'])
            etrps = 1.0*float(row['trexpfac']) #expanded trips
        except:
            print 'Could not batch - ', row
        
        try:
            trip_data.execute("insert into trips values ((?),(?),(?),(?), (?), (?), (?))",(otaz, dtaz, deptm, arrtm, mode, half, etrps))
            conn.commit()
        except:
            print 'Could not commit - ', row

    tripsfile.close()
    print 'Finished pushing trips to sqlite db in ', time.time()-start, 'secs' 
    return conn, trip_data


def GetDaySimTripsDB2(daysimtripfilepath):
    '''usage: -> put the script in python site packages and then use as below
       import LoadDaySimTrips
       conn, trip_data = LoadDaySimTrips.GetDaySimTripsDB(daysimtripfilepath)
       
       daysimtripfilepath = full path and file name for the daysim trips file
       conn = connection to db
       trip_data = db table
       *the db is an in memory db
       
       For details on using sqlite and db queries, see: https://docs.python.org/2/library/sqlite3.html#
    '''
    start = time.time()
    print 'Start reading daysim trips...'
    #tripsfile = open(r'C:\Projects\DVRPC Model\Visum\PA\Output\_trip_2.dat', 'rb')  #Check this path...
    tripsfile = open(daysimtripfilepath, 'rb')
    reader = csv.DictReader(tripsfile, delimiter='\t')

    conn = sqlite3.connect(':memory:')
    trip_data = conn.cursor()
    trip_data.execute("CREATE TABLE trips(otaz INT, dtaz INT, deptm INT, arrtm INT, mode INT, half INT, etrps DOUBLE)")
    conn.commit()

    #data = [[row['otaz'], row['dtaz'], row['deptm'], row['arrtm'], row['mode'], row['half'], 1.0*float(row['trexpfac'])] for row in reader] # alternative list comprehension
    data = []

    for row in reader:   #TO DO: Load data into temp array and push all of it together using -> executemany(...) 
        data.append([int(row['otaz']), int(row['dtaz']), int(row['deptm']), int(row['arrtm']), int(row['mode']), int(row['half']), 1.0*float(row['trexpfac'])])
    tripsfile.close()
    
    data = map(tuple, data) # not sure if it is really needed... need to check proper way to do this
    trip_data.executemany("insert into trips values (?,?,?,?,?,?,?)", data)
    conn.commit()
    del data
    
    print 'Finished pushing trips to sqlite db in ', time.time()-start, 'secs' 
    return conn, trip_data

#--- usage | in general the first variant takes twice the time, but examines each row one at a time -------- #
dsfile = r"C:\Projects\Tests\data\_trip_2.dat"
##
##cnxn, trip_dat = GetDaySimTripsDB1(dsfile)
##
##del cnxn, trip_dat

cnxn, trip_dat = GetDaySimTripsDB2(dsfile)

del cnxn, trip_dat







































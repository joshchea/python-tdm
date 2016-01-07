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

def GetDaySimTripsDB(daysimtripfilepath):
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
    reader = csv.reader(tripsfile, delimiter='\t')

    header = reader.next()
    ix = dict(zip(header, range(0, len(header))))

    conn = sqlite3.connect(':memory:')
    trip_data = conn.cursor()
    trip_data.execute("CREATE TABLE trips(otaz INT, dtaz INT, deptm INT, arrtm INT, mode INT, half INT, etrps DOUBLE)")
    conn.commit()

    for row in reader:
        otaz = int(row[ix['otaz']])
        dtaz = int(row[ix['dtaz']])
        deptm = int(row[ix['deptm']])
        arrtm = int(row[ix['arrtm']])
        mode = int(row[ix['mode']])
        half = int(row[ix['half']])
        etrps = 1.0*float(row[ix['trexpfac']]) #expanded trips
        trip_data.execute("insert into trips values ((?),(?),(?),(?), (?), (?), (?))",(otaz, dtaz, deptm, arrtm, mode, half, etrps))
        conn.commit()

    tripsfile.close()
    print 'Finished pushing trips to sqlite db in ', time.time()-start, 'secs' 
    return conn, trip_data



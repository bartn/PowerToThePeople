#!/usr/bin/python
# filename: datademo.py 
# a simple script to pull some data from a MySQL table

from time import time, strftime, asctime, sleep

import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="eindhoven", db="energylogging")

#create a cursor for the select
cursor = db.cursor()

#execute an sql query
#cur.execute("SELECT firstname,lastname FROM test.name")

# loop to iterate
#for row in cur.fetchall() :
      #data from rows
 #       firstname = str(row[0])
  #      lastname = str(row[1])

      #print i
   #     print "This Person's name is " + firstname + " " + lastname

watt_average = 12
time = strftime('%Y%m%d %H:%M')
# Prepare SQL query to INSERT a record into the database.
sql = "INSERT INTO logger(time, \
       averagewatt) \
       VALUES ('%s', '%s')" % \
       (time, watt_average)
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Commit your changes in the database
   db.commit()
   
except:
   # Rollback in case there is any error
   db.rollback()

# disconnect from server
db.close()
"""Script to import certain fields from Embrace export into PowerSchool.

https://github.com/Philip-Greyson/D118-Embrace-PowerSchool-Import

Connects to the Embrace SFTP server using the connection details they provided to us and pulls the latest poweriep file.
Then takes the information from just the desired columns and exports it in a tab delimited file starting with the student ID number.
Takes that file and uploads it to our local SFTP server in order to be imported into PowerSchool

Needs pysftp: pip install pysftp --upgrade
"""

# importing modules
import csv  # needed to parse the csv file
import datetime  # used to get current date for course info
import os  # needed to get environement variables
from datetime import *

# import oracledb  # used to connect to PowerSchool database
import pysftp  # used to connect to the Performance Matters sftp site and upload the file

EMBRACE_SFTP_UN = os.environ.get('EMBRACE_SFTP_USERNAME')  # username for the embrace sftp server
EMBRACE_SFTP_PW = os.environ.get('EMBRACE_SFTP_PASSWORD')  # password for the embrace sftp server
EMBRACE_SFTP_HOST = os.environ.get('EMBRACE_SFTP_ADDRESS')  # ip address/URL for the embrace sftp server

CNOPTS = pysftp.CnOpts(knownhosts='known_hosts')  # connection options to use the known_hosts file for key validation

D118_SFTP_UN = os.environ.get('D118_SFTP_USERNAME')  # username for the d118 sftp server
D118_SFTP_PW = os.environ.get('D118_SFTP_PASSWORD')  # password for the d118 sftp server
D118_SFTP_HOST = os.environ.get('D118_SFTP_ADDRESS')  # ip address/URL for the d118 sftp server

# Variables to change based on different use cases
EMBRACE_FILE_NAME = 'poweriep-students.csv'
EMBRACE_FILE_DIRECTORY = './files'
OUTPUT_FILE_NAME = 'embrace_fields.txt'
OUTPUT_FILE_DIRECTORY = 'sftp/embrace'
STUDENT_ID_COLUMN = 4  # which column the student ID number is in in the embrace export file, 0 indexed
COLUMNS_TO_EXPORT = [43]  # which other columns from the csv to include in the output file

print(f'Embrace SFTP Username: {EMBRACE_SFTP_UN} | Embrace SFTP Password: {EMBRACE_SFTP_PW} | Embrace SFTP Server: {EMBRACE_SFTP_HOST}')  # debug so we can see what info sftp connection is using
print(f'D118 SFTP Username: {D118_SFTP_UN} | D118 SFTP Password: {D118_SFTP_PW} | D118 SFTP Server: {D118_SFTP_HOST}')  # debug so we can see what info sftp connection is using

if __name__ == '__main__':  # main file execution
    with open('embraceImportLog.txt', 'w', encoding='utf-8') as log:  # open logging file
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'INFO: Execution started at {startTime}')
        print(f'INFO: Execution started at {startTime}', file=log)

        try:
            # Connect to Embrace SFTP server and pull down the file we need to process
            with pysftp.Connection(EMBRACE_SFTP_HOST, username=EMBRACE_SFTP_UN, password=EMBRACE_SFTP_PW, cnopts=CNOPTS) as sftp:
                print(f'INFO: SFTP connection to Embrace at {EMBRACE_SFTP_HOST} successfully established')
                print(f'INFO: SFTP connection to Embrace at {EMBRACE_SFTP_HOST} successfully established', file=log)
                sftp.chdir(EMBRACE_FILE_DIRECTORY)
                # print(sftp.pwd)
                # print(sftp.listdir())
                sftp.get(EMBRACE_FILE_NAME, 'embrace_file.csv')  # just save the file to the local directory and call it embrace_file.csv
        except Exception as er:
            print(f'ERROR while connecting to Embrace SFTP server: {er}')
            print(f'ERROR while connecting to Embrace SFTP server: {er}', file=log)

        try:
            # Process the downloaded file, extract the fields we care about and export it into a new import file
            with open('embrace_file.csv', encoding='utf-8') as inputFile:  # open the file saved above
                with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as outputFile:  # open a new output file that we will upload to PowerSchool
                    lines = csv.reader(inputFile, delimiter=',')  # open the input file as a csv file https://docs.python.org/3/library/csv.html
                    for line in lines:  # go through each line in the csv, which is an individual student
                        try:  # each line can go into a try block so we can skip a single line/student in the event of an error
                            fields = []  # create blank list each line for each student's data
                            studentNum = line[STUDENT_ID_COLUMN]
                            for column in COLUMNS_TO_EXPORT:  # go through the list of columns we want, and append them to our fields data list
                                fields.append(line[column])
                            if all(values == '' for values in fields):  # check to see if all our values that we got above are blank, so we can skip that student from the output
                                # print(f'WARN: {studentNum} has no data in selected columns')  # debug to see who has no data in the columns we care about
                                print(f'WARN: {studentNum} has no data in selected columns', file=log)
                            else:
                                if studentNum == '':  # check to see if there is no student ID number for the student
                                    print(f'WARN: {line[1]} {line[2]}, embrace ID {line[0]} does not have a student ID number, skipping')
                                else:
                                    outputString = studentNum + "\t"  # start the output string with their student id number and a tab for delimiting
                                    for i in range(len(fields)):  # go through our fields and append them to our output string
                                        outputString = outputString + fields[i] + '\t'
                                    outputString = outputString.rstrip(outputString[-1])  # use rstrip to remove just the last character of the output string, which is an additional \t delimiter that is not needed
                                    print(outputString)
                                    print(outputString, file=outputFile)  # output the string to our file that is imported to PowerSchool
                        except Exception as er:
                            print(f'ERROR while processing student {line[STUDENT_ID_COLUMN]}: {er}')
                            print(f'ERROR while processing student {line[STUDENT_ID_COLUMN]}: {er}', file=log)
        except Exception as er:
            print(f'ERROR while opening local csv file for processing: {er}')
            print(f'ERROR while opening local csv file for processing: {er}', file=log)

        try:
            # Now connect to the D118 SFTP server and upload the file to be imported into PowerSchool
            with pysftp.Connection(D118_SFTP_HOST, username=D118_SFTP_UN, password=D118_SFTP_PW, cnopts=CNOPTS) as sftp:
                print(f'INFO: SFTP connection to D118 at {D118_SFTP_HOST} successfully established')
                print(f'INFO: SFTP connection to D118 at {D118_SFTP_HOST} successfully established', file=log)
                # print(sftp.pwd)  # debug to show current directory
                # print(sftp.listdir())  # debug to show files and directories in our location
                sftp.chdir(OUTPUT_FILE_DIRECTORY)
                # print(sftp.pwd) # debug to show current directory
                # print(sftp.listdir())  # debug to show files and directories in our location
                sftp.put(OUTPUT_FILE_NAME)  # upload the file to our sftp server
        except Exception as er:
            print(f'ERROR while connecting to D118 SFTP server: {er}')
            print(f'ERROR while connecting to D118 SFTP server: {er}', file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'INFO: Execution ended at {endTime}')
        print(f'INFO: Execution ended at {endTime}', file=log)


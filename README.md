# D118-Embrace-PowerSchool-Import

Script to upload certain fields (for us just transportation info) from Embrace into PowerSchool. Connects to the embrace SFTP server, grabs the file, goes through each student seeing if there is information in the desired columns, and if so, adds them to the output tab delimited .txt file. Then uploads the .txt file to our local SFTP server to be imported into PowerSchool.

## Overview

This is a fairly simple script to just grab certain fields from our Embrace IEP information and get them into PowerSchool. Right now, we are only using this for transportation information which is just one field, but it should have the capability to easily include as many fields as desired in case we need it in the future.
The script first connects to our Embrace SFTP server instance using the login information provided by Embrace, and pulls down the PowerIEP file which contains the information we need.
This file is then opened and processed by the script. It uses the Python csv library to parse each line into lists, then goes through each line (one student's data) and creates a list which includes their student ID number and the fields we care about. If the fields are empty, the student is skipped in the export. If there *is* information, the student ID number and the designated fields are exported to a tab delimited .txt output file.
That file is finally uploaded to a local SFTP server, which we setup to have PowerSchool pull from in a scheduled AutoComm import.

## Requirements

The following Environment Variables must be set on the machine running the script:

- EMBRACE_SFTP_USERNAME
- EMBRACE_SFTP_PASSWORD
- EMBRACE_SFTP_ADDRESS
- D118_SFTP_USERNAME -*This can be replaced with an environment variable of the username of your specific SFTP server*
- D118_SFTP_PASSWORD - *This can be replaced with an environment variable of the password of your specific SFTP server*
- D118_SFTP_ADDRESS - *This can be replaced with an environment variable of the host address of your specific SFTP server*

Additionally,the following Python libraries must be installed on the host machine (links to the installation guide):

- [pysftp](https://pypi.org/project/pysftp/)

**As part of the pysftp connection to the SFTP server, you must include the server hosts key in a file** with no extension named "known_hosts" in the same directory as the Python script. You can see [here](https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-cnopts) for details on how it is used, but the easiest way to include this I have found is to create an SSH connection from a Linux machine using the login info and then find the key (the newest entry should be on the bottom) in ~/.ssh/known_hosts and copy and paste that into a new file named "known_hosts" in the script directory.
You will need to include both the Embrace and your local SFTP host key in this file as it is used for both connections (though it could be split out if desired without much work).

You will also need a SFTP server running and accessible that is able to have files written to it in the directory /sftp/embrace/ or you will need to customize the script (see below) In order to import the information into PowerSchool, a scheduled AutoComm job should be setup, that uses the managed connection to your SFTP server, and imports into student_number,  and whichever custom fields you need based on the data. The field delimiter is a tab, and the record delimiter is LF with the UTF-8 character set. That setup is a bit out of the scope of this readme.

## Customization

While this is a fairly specific script to our uses here at D118, I did write it so that it could be as flexible as possible. Things you might want to change:

- `EMBRACE_FILE_NAME` is the name of the file you will be pulling from the Embrace SFTP server. If this is not the poweriep file you will want to change it to the correct. Similarly, `EMBRACE_FILE_DIRECTORY` is the path to the directory that the file is found within on the Embrace server.
- Mirroring the above, `OUTPUT_FILE_NAME` and `OUTPUT_FILE_DIRECTORY` are the names of the output file and the directory in which is should be placed on the local SFTP server. This will then be where you will need to set up the AutoComm into PowerSchool from (if you are going that route)
- `STUDENT_ID_COLUMN` is an integer that equates to the column number that the student ID number can be found in the Embrace poweriep file. It is zero indexed, so Column A is 0, B is 1, etc. Our student ID numbers are found in column E, which is why I have it set to 4. If this information is found in a different column, or a different method for identifying the students should be used, it can be changed to the relevant column number.
- `COLUMNS_TO_EXPORT` is a list of integers that contains any of the columns that should be exported for each student. In our case it is a single column/field, but this list can be extended as much as desired. As with the student ID column, it is 0 indexed for column A.
- If you are not going to use a local SFTP server to AutoComm from or aren't importing into PowerSchool, you can comment out the block under `# Now connect to the D118 SFTP server and upload the file to be imported into PowerSchool` as it would no longer be necessary.

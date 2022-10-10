# PayrollCostingAudit

A program written in Python 3 to reconcile the detail payroll register to the detail costing reports produced by the Oracle Cloud ERP payroll system. The program performs the following audit steps on each payroll element for each employee in the detailed payroll register:

- Validates the existence of all payroll and costing element names against a master list referred to as the "elements file". 
- Recalculates net pay for each employee on the payroll register.
- Verifies that the correct general ledger accounts are debited and credited for each element on the costing file(s).
- Verifies that all debits and credits balance for each payroll element for each employee on the costing file(s). 
- Reconciles the debits and credits for each pay element on the costing file(s) to the payroll register.

Any situation that is inconsistent with the aforementioned items is treated by the program as an error or exception. The program outputs a spreadsheet with a tab for each of the following items:

- A list of all entries on the payroll register and costing files(s) that are considered "problematic".
- A correcting journal entry that can be posted to fix the problematic entries.
- A log of all errors and exceptions encountered during the audit process.
- A reconciliation in T-account format.

The program will terminate and report an error if it encounters a run-time error. For example, if the element file or the config.json file are not properly updated or formatted.

## License

_PayrollCostingAudit_ is licensed under the MIT License. Please read the LICENSE.txt file included herein for more information.

## Installation

The first step to installing and running _PayrollCostingAudit_ is to be sure that Python 3 is installed on your computer. If you are planning to use this program on your work computer, then please consult your system administrator or IT department for assistance installing Python 3.

To determine if Python 3 is already installed on your computer, open a command line terminal, type the following, and press _Enter_:

```
python3 --version
```
If Python 3 is already installed then you will see the following displayed (the actual numbers may be different, depending upon the version of Python that is installed on your computer):
```
Python 3.10.6
```
Otherwise, please proceed to https://www.python.org/downloads/ to download a copy of Python 3 and obtain installation instructions for Python.

Once Python is installed on your computer you can download _PayrollCostingAudit_ by navitating to this repository https://github.com/herrsmitty8128/PayrollCostingAudit, clicking on the green _Code_ drop-down menu, and then clicking on _Download Zip_. 

![How to download PayrollCostingAudit](https://github.com/herrsmitty8128/PayrollCostingAudit/blob/main/img/download_menu.png)

Then download the zip file to a local directory of your choosing, where you should then extract everything in the zip file. Once the files are extracted and Python 3 is installed. You should proceed to the _Dependencies_ section below.

## Dependencies

Most of the modules required by _PayrollCostingAudit_ are included with Python 3. However, there are two exceptions (listed below):

- openpyxl (see https://pypi.org/project/openpyxl/ for more information)
- pandas (see https://pypi.org/project/pandas/ for more information)

These modules can be installed by opening a command line terminal and running the following command:

```
python3 -m pip install openpyxl pandas
```

On MS Windows, if you are not logged in as a system administator then pip will default to a local user installation. If this occurs, then you should be sure to include the full path to the local user installation directory in the "Local Install Paths" listing in the config.json file that accompanies _PayrollCostingAudit_.

On Linux, if you are not logged in as a root user then be sure to prepend the commands above with _sudo_.

## Instructions for Use

There are three basic steps required to use _PayrollCostingAudit_:

1. Create/update the elements CSV file
2. Update the config.json file
3. Run the app.py python script

### Step 1: Create or update the elements CSV file with a list of all payroll and costing elements.

The elements file contains a list of all payroll elements, which costing elements they correspond to, and which general ledger accounts should be debited and credited by each element. _PayrollCostingAudit_ uses this file as a master list against which all payroll and costing elements are compared. During the audit process, any situation that is inconsistent with the information in this file is considered by the program as an error or exception.

Each payroll element and costing element must appear only once in the file and there must be a one-to-one relationship between the two. If an element appears more than one time in the file, or if the payroll and costing elements do not have a one-to-one relationship, then _PayrollCostingAudit_ can not produce accruate results.

The elements file is a data table in CSV format using ANSI encoding. It must contain each of the following headers:

- "Payroll Name": The name of the payroll element.
- "Payroll Category": The category name of the payroll element.
- "Costing Name": The name of the costing element.
- "Costing Category": The category name of the costing element.
- "Debit Account": A semicolon delimited list of the general ledger account numbers that are permitted to be debited by the corresponding element.
- "Credit Account": A semicolon delimited list of the general ledger account numbers that are permitted to be credited by the corresponding element.
- "Should Cost": A boolean field that indicates whether or not the corresponding payroll element should be costed. The value of this field must be either "TRUE" or "FALSE". If the value for an element is "FALSE" then that element is excluded from the audit process.

The full path and filename of the elements file must be saved in the "Elements File" field of the config.json file that accompanies _PayrollCostingAudit_. The elements file can be saved in any location that is accessible by the user. You can also give the file a name of your choosing. However, the file MUST be in CSV format using ANSI encoding and include all the aforementioned fields for all payroll and costing elements.

Below is a short example of the element file viewed in a text editor. Most popular spreadsheet applications also support CSV file format and can be used to create and edit the file.

```CS
"Payroll Name","Payroll Category","Costing Name","Costing Category","Debit Account","Credit Account","Should Cost"
"Regular pay","Earnings","Regular payroll","Reg Earnings",54000;53000;51000,21000,TRUE
"FIT Withheld","Withholdings","Federal Tax Withheld","Employee Withholdings",22000;23000,21000,TRUE
```

### Step 2: Update the config.json file that accompanies _PayrollCostingAudit_.

The config.json file is a file that contains the information necessary for the processing of _PayrollCostingAudit_. The file uses Javascript Object Notation ("JSON") file format. Please refer to https://www.w3schools.com/js/js_json.asp for a tutorial about the JSON format. The value of each field in the file described below must be valid before _PayrollCostingAudit_ can be executed.

- "Name Substitutions": A set of name:value pairs used to replace an element's name with another name. This is useful in situations where elements in the payroll register do not have a one-to-one relationship with elements on the costing register.
- "Input Files": A list of the full path and filename of all the input files. Input files should consist of one or more detail payroll registers and one or more detailed costing registers.
- "Output File": The full path and filename of the outputfile that will contain the results of the audit.
- "Local Install Paths": A list of one or more paths to the directory(ies) where local user installation of Python modules are located. These paths are added to the Python interpreter's environment at run time to ensure that it can locate any user specific installations of Python modules.
- "Elements File": The full path and filename of the elements file (described in Step 1, above) in CSV format using ANSI encoding.

Here is an example of the config.json file as viewed with a text editor:

```json
{
    "Name Substitutions": {
        "FIT Withheld": "Federal Income Tax Withholding",
        "SIT Withheld": "State Income Tax Withholding"
    },
    "Input Files": [
        "c:/my directory/input files/costing file1",
        "c:/my directory/input files/costing file2",
        "c:/my directory/input files/payroll register"
    ],
    "Output File": "c:/my directory/output files/output file PPD12",
    "Local Install Paths": [
        "c:/users/username/program files/python/scripts",
        "c:/users/username/program files/python/other stuff"
    ],
    "Elements File": "c:/my directory/output files/output file PPD12"
}
```

### Step 3: Run the app.py python script.

_PayrollCostingAudit_ can be executed by opening a command line terminal, navigating to the directory where you extracted the program files, typing _python3 app.py_, pressing _Enter_. For example:

```
cd c:/users/your username/a directory/another directory/PayrollCostingAudit
python3 app.py
```
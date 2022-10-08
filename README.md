# PayrollCostingAudit

A program written in Python 3 to reconcile the detail payroll register to the detail costing reports produced by a certain cloud-based ERP payroll system. 

## License

_PayrollCostingAudit_ is licensed under the MIT License. Please read the LICENSE.txt file included herein for more information.

## Installation

The first step to installing and running _PayrollCostingAudit_ is to be sure that Python 3 is installed on your computer. If you are planning to use this program on your work computer, then please consult your system administrator or IT department for assistance installing Python 3.

To determine if Python 3 is already installed on your computer, open a command line terminal, type the following, and press _Enter_:

```
python3 --version
```
*or*
```
python --version
```
If Python 3 is already installed then you will see the following displayed (the actual numbers may be different, depending upon the version of Python that is installed on your computer):
```
Python 3.10.6
```
Otherwise, please proceed to https://www.python.org/downloads/ to download a copy of Python 3 and obtain installation instructions for Python.

Once Python is installed on your computer you can download _PayrollCostingAudit_ by clicking on the green _Code_ drop-down menu and then click on _Download Zip_.

![How to download PayrollCostingAudit](https://github.com/herrsmitty8128/PayrollCostingAudit/blob/main/img/download_menu.png)

## Dependencies

Most of the modules required by _PayrollCostingAudit_ are included with Python 3. However, there are two exceptions (listed below):

- openpyxl (see https://pypi.org/project/openpyxl/ for more information)
- pandas (see https://pypi.org/project/pandas/ for more information)

These modules can be installed by opening a command line terminal and running the following command:

```
python3 -m pip install openpyxl pandas
```
*or*
```
python -m pip install openpyxl pandas
```

On MS Windows, if you are not logged in as a system administator then pip will default to a local user installation. If this occurs, then you should be sure to include the full path to the local user installation directory in the "Local Install Paths" listing in the config.json file that accompanies _PayrollCostingAudit_.

On Linux, if you are not logged in as a root user then be sure to prepend the commands above with _sudo_.

## Instructions for Use
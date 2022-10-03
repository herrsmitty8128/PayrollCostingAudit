
import json
import os
import sys
import openpyxl
import Element
import Reconciliation
import pandas as pd
from datetime import datetime


def create_xlsx_with_tables(file_name: str, descriptors: list) -> None:
    '''
    Creates a new xlsx file with multiple tables in separate sheets, each built from a different pandas DataFrame.

    file_name:  The path to the new xlsx file.
                The file will be over-written if it already exists

    descriptor: A list of dicts describing each table.
                For example: [{'sheet_name': 'sheetname1',
                               'data_frame': df,
                               'display_name': 'displayname1'
                               },
                              {'sheet_name': 'sheetname2',
                               'data_frame': df2,
                               'display_name': 'displayname2'
                               }]
    '''

    file_name = os.path.abspath(file_name)

    with pd.ExcelWriter(file_name) as writer:
        for desc in descriptors:
            df = desc['data_frame']
            if not df.index.name:
                df.index.name = 'Id'
            df.to_excel(writer, sheet_name=desc['sheet_name'])

    wb = openpyxl.load_workbook(filename=file_name)

    for desc in descriptors:
        df = desc['data_frame']
        xlscols = [
            'A', 'B', 'C', 'D', 'E', 'F',
            'G',
            'H',
            'I',
            'J',
            'K',
            'L',
            'M',
            'N',
            'O',
            'P',
            'Q',
            'R',
            'S',
            'T',
            'U',
            'V',
            'W',
            'X',
            'Y',
            'Z',
            'AA',
            'AB',
            'AC',
            'AD',
            'AE',
            'AF',
            'AG',
            'AH',
            'AI',
            'AJ',
            'AK',
            'AL',
            'AM',
            'AN',
            'AO',
            'AP',
            'AQ',
            'AR',
            'AS',
            'AT',
            'AU',
            'AV',
            'AW',
            'AX',
            'AY',
            'AZ',
            'BA',
            'BB',
            'BC',
            'BD',
            'BE',
            'BF',
            'BG',
            'BH',
            'BI',
            'BJ',
            'BK',
            'BL',
            'BM',
            'BN',
            'BO',
            'BP',
            'BQ',
            'BR',
            'BS',
            'BT',
            'BU',
            'BV',
            'BW',
            'BX',
            'BY',
            'BZ',
            'CA',
            'CB',
            'CC',
            'CD',
            'CE',
            'CF',
            'CG',
            'CH',
            'CI',
            'CJ',
            'CK',
            'CL',
            'CM',
            'CN',
            'CO',
            'CP',
            'CQ',
            'CR',
            'CS',
            'CT',
            'CU',
            'CV',
            'CW',
            'CX',
            'CY',
            'CZ',
            'DA',
            'DB',
            'DC',
            'DD',
            'DE',
            'DF',
            'DG',
            'DH',
            'DI',
            'DJ',
            'DK',
            'DL',
            'DM',
            'DN',
            'DO',
            'DP',
            'DQ',
            'DR',
            'DS',
            'DT',
            'DU',
            'DV',
            'DW',
            'DX',
            'DY',
            'DZ']

        rows = df.shape[0] + 1
        cols = xlscols[df.shape[1]]
        refs = f'A1:{cols}{rows}'
        tab = openpyxl.worksheet.table.Table(displayName=desc['display_name'], ref=refs)
        wb[desc['sheet_name']].add_table(tab)

    wb.save(file_name)


def get_config() -> tuple:
    file_name = os.path.abspath('./config files/config.txt')
    with open(file_name) as f:
        data = json.load(f)
    input_files = ['./input files/' + f + '.csv' for f in data['Input files']]
    output_file = './output files/' + data['Output file name'] + ' ' + \
        datetime.today().isoformat(sep=' ', timespec='minutes').replace(':', '') + '.xlsx'
    return (input_files, output_file)


if __name__ == '__main__':

    # add the paths for locally installed modules
    sys.path.append(r'c:\users\smitchris\appdata\roaming\python\python39\site-packages')
    sys.path.append(r'C:\Users\smitchris\AppData\Roaming\Python\Python39\Scripts')

    print('Loading the configuration file...')
    filenames, analysis_file = get_config()

    print('Parsing the element lookup table...')
    element_table = Element.Parser.parse()

    print('Parsing the payroll files...')
    tree, errors = Reconciliation.Tree.build(filenames, element_table)

    if len(errors) > 0:
        print('PARSE ERRORS:')
        for err in errors:
            print(err)
        print('Number of parse errors:', len(errors))
    print('Number of parsed employees:', len(tree.tree))

    print('Reconciling payroll transactions...')
    errors = tree.reconcile()
    df0 = pd.DataFrame(errors)

    print('Building the table of problematic entries...')
    rows, headers = tree.build_unreconciled_entries()
    df1 = pd.DataFrame(rows, columns=headers)

    print('Building the correcting JE...')
    rows, headers = tree.build_correcting_je()
    df2 = pd.DataFrame(rows, columns=headers)

    print('Building the summary table...')
    rows, headers = tree.build_summary_table()
    df3 = pd.DataFrame(rows, columns=headers)

    print('Writing tables to', analysis_file)
    desc = [{'sheet_name': 'Problematic Entries',
             'data_frame': df1,
             'display_name': 'Problematic_Entries'},
            {'sheet_name': 'Correcting JE',
             'data_frame': df2,
             'display_name': 'Correcting_JE'},
            {'sheet_name': 'Summary Table',
             'data_frame': df3,
             'display_name': 'Summary_Table'},
            {'sheet_name': 'Errors',
             'data_frame': df0,
            'display_name': 'Errors'}]

    create_xlsx_with_tables(analysis_file, desc)

    print('RECONCILIATION COMPLETE.')

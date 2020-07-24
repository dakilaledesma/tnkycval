from __future__ import print_function

from flask import Flask, render_template, get_template_attribute
import flask

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys

"""
Taken from the Python version of Google's Sheets API Quickstart:
https://developers.google.com/sheets/api/quickstart/python
"""
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

response_ss_id = '1VfRA50cj9PO5sTcqdBrl8riJZqzcmWbpmoRZRlOJlOw'
data_ss_id = '1rH7K7ytcVMY-8k3piNH19z899FEJpZSD7G7p8-yUEKU'
SAMPLE_RANGE_NAME = 'A1:KFC25'

creds = None
if os.path.exists('tokens/token.pickle'):
    with open('tokens/token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'tokens/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('tokens/token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

data_sheet_read = sheet.values().get(spreadsheetId=data_ss_id, range="A:BK").execute()
data_sheet_values = data_sheet_read.get('values', [])

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    id = flask.request.args.get('uid')

    current_ids = sheet.values().get(spreadsheetId=response_ss_id,
                                     range="A1:B25").execute()

    values = current_ids.get('values', [])

    for row in range(1, len(values)):
        if id == values[row][0]:
            user_name = values[row][1]
            urow = row
            uid = id
            break
    else:
        return flask.jsonify({"result": 0})

    return flask.jsonify({"result": 1, "returns": [uid, urow, user_name]})


@app.route('/refresh_data_sheet')
def refresh_read_sheet():
    global data_sheet_read, data_sheet_values
    data_sheet_read = sheet.values().get(spreadsheetId=data_ss_id, range="A:BK").execute()
    data_sheet_values = data_sheet_read.get('values', [])

    return '1'


@app.route('/generate_dropdown')
def generate_dropdown():
    save_family = flask.request.args.get('save_family')
    urow = int(flask.request.args.get('urow'))

    response_sheet_read = sheet.values().get(spreadsheetId=response_ss_id,
                                             range=f"A{int(urow) + 1}:KFC{int(urow) + 1}").execute()
    response_sheet_values = response_sheet_read.get('values', [])[0]

    ret_string = f'''<input type="text" 
                            value="{save_family}" 
                            placeholder="Search family" 
                            id="familysearch" 
                            onkeyup="filterFunction()">

                     <div id="myDropdown" class="dropdown-content">'''

    family_array = []
    full_family_array = [str(row[54]).lower() for row in data_sheet_values]

    for row in range(1, len(data_sheet_values)):
        family_string = str(data_sheet_values[row][54]).lower()

        if family_string not in family_array and "*" in [data_sheet_values[row][58], data_sheet_values[row][59]]:
            all_occurrences = [i for i in range(len(full_family_array)) if full_family_array[i] == family_string]
            complete = 2

            for i in all_occurrences:
                include_species = "*" in [data_sheet_values[i][58], data_sheet_values[i][59]]
                occurrence_col = i + 9
                if response_sheet_values[occurrence_col] == '' and include_species:
                    complete = 0
                elif response_sheet_values[occurrence_col] == '*' and include_species:
                    complete = 1

            """
            For whatever reason, <br> breaks the dropdown list but <p></p> does not.
            """
            if complete == 2:
                ret_string += f'''  <p>
                                    </p>
                                    <a  href="javascript:;" 
                                        onclick="update_search(this.innerText)" 
                                        style="color: #75e091;">
                                    {family_string}
                                    </a>'''
            elif complete == 1:
                ret_string += f'''  <p>
                                    </p>
                                    <a  href="javascript:;" 
                                        onclick="update_search(this.innerText)" 
                                        style="color: yellow;">
                                    {family_string}
                                    </a>'''
            else:
                ret_string += f'''  <p>
                                    </p>
                                    <a  href="javascript:;" 
                                        onclick="update_search(this.innerText)" 
                                        style="color: white;">
                                    {family_string}
                                    </a>'''

            family_array.append(family_string)

    ret_string += "</div></div>"
    return ret_string


@app.route('/generate_result')
def generate_result():
    search_indices = flask.request.args.get('search_indices')
    if search_indices == '-1':
        urow = int(flask.request.args.get('urow'))
        ufamily = flask.request.args.get('ufamily')
        umajorgroup = flask.request.args.get('umajorgroup')
        utnstatus = flask.request.args.get('utnstatus')
        ukystatus = flask.request.args.get('ukystatus')
        uwetlanda = flask.request.args.get('uwetlanda')
        uwetlande = flask.request.args.get('uwetlande')
        usupport = flask.request.args.get('usupport')
        ufinished = flask.request.args.get('ufinished')
        uinvasives = flask.request.args.get('uinvasives')
        uotherc = flask.request.args.get('uotherc')
        udiffc = flask.request.args.get('udiffc')

        search_indices = f"{urow},{ufamily},{umajorgroup},{utnstatus},{ukystatus},{uwetlanda},{uwetlande},{usupport}," \
                         f"{ufinished},{uinvasives},{uotherc},{udiffc}"
    else:
        search_indices_list = search_indices.split(",")
        urow = int(search_indices_list[0])
        ufamily = search_indices_list[1]
        umajorgroup = search_indices_list[2]
        utnstatus = search_indices_list[3]
        ukystatus = search_indices_list[4]
        uwetlanda = search_indices_list[5]
        uwetlande = search_indices_list[6]
        usupport = search_indices_list[7]
        ufinished = search_indices_list[8]
        uinvasives = search_indices_list[9]
        uotherc = search_indices_list[10]
        udiffc = search_indices_list[11]
        
    minotherc, maxotherc = [int(val) for val in uotherc.split("-")]
    mindiffc, maxdiffc = [int(val) for val in udiffc.split("-")]

    response_sheet_read = sheet.values().get(spreadsheetId=response_ss_id, range=f"A1:KFC25").execute()
    response_sheet_values = response_sheet_read.get('values', [])

    def check_equality(search_parameter, found_value):
        if search_parameter == "any":
            return True
        elif search_parameter == found_value:
            return True
        elif search_parameter == "no" and found_value == "":
            return True
        elif search_parameter == "only" and found_value != "":
            return True
        else:
            return False
        
    def check_diff_range(min, max, found_value):
        if found_value == -2:
            return True
        elif min <= found_value <= max:
            return True
        else:
            return False

    ret_string = '''<h2>Search results</h2><table style="width:80%" id=customers>
                    <colgroup>
                        <col span="1" style="width: 25%;">
                        <col span="1" style="width: 5%;">
                        <col span="1" style="width: 30%;">
                        <col span="1" style="width: 5%;">
                        <col span="1" style="width: 30%;">
                        <col span="1" style="width: 5%;">
                    </colgroup>
                    
                    <th>Species</th>
                    <th>Your submitted C-value</th>
                    <th>Your submitted additional notes</th>
                    <th># of user submitted C-vals</th>
                    <th>User submitted notes</th>
                    <th>Submitted C-val range</th>'''

    new_search_indices = []
    for row in range(1, len(data_sheet_values)):
        cval_str = ""
        notes_str = ""

        num_other_c = 0
        num_other_notes = 0
        other_notes_str = ""
        max_c = -1
        min_c = -1

        species_col = int(row) + 9
        notes_col = int(row) + 3999

        if urow != -1:
            try:
                if response_sheet_values[urow][species_col] != '':
                    cval_str = response_sheet_values[urow][species_col]
            except IndexError:
                pass

            try:
                if response_sheet_values[urow][notes_col] != '':
                    notes_str = response_sheet_values[urow][notes_col]
            except IndexError:
                pass

        for user_index in range(1, len(response_sheet_values)):
            if response_sheet_values[user_index][1] != "Guest" and response_sheet_values[user_index][1] != "Dax":
                this_ucval = response_sheet_values[user_index][species_col]
                this_unotes = response_sheet_values[user_index][notes_col]

                if this_ucval != '' and this_ucval != '*':
                    num_other_c += 1

                    if max_c == -1 or int(this_ucval) > max_c:
                        max_c = int(this_ucval)

                    if min_c == -1 or int(this_ucval) < min_c:
                        min_c = int(this_ucval)

                if this_unotes != '':
                    num_other_notes += 1
                    other_notes_str += f"<b>{num_other_notes}</b>: {this_unotes}<br>"

        """
        Hard pulling values from the columns of interest to check if they fulfill the search
        """
        species_family = data_sheet_values[row][54].lower()
        species_major_group = data_sheet_values[row][56].lower()
        species_tn_status = data_sheet_values[row][50].lower()
        species_ky_status = data_sheet_values[row][51].lower()
        species_agcp_wetland_status = data_sheet_values[row][52].lower()
        species_emp_wetland_status = data_sheet_values[row][53].lower()
        species_support = data_sheet_values[row][57].lower()
        include_1 = data_sheet_values[row][58]
        include_2 = data_sheet_values[row][59]
        tn_invasive_value = data_sheet_values[row][60].lower()
        ky_invasive_value = data_sheet_values[row][61].lower()

        """
        Checking if species fulfill search requirements
        """
        if all([check_equality("any" if ufamily == "" else ufamily.lower(), species_family),
                check_equality(umajorgroup.lower(), species_major_group),
                check_equality(utnstatus.lower(), species_tn_status),
                check_equality(ukystatus.lower(), species_ky_status),
                check_equality(uwetlanda.lower(), species_agcp_wetland_status),
                check_equality(uwetlande.lower(), species_emp_wetland_status),
                check_equality(usupport.lower(), species_support),
                check_equality(ufinished.lower(), cval_str),
                check_diff_range(mindiffc, maxdiffc, max_c - min_c),
                (minotherc <= num_other_c <= maxotherc),
                True in [check_equality(uinvasives.lower(), tn_invasive_value),
                          check_equality(uinvasives.lower(), ky_invasive_value)],
                '*' in [include_1, include_2] or "" not in [tn_invasive_value, ky_invasive_value],
                ]):

            new_search_indices.append(str(row))
            ret_string += f'''  <tr>
                                    <td>
                                        <a  href="javascript:;" 
                                            class="species" 
                                            id="{data_sheet_values[row][1]}:lim:{cval_str}:lim:{notes_str}">
                                            {data_sheet_values[row][1]}
                                            {"(invasive)" if "" not in [tn_invasive_value, ky_invasive_value] else ""}
                                        </a>
                                    </td>
                                    <td>{cval_str}</td>
                                    <td>{notes_str}</td>
                                    <td>{str(num_other_c)}</td>
                                    <td>{other_notes_str[:-4] if num_other_notes != 0 else ""}</td>
                                    <td>{"N/A" if max_c == -1 else f"{min_c} to {max_c}"}</td>
                                </tr>'''

    ret_string += "</table>"
    return flask.jsonify({"returns": [-1, ret_string, search_indices]})
    

@app.route('/gather_species_info')
def gather_species_info():
    species_name = flask.request.args.get('species_name')
    cval = flask.request.args.get('cval')
    notes = flask.request.args.get('notes')

    species_row = -1
    for row in range(len(data_sheet_values)):
        if species_name.lower() == data_sheet_values[row][1].lower():
            species_row = row
            break

    if cval == "*":
        cval_default_select = '<option value="*" selected disabled hidden>Mark as seen/Skip</option>'
    elif cval == "":
        cval_default_select = '<option value="" selected disabled hidden>Select value</option>'
    else:
        cval_default_select = f'<option value="{cval}" selected hidden>{cval}</option>'

    option_string = ""
    for value in range(0, 11):
        option_string += f'<option value="{value}">{value}</option>'

    ret_string = f'''<table style="width:60%"
                            id=customers>
                        <tr>
                            <td>
                                <h2 id="species_name">{species_name}</h2>
                                <a target="_blank" 
                                    href="https://tnky.plantatlas.usf.edu/Plant.aspx?id={data_sheet_values[species_row][0]}">
                                    View {species_name} on the TNKY Plant Atlas</a>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <strong>Give this species a C-value: </strong>
                                <select id="ucval">{cval_default_select}
                                    {''.join([f'<option value="{value}">{value}</option>' for value in range(0, 11)])}
                                    <option value="*">Mark as seen/Skip</option>
                                    <option value="">Delete</option>
                                </select>
                                <input type="text" 
                                    id="speciesnotes" 
                                    placeholder="Additional notes" value="{notes}"/>
                                <input type="button" class="create" 
                                    value="Submit C-value" 
                                    id="submit_cval_button"/>
                            </td>
                        </tr>'''

    if "" not in [data_sheet_values[species_row][60], data_sheet_values[species_row][61]]:
        ret_string += f'''  <tr bgcolor="#ffe6e6">
                                <td>
                                    This species is invasive in Tennessee, as it was found in the 
                                    <a  target="_blank" 
                                        href="https://www.tnipc.org/invasive-plants/">
                                        TN-IPC Invasive Plants list
                                    </a>! 
                                    Recommended C-value for TN: {data_sheet_values[species_row][60]}
                                    <br>
                                    This species is invasive in Kentucky, as it was found in the 
                                    <a  target="_blank" 
                                        href="https://www.se-eppc.org/ky/KYEPPC_2013list.pdf">
                                        KY-EPPC Invasive Plants list
                                    </a>! 
                                    Recommended C-value for KY: {data_sheet_values[species_row][61]}
                                </td>
                            </tr>'''
    elif data_sheet_values[species_row][60] != "":
        ret_string += f'''  <tr bgcolor="#ffe6e6">
                                <td>
                                    This species is invasive in Tennessee, as it was found in the 
                                    <a target="_blank"
                                        href="https://www.tnipc.org/invasive-plants/">
                                        TN-IPC Invasive Plants list
                                    </a>! 
                                    Recommended C-value for TN: {data_sheet_values[species_row][60]}
                                </td>
                            </tr>'''
    elif data_sheet_values[species_row][61] != "":
        ret_string += f'''  <tr bgcolor="#ffe6e6">
                                <td>
                                    This species is invasive in Kentucky, as it was found in the 
                                    <a target="_blank" 
                                        href="https://www.se-eppc.org/ky/KYEPPC_2013list.pdf">
                                        KY-EPPC Invasive Plants list
                                    </a>! 
                                    Recommended C-value for KY: {data_sheet_values[species_row][61]}
                                </td>
                            </tr>'''

    ret_string +='</table><br>'

    temp_ret_string = f'''  {ret_string}
                            <hr width="60%">
                            <h2>C-values</h2>
                            <table style="width:60%" id=customers>
                                <th>Location</th>
                                <th>C-value</th>'''
    num_info = 0
    exclude_columns = [
        '"Appalachian Mountains of KY, TN, NC, SC, GA, AL"',
        "Coastal Plain of the Southeast",
        "Illinois",
        "Indiana",
        '"Interior Plateau of KY, TN, AL"',
        "Missouri",
        '"Piedmont Region of the Southeast NC, SC, GA, AL, MS, FL, TN, KY"',
        "Southern Coastal Plain",
        "West Virginia"
    ]

    for col in range(2, 47):
        if data_sheet_values[species_row][col] != "" and data_sheet_values[0][col] not in exclude_columns:
            temp_ret_string += f''' <tr>
                                        <td>{data_sheet_values[0][col]}</td>
                                        <td>{data_sheet_values[species_row][col]}</td>
                                    </tr>
                                '''
            num_info = num_info + 1

    temp_ret_string += '''  </table>
                            <br>'''

    ret_string = temp_ret_string if num_info != 0 else ret_string

    temp_ret_string = f'''  {ret_string}
                            <hr width="60%">
                            <h2>General Information</h2>
                            <table style="width:60%" id=customers>
                                <th>Information</th>
                                <th>Value</th>'''
    num_info = 0

    for col in range(47, 54):
        if data_sheet_values[species_row][col] != "":
            temp_ret_string += f''' <tr>
                                        <td>{data_sheet_values[0][col]}</td>
                                        <td>{data_sheet_values[species_row][col]}</td>
                                    </tr>
                                '''
            num_info = num_info + 1

    temp_ret_string += '''  </table>
                            <br>'''

    ret_string = temp_ret_string if num_info != 0 else ret_string

    return flask.jsonify({"returns": [species_row, ret_string]})


@app.route('/cval_to_sheet')
def cval_to_sheet():
    urow = int(flask.request.args.get('urow'))
    species_row = int(flask.request.args.get('species_row'))
    ucval = flask.request.args.get('ucval')
    unotes = flask.request.args.get('unotes')

    notes_col = species_row + 4000
    species_row += 10

    sheet.values().update(
        spreadsheetId=response_ss_id, range=f"R{int(urow) + 1}C{species_row}", valueInputOption="USER_ENTERED",
        body={"values": [[ucval]]}).execute()

    sheet.values().update(
        spreadsheetId=response_ss_id, range=f"R{int(urow) + 1}C{notes_col}", valueInputOption="USER_ENTERED",
        body={"values": [[unotes]]}).execute()
    return '1'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, threaded=True, debug=False)

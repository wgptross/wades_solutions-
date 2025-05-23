#!/usr/bin/env python3.12
test = True

import sys
import os
import requests
import json
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from updater import check_and_update

# API Key
api_key = os.environ.get('fs_api_key')
if not api_key:
    raise ValueError("fs_api_key environment variable not set.")

# group_id
fs_group_id = 21000562404 #os.environ.get('fs_group_id')
if not fs_group_id:
    raise ValueError("fs_group_id environment variable not set.")

# responder_id
fs_responder_id = 21003746754 #os.environ.get('fs_responder_id')
if not fs_responder_id:
    raise ValueError("fs_responder_id environment variable not set.")

# global vars
global override_number

#testing version while 
__version__ = "1.0.0"




# Variables
base_url = 'https://pacs.freshservice.com'
api_password = 'x'
group_id = int(fs_group_id)
responder_id = int(fs_responder_id)
email = 'phone_call@email.com'
line_break = "\n"
issue_type = "Other"
category = "Other"
current_date_time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M")
all_department_ids = []
all_department_names = []
all_primary_domain = []
selected_facility_name = ""
email_domain = ""
issue_type_bubble = ""
first_name = ''
last_name = ''

# conditional variables for testing or live
if test:
    incoming_full_name = "POD 2 - San Diego & Desert Wave Regions - Country Hills Post Acute Director of Staff Development Asst."
    incoming_phone_number = '987654321'
    incoming_first_name = 'First'
    incoming_last_name = 'Last'
    ticket_number = "987176"
else:
    incoming_full_name = sys.argv[1]
    incoming_phone_number = sys.argv[2]
    incoming_first_name = sys.argv[3]
    incoming_last_name = sys.argv[4]
    ticket_number = ''


# functions to Bind mouse events for dragging
def start_move(event):
    root.x = event.x
    root.y = event.y
def move_window(event):
    x = root.winfo_x() - root.x + event.x
    y = root.winfo_y() - root.y + event.y
    root.geometry(f"+{x}+{y}")

# Create the ticket
def create_ticket():
    global ticket_number
    url = f"{base_url}/api/v2/tickets"
    headers = {'Content-Type': 'application/json'}

    ticket_data = {
        'category': category,
        'email': email,
        'status': 2,
        'priority': 1,
        'source': 3,
        'subject': f'{incoming_full_name} | Phone Call, {current_date_time}',
        'description': f"{incoming_full_name} | Phone Call, {current_date_time}",
        'workspace_id': 11,
        'group_id': group_id,
        'responder_id': responder_id,
        'custom_fields': {
            'issuetype': issue_type,
            'user_phone_number': incoming_phone_number
        }
    }
    data = json.dumps(ticket_data)

    try:
        response = requests.post(url, auth=(api_key, api_password), headers=headers, data=data)
        response.raise_for_status()

        ticket_number = response.json()['ticket']['id']
        return ticket_number

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")

# function to start the timer
def start_timer(ticket):
    url = f"{base_url}/api/v2/tickets/{ticket}/time_entries"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'time_entry': {
            'timer_running': 'true',
            'agent_id': responder_id,
            'billable': True,
      }
  })

    # Send request to start timer
    try:
        response = requests.post(url, auth=(api_key, api_password), headers=headers, data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error starting timer: {str(e)}\n {response.text}")

# function to stop the timer
def stop_timer(ticket):
    url = f"{base_url}/api/v2/tickets/{ticket}/time_entries"
    headers = {'Content-Type': 'application/json'}

    try:
        # Fetch time entries for the ticket
        response = requests.get(url, auth=(api_key, api_password), headers=headers)
        response.raise_for_status()

        # Extract time entry data
        time_entry_data = response.json()

        # Check if any timers are running
        if time_entry_data and 'time_entries' in time_entry_data:
            time_entries = time_entry_data['time_entries']

            # Loop through each time entry and stop running timers
            for entry in time_entries:
                if entry['timer_running']:  # Check if timer is running
                    time_entry_id = entry['id']
                    stop_url = f"{base_url}/api/v2/tickets/{ticket_number}/time_entries/{time_entry_id}"
                    data = {'timer_running': False}

                    # Send PUT request to stop the timer
                    response = requests.put(stop_url, auth=(api_key, api_password), headers=headers, json=data)
                    response.raise_for_status()

    # error catch message box
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error stopping timer: {str(e)}{response.text}")

# function to override the passed phone number arg
def phone_number_override():
    override_number = number_override_text.get("1.0", tk.END).strip()
    if override_number == '':
        return
    else:
        ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}"
        ticket_headers = {'Content-Type': 'application/json'}
        ticket_data = json.dumps({
            'custom_fields': {
                'user_phone_number': override_number
            }
        })


        # Send put request to changes endpoint to adjust the phone number
        try:
            response = requests.put(ticket_url, auth=(api_key, api_password), headers=ticket_headers,
                                                data=ticket_data)
            response.raise_for_status()  # Raise exception for error responses
            return override_number

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")

# function to override the name
def name_override():
    input_name = set_upn_entry.get().strip()

    if input_name == "":
        return incoming_full_name
    else:
        return input_name

### Functions Buttons ###

# Function to submit all notes and adjustments but places the ticket on hold/stop timer (unfinished)
def submit_and_hold(body):
    # Create a new window for the text box
    text_box_window = tk.Toplevel(root)
    text_box_window.title("Submit/Hold Reason")
    text_box_window.geometry('300x150')

    # Label for instructions or context
    reason_label = tk.Label(text_box_window, text="Please state a reason this ticket is on hold:")
    reason_label.pack()

    # Combobox for issue types
    reason_text = tk.Text(text_box_window, height=3, width=30)
    reason_text.pack()

    def _submit_and_hold():
        phone_number_override()
        update_requester_email()
        full_input_name = name_override()
        selected_facility_id = selected_facility()
        issuetype, sub_category, item = radio_button_value(issue_type_bubble)
        issue_type_name, var_a, var_b = radio_button_value(issue_type_bubble)

        if selected_facility_id is None:
            messagebox.showerror("Error", "Please select a valid facility before submitting.")
            return

        # get reason text box text and set to variable
        reason = reason_text.get('1.0', tk.END).strip()

        # note data
        note_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
        note_headers = {'Content-Type': 'application/json'}
        formatted_body = body.replace('\n', '<br>')
        enter = line_break.replace('\n', '<br>')
        note_data = json.dumps({
            "private": True,
            "body": f"Agent Notes:{enter}{formatted_body}{enter}Reason for hold: {reason}"
        })

        # Update ticket properties
        update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
        update_headers = {'Content-Type': 'application/json'}
        update_data = json.dumps({
            'group_id': group_id,
            'status': 16,
            'department_id': selected_facility_id,
            'subject': f'{full_input_name} | Phone Call, {current_date_time}',
            'description': f"{full_input_name} | Phone Call,{current_date_time}{enter}Issue: {issue_type_name}",
            'custom_fields': {
                'issuetype': issuetype,
                'sub_category': sub_category,
                'item': item,
            }
        })

        # Send request to submit private note and status change
        try:
            # api request for update data
            update_response = requests.put(update_url, auth=(api_key, api_password), headers=update_headers,
                                           data=update_data)
            update_response.raise_for_status()

            # api request for note data
            response = requests.post(note_url, auth=(api_key, api_password), headers=note_headers, data=note_data)
            response.raise_for_status()  # Raise exception for error responses

            # exits out of the gui
            root.destroy()

        except requests.exceptions.RequestException as e:
            # catch errors from either the update or the note submission
            if e.response is not None:
                error_message = f"Error updating ticket or submitting note: {str(e)}\n{e.response.text}"
            else:
                error_message = f"Error updating ticket or submitting note: {str(e)}"
            messagebox.showerror("Error", error_message)

        # Stop the timer
        stop_timer(ticket_number)

    # Submit Hold reason button
    submit_button = ttk.Button(text_box_window, text="Submit Reason", command=_submit_and_hold)
    submit_button.pack(padx=10, pady=10)

# Submit/Continue function, Submits all notes and adjustments to the ticket and closes the ticket out
def submit_and_continue(body):
    # run phone number override function
    phone_number_override()
    update_requester_email()
    full_input_name = name_override()
    issuetype, sub_category, item = radio_button_value(issue_type_bubble)
    issue_type_name, var_a, var_b = radio_button_value(issue_type_bubble)

    # get facility name, forced
    selected_facility_id = selected_facility()
    if selected_facility_id is None:
        messagebox.showerror("Error", "Please select a valid facility before submitting.")
        return

    # submit private notes with formatting
    ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    formatted_body = body.replace('\n', '<br>')
    enter = line_break.replace('\n', '<br>')
    ticket_data = json.dumps({
        "private": True,
        "body": f"Agent Notes:{enter}{formatted_body}",
    })

    # Update ticket properties
    update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
    update_headers = {'Content-Type': 'application/json'}
    update_data = json.dumps({
        'group_id': group_id,
        'department_id': selected_facility_id,
        'subject': f'{full_input_name} | Phone Call, {current_date_time}',
        'description': f"{full_input_name} | Phone Call,{current_date_time}{enter}Issue: {issue_type_name}",
        'custom_fields': {
            'issuetype': issuetype,
            'sub_category': sub_category,
            'item': item,
        }

    })

    try:
        # api request for updated url data
        update_response = requests.put(update_url, auth=(api_key, api_password), headers=update_headers,
                                       data=update_data)
        update_response.raise_for_status()

        # note response data
        response = requests.post(ticket_url, auth=(api_key, api_password), headers=ticket_headers, data=ticket_data)
        response.raise_for_status()  # Raise exception for error responses
        root.destroy() # exits out of the gui

    except requests.exceptions.RequestException as e:
        # catch errors from either the status update or the note submission
        if e.response is not None:
            error_message = f"Error updating ticket or submitting note: {str(e)}\n{e.response.text}"
        else:
            error_message = f"Error updating ticket or submitting note: {str(e)}"
        messagebox.showerror("Error", error_message)

# Submit/close function, Submits all notes and adjustments to the ticket and closes the ticket out
def submit_and_close(body):
    # run phone number override function
    phone_number_override()
    update_requester_email()
    full_input_name = name_override()
    issuetype, sub_category, item = radio_button_value(issue_type_bubble)
    issue_type_name, var_a, var_b = radio_button_value(issue_type_bubble)

    # get facility name, forced
    selected_facility_id = selected_facility()
    if selected_facility_id is None:
        messagebox.showerror("Error", "Please select a valid facility before submitting.")
        return

    # submit private notes with formatting
    ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    formatted_body = body.replace('\n', '<br>')
    enter = line_break.replace('\n', '<br>')
    ticket_data = json.dumps({
        "private": True,
        "body": f"Agent Notes:{enter}{formatted_body}",
    })

    # Update ticket properties
    update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
    update_headers = {'Content-Type': 'application/json'}
    update_data = json.dumps({
        'group_id': group_id,
        'status': 5,
        'department_id': selected_facility_id,
        'subject': f'{full_input_name} | Phone Call, {current_date_time}',
        'description': f"{full_input_name} | Phone Call,{current_date_time}{enter}Issue: {issue_type_name}",
        'custom_fields': {
            'issuetype': issuetype,
            'sub_category': sub_category,
            'item': item,
        }

    })

    try:
        # api request for updated url data
        update_response = requests.put(update_url, auth=(api_key, api_password), headers=update_headers,
                                       data=update_data)
        update_response.raise_for_status()

        # note response data
        response = requests.post(ticket_url, auth=(api_key, api_password), headers=ticket_headers, data=ticket_data)
        response.raise_for_status()  # Raise exception for error responses
        root.destroy() # exits out of the gui

    except requests.exceptions.RequestException as e:
        # catch errors from either the status update or the note submission
        if e.response is not None:
            error_message = f"Error updating ticket or submitting note: {str(e)}\n{e.response.text}"
        else:
            error_message = f"Error updating ticket or submitting note: {str(e)}"
        messagebox.showerror("Error", error_message)

# Function to move the ticket to EHR
def transfer_to_ehr():
    ticket_url = f"{base_url}/api/v2/tickets/{ticket_number}/notes"
    ticket_headers = {'Content-Type': 'application/json'}
    ehr_note = json.dumps({
        "private": True,
        "body": f"Call was related to PCC and was not IT related, call transferred to EHR.",
    })

    # ticket data to set ticket properties to close
    update_url = f"{base_url}/api/v2/tickets/{ticket_number}"
    update_headers = {'Content-Type': 'application/json'}
    update_data = json.dumps({
        'status': 5,
        'department_id': 21000438222,
        'custom_fields':{
            'issuetype': 'Other',
            'sub_category': 'Miscellaneous',
        }
    })

    # Api request to submit ticket data and notes data
    try:
        # note response data
        note_response = requests.post(ticket_url, auth=(api_key, api_password), headers=ticket_headers, data=ehr_note)
        note_response.raise_for_status()

        update_response = requests.put(update_url, auth=(api_key, api_password), headers=ticket_headers,
                                        data=update_data)
        update_response.raise_for_status()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{e.response.text}")

    root.destroy() # destroys the gui/ quits application

### Function buttons ##

# function to submit properties for radio button/issue types
def radio_button_value(issue_type_bubble):
    issue_var = issue_type_bubble.lower()

    if issue_var == "password reset":
        issuetype = 'Identity Management'
        sub_category = 'Password Reset'
        item = None

    elif issue_var == "mfa reset":
        issuetype = 'Identity Management'
        sub_category = 'MFA'
        item = None

    elif issue_var == "printer issue":
        issuetype = 'Printer/scanner'
        sub_category = 'Setup'
        item = 'Existing Printer'

    elif issue_var == "device issue":
        issuetype = 'Workstations'
        sub_category = 'Windows Workstation'
        item = 'Other'

    elif issue_var == "network issue":
        issuetype = 'Networking'
        sub_category = 'Other'
        item = None

    elif issue_var == "account issue":
        issuetype = 'Identity Management'
        sub_category = 'Other'
        item = None

    elif issue_var == "add licensing":
        issuetype = 'Software'
        sub_category = 'Other'
        item = 'Licensing/Activation'

    else:
        issuetype = 'Other'
        sub_category = 'Miscellaneous'
        item = None

    return issuetype, sub_category, item

# function to get a list of all facility names and domains
def get_departments_and_domain():
    all_departments = []
    all_dept_ids = []
    all_domains = []
    page = 1
    per_page = 100

    while True:
        departments_url = f"{base_url}/api/v2/departments?page={page}&per_page={per_page}"
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.get(departments_url, auth=(api_key, api_password), headers=headers)
            response.raise_for_status()

            departments_data = response.json()
            departments = departments_data.get('departments', [])

            if not departments:
                break

            for dept in departments:
                primary_domain = dept.get('custom_fields', {}).get('primary_domain', [])
                if primary_domain and primary_domain not in all_domains:
                    all_domains.append(primary_domain)

            all_departments.extend([dept['name'] for dept in departments])
            all_dept_ids.extend([dept['id'] for dept in departments])

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching departments: {e}\n{response.text}")
            break

    global all_department_names
    global all_department_ids
    global all_primary_domain
    all_domains.insert(0,'pacsne.com')
    all_domains.insert(0,'guestsso.com')
    all_department_names = all_departments
    all_department_ids = all_dept_ids
    all_primary_domain = all_domains

# sets a variable for the selected facility
def selected_facility():
    global selected_facility_name
    global all_department_ids
    global all_department_names

    selected_facility_name = dept_list_dropdown_combobox.get()


    # create dictionary
    dept_name_to_id = {name: id for name, id in zip(all_department_names, all_department_ids)}

    selected_facility_id = dept_name_to_id.get(selected_facility_name)  # Get ID or None if not found
    return selected_facility_id

# function to search as you type in facility list (Needs bugs worked out)
def update_facility_dropdown_list(event=None):
    global all_department_names

    # Get the typed text
    typed_text = dept_list_dropdown_combobox.get()

    # Filter the names
    filtered_names = [name for name in all_department_names if typed_text.lower() in name.lower()]

    # Update the combobox values
    dept_list_dropdown_combobox['values'] = filtered_names

    # Only generate the <Down> event if it was a genuine key press
    if event and event.type == 'key':  # Check if it's a key press event
        dept_list_dropdown_combobox.event_generate('<Down>')

# function to search as you type in domain list (Needs bugs worked out)
def update_domain_dropdown_list(event=None):
    global all_primary_domain

    # Get the typed text
    typed_text = domain_list_dropdown_combobox.get()

    # Filter the names
    filtered_names = [name for name in all_primary_domain if typed_text.lower() in name.lower()]

    # Update the combobox values
    domain_list_dropdown_combobox['values'] = filtered_names

    # Only generate the <Down> event if it was a genuine key press
    if event and event.type == 'key':  # Check if it's a key press event
        domain_list_dropdown_combobox.event_generate('<Down>')

# function to handle bubble selection
def select_issue_type():
    global issue_type_bubble
    issue_type_bubble = selected_issue_vars[issue_types.index(selected_issue.get())].get()

# update the email to update the requester information
def update_requester_email():
    global ticket_number
    selected_email_domain = domain_list_dropdown_combobox.get()



    if selected_email_domain == "":
        email_update = email
    else:
        email_update = (set_upn_entry.get() + "@" + selected_email_domain)

    url = f"{base_url}/api/v2/tickets/{ticket_number}"
    headers = {'Content-Type': 'application/json'}

    email_data = json.dumps({
        'email': email_update
    })

    try:
        response = requests.put(url, auth=(api_key, api_password), headers=headers, data=email_data)
        response.raise_for_status()


    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error creating ticket: {str(e)}\n{response.text}")

# kill program function



# Fetch departments and extract names
all_departments = get_departments_and_domain()

# Create the main window
root = tk.Tk()
root.title("RC/FS Call Tool")
root.overrideredirect(True) # removes default title bar
root.configure(cursor='hand2')

# grids for testing UI stuff

for i in range(10): 
    root.grid_rowconfigure(i, weight=1)
    root.grid_columnconfigure(i, weight=1)

## kill program function

def quit_program():
    root.destroy()

# Make the GUI stay on top
root.attributes('-topmost', True)

# Style for themed widgets
radio_style = ttk.Style()
radio_style.theme_use('default')

# Create the title bar
title_bar = ttk.Frame(root, style='Titlebar.TFrame')
title_bar.grid(row=0, column=0, columnspan=5, sticky="ew")

# Configure the title bar style
radio_style.configure('Titlebar.TFrame')

# Load and display the icon
icon_image = Image.open(".\Images\\PACS_logo_RC-FS.png")
icon_photo = ImageTk.PhotoImage(icon_image.resize((115, 34)))
icon_label = tk.Label(title_bar, image=icon_photo)

icon_label.image = icon_photo
icon_label.grid(row=0, column=0, padx=5, pady=5)

# Title label
title_label = ttk.Label(title_bar, text=f"RC Call App -- Version: {__version__}",
                        font=("Helvetica", 14, "bold"), foreground='white')
title_label.grid(row=0, column=1, padx=10, pady=5)

# Bind to the title bar
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<B1-Motion>", move_window)

# Bind to the title label
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", move_window)

# Bind to the logo
icon_label.bind("<ButtonPress-1>", start_move)
icon_label.bind("<B1-Motion>", move_window)

# Main content area
content_frame = ttk.Frame(root, padding=10)
content_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

# Ticket number label and display
ticket_number_label = ttk.Label(content_frame, text="Ticket Number:")
ticket_number_label.grid(row=0, column=0, sticky="w")
if test:
    ticket_number_entry = ttk.Label(content_frame, text=ticket_number)
else:
    ticket_number_entry = ttk.Label(content_frame, text=create_ticket())
ticket_number_entry.grid(row=0, column=1, sticky="e")

# Phone number label and display
incoming_phone_number_label = ttk.Label(content_frame, text="Phone Number:")
incoming_phone_number_label.grid(row=1, column=0, sticky="w")
incoming_phone_number_text = ttk.Label(content_frame, text=incoming_phone_number)
incoming_phone_number_text.grid(row=1, column=1, sticky="e")

# Full name label and display
full_name_label = ttk.Label(content_frame, text="Full Name:")
full_name_label.grid(row=2, column=0, sticky="w")
if test:
    full_name_text = ttk.Label(content_frame, text=f"{incoming_full_name}")
else:
    full_name_text = ttk.Label(content_frame, text=f"{incoming_first_name} {incoming_last_name}")
full_name_text.grid(row=2, column=0, columnspan=4)
full_name_text.lower() # send to back

# override set the upn text box
set_upn_entry = tk.Entry(content_frame)
set_upn_entry.grid(row=2, column=2)

# Notes label and text box
notes_label = ttk.Label(content_frame, text="Notes:")
notes_label.grid(row=3, column=0, sticky="w")
notes_text = tk.Text(content_frame, width=45, height=10, wrap="word")
notes_text.grid(row=4, column=0, columnspan=3, pady=5)

# Phone number override text box
number_override_text = tk.Text(content_frame, width=15, height=1, wrap="word")
number_override_text.grid(row=1, column=2, sticky="w")

# department list label
dept_list_label = ttk.Label(content_frame, text="Facility List:")
dept_list_label.grid(row=0, column=3, columnspan=2, sticky="s")

# department list drop down
dept_list_dropdown_combobox = ttk.Combobox(content_frame, values=all_department_names,
                                           postcommand=update_facility_dropdown_list)
dept_list_dropdown_combobox.grid(row=1, column=3, columnspan=2, pady=5, sticky="n")
dept_list_dropdown_combobox.bind("<Key>", update_facility_dropdown_list)

# department list label
domain_list_label = ttk.Label(content_frame, text="Domain:")
domain_list_label.grid(row=2, column=3, sticky="w")

# all domain dropdown list
domain_list_dropdown_combobox = ttk.Combobox(content_frame, values=all_primary_domain,
                                           postcommand=update_domain_dropdown_list, width=14)
domain_list_dropdown_combobox.grid(row=2, column=3, columnspan=1, sticky="e")
domain_list_dropdown_combobox.bind("<Key>", update_domain_dropdown_list)

# Issue type label
issue_type_label = ttk.Label(content_frame, text="Issue Type:")
issue_type_label.grid(row=3, rowspan=2, column=3, columnspan=2, sticky="n")

###############
### Buttons ###
###############

# Submit/Continue button

#testing close feature

close_program = ttk.Button(title_bar, text="close", command=quit_program)
close_program.grid(row=0, column=4, columnspan=5, pady=10)



submit_and_Continue_button = ttk.Button(content_frame, text="Submit/Continue",
                                        command=lambda: submit_and_continue(notes_text.get('1.0', tk.END)))
submit_and_Continue_button.grid(row=5, column=1, columnspan=1, pady=10)

# Submit/Hold
submit_and_hold_button = ttk.Button(content_frame, text="Submit/Hold",
                                    command=lambda: submit_and_hold(notes_text.get('1.0', tk.END)))
submit_and_hold_button.grid(row=5, column=0, columnspan=1, pady=10)

# Submit/Close Button
submit_and_close_button = ttk.Button(content_frame, text="Submit/Close",
                                     command=lambda: submit_and_close(notes_text.get('1.0', tk.END)))
submit_and_close_button.grid(row=5, column=2, columnspan=1, pady=10)

# Transfer to EHR Button
transfer_to_ehr_button = ttk.Button(content_frame, text="Transfer To EHR",
                                     command=lambda: transfer_to_ehr())
transfer_to_ehr_button.grid(row=5, column=3, columnspan=2, pady=10, sticky='w')

####################
### Bubble Frame ###
####################

# Frame for positioning (using ttk.Frame)
bubble_frame = ttk.Frame(content_frame, padding=14)
bubble_frame.grid(row=3, column=3, rowspan=3, sticky="n")
bubble_frame.lower() # send frame to back

# issue type list for the bubbles
issue_types = ['Password Reset', 'MFA Reset', 'Printer Issue',
               'Device Issue', 'Network Issue', 'Account Issue', 'Add Licensing', 'Other']

# List to store StringVar for each radio button
selected_issue_vars = []
selected_issue = tk.StringVar(value=issue_types[7])

# Create the radio buttons with labels
for i, issue in enumerate(issue_types):
    # Frame for each radio button and label
    item_frame = ttk.Frame(bubble_frame)
    item_frame.grid(row=i, column=0, sticky="w", pady=2)

    # Create a StringVar for this radio button and add it to the list
    var = tk.StringVar(value=issue)
    selected_issue_vars.append(var)


    # Radio button
    radio_btn = ttk.Radiobutton(
        item_frame,
        text="",
        variable=selected_issue,
        value=issue,
        command=select_issue_type,
        style="Radio.TButton"
    )
    radio_btn.pack(side="left")

    # Label for the radio button
    label = ttk.Label(item_frame, text=issue)
    label.pack(side="left", padx=5)

# Create the radio button style
radio_style = ttk.Style()
radio_style.configure("Radio.TButton", relief="raised", width=3, font=("TkDefaultFont", 8))
radio_style.map("Radio.TButton", background=[("active", "white"), ("selected", "black"), ("!selected", "purple")],
                foreground="white")

# Configure grid weights for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# run functions and keep gui open
if not test:
    start_timer(ticket_number)
root.mainloop()

# check and update version
check_and_update()

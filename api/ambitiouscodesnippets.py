# i believe this was stuff if i wanted match timeline info rather than just match info

"""

# Replace 'your_json_file.json' with the path to your JSON file
json_file_path = 'matchtimelineinfo.json'

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract only item purchase events from all frames
item_purchase_events = [event for frame in data["info"]["frames"] for event in frame.get("events", []) if event["type"] == "ITEM_PURCHASED"]

# Normalize the item purchase events data to create a DataFrame
item_purchase_events_df = pd.json_normalize(item_purchase_events)

# Specify the path for the output Excel file
excel_file_path = 'item_purchase_events.xlsx'

# Write the DataFrame to an Excel file
# Ensure you have openpyxl installed for .xlsx support
item_purchase_events_df.to_excel(excel_file_path, index=False)

print(f'Item purchase events data has been written to {excel_file_path}')
"""

# old code for converting json to xlsx

"""

# try to put json into a google sheet

# Load the JSON data from the file
json_file_path = 'matchinfo.json'  # Replace with your actual file path
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract the 'info' part of the JSON, which contains match details
info_data = data.get('info', {})

# Extract and normalize 'participants' data
participants = info_data.get('participants', [])

# Use json_normalize to convert the list of participants into a DataFrame
participants_df = pd.json_normalize(participants)

# Save the participants' data to an Excel file for easy reading
excel_file_path = 'match_participants_info.xlsx'
participants_df.to_excel(excel_file_path, index=False)

print(f'Participants information has been saved to {excel_file_path}')

"""
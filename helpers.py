# File contains helper functions for the EU_Scraper

import numpy as np
import pandas as pd
import json
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for both dev and PyInstaller """
    try:
        # PyInstaller stores bundled files in a temporary folder at runtime
        base_path = sys._MEIPASS
    except AttributeError:
        # Use the current working directory during development
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Load translations from a JSON file
TRANSLATIONS = json.load(open(resource_path('translations.json')))

def load_initiatives(target_filename):
    """
    Loads the saved initiatives and logs from an Excel file. 
    If the file or sheet does not exist, it returns empty DataFrames.
    
    Returns:
        df_initiatives (DataFrame): DataFrame containing the initiatives.
        df_log (DataFrame): DataFrame containing the log.
    """
    try:
        df_initiatives = pd.read_excel(resource_path(target_filename), sheet_name="Alle initiatieven", index_col=0)
        df_log = pd.read_excel(resource_path(target_filename), sheet_name="Log", index_col=0)
    except FileNotFoundError:
        df_initiatives = pd.DataFrame(columns=["Naam", "Toelichting", "Type", "Impact IenW", "Status", "Details", "URL"])
        df_log = pd.DataFrame()
    
    return df_initiatives, df_log

def write_to_excel(df_initiatives, df_log, target_filename):
    """
    Writes the updated initiatives and log to the target Excel file.
    
    Args:
        df_initiatives (DataFrame): DataFrame containing the initiatives to write.
        df_log (DataFrame): DataFrame containing the log to write.
    """
    with pd.ExcelWriter(resource_path(target_filename), engine='xlsxwriter') as writer:
        write_initiatives(df_initiatives, writer)
        df_initiatives.to_excel(writer, sheet_name="Alle initiatieven")
        df_log.to_excel(writer, sheet_name="Log")


def highlight_alternate_rows(row):
    """
    Applies alternating row coloring based on the row index.
    
    Args:
        row (Series): The row of the DataFrame being styled.

    Returns:
        List[str]: A list of background colors for each cell in the row.
    """
    return ['background-color: white' if row.name % 2 != 0 else f'background-color: {TRANSLATIONS["Status"][row["Status"]]["Colors"]["Row"]}' for _ in row]

def write_initiatives(df, writer):
    """
    Writes the initiatives DataFrame to multiple Excel sheets, grouped by 'Status', 
    and applies specific styling and formatting.

    Args:
        df (DataFrame): The initiatives DataFrame to write.
        writer (ExcelWriter): The Excel writer object for writing to the file.
    """
    # Create a temporary DataFrame with selected columns
    df_temp = df[['Naam', 'Toelichting', 'Type', 'Impact IenW', "Status", "URL"]]

    # Create hyperlinks in the "Naam" column and remove the column
    df_temp.loc[:, 'Naam'] = df_temp.apply(lambda row: f'=HYPERLINK("{row["URL"]}", "{row["Naam"]}")', axis=1)
    df_temp = df_temp.drop(columns=['URL'])

    for status_name, group in df_temp.groupby("Status"):
        nl_status = TRANSLATIONS["Status"][status_name]["Nederlands"]

        # Re-index from 1
        group.index = np.arange(1, len(group) + 1)

        # Apply alternating row colors
        styled_group = group.style.apply(highlight_alternate_rows, axis=1)

        # Write to Excel sheet with the Dutch status as the sheet name
        styled_group.to_excel(writer, sheet_name=nl_status, startrow=1, columns=["Naam", "Toelichting", "Type", "Impact IenW"], header=False)

        # Format the header row with the specified color
        header_format = writer.book.add_format({
            'fg_color': TRANSLATIONS["Status"][status_name]["Colors"]["Header"]
        })

        for col_num, value in enumerate(styled_group.columns.values):
            if value != "Status":
                writer.sheets[nl_status].write(0, col_num + 1, value, header_format)
        

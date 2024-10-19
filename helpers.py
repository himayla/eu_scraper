import numpy as np
import pandas as pd

target_file = "output/Europese Digitaliseringsinitiatieven.xlsx" 

en_to_nl_type = {
    "Non-Legislative": "Niet-regelgevend",
}

en_to_nl_status = {
    "Announced": "Aangekondigd",
    "Tabled": "Ingediend",
    "Blocked": "Geblokkeerd",
    "Close to adoption": "Bijna adoptie",
    "Adopted / Completed": "Aangenomen of Voltooid",
    "Withdrawn": "Ingetrokken"
}

colors = {
    "Aangekondigd": {
        "Header": "#b3deff",
        "Row": "#0171c0"
    },
    "Ingediend": {
        "Header": "#00b0f0",
        "Row": "#b7ecff"
    },
    "Geblokkeerd": {
        "Header": "#ed7d31",
        "Row": "#f8ceb2"
    },
    "Bijna adoptie": {
        "Header": "#ffc000",
        "Row": "#fff2cc"
    },
    "Aangenomen of Voltooid": {
        "Header": "#00b050",
        "Row": "##e1ffef"
    },
    "Ingetrokken": {
        "Header": "#ff0000",
        "Row": "#ffcccc"
    }
}

def load():
    """
    """
    df_ini = load_ini()
    df_log = load_log()

    return df_ini, df_log

def load_ini():
    """
    Reads the existing initiatives and returns it as a DataFrame.
    """
    try:
        df_ini = pd.read_excel(target_file, sheet_name="Alle initiatieven", index_col=0)
    except:
        df_ini = pd.DataFrame(columns=["Naam", "Toelichting", "Type", "Impact IenW", "Status", "Details", "URL"]) 
    return df_ini

def load_log():
    """
    """
    try:
        df_log = pd.read_excel(target_file, sheet_name="Log", index_col=0)
    except:
        df_log = pd.DataFrame()#columns=["Start", "# New Initiatives", "# Updated Columns", "Updated columns", "Runtime"])

    return df_log

def write(df_ini, df_log):

    with pd.ExcelWriter(target_file, engine='xlsxwriter') as writer:
        write_ini(df_ini, writer)

        df_log.to_excel(writer, sheet_name="Log")
    

def highlight_alternate_rows(row):
    """
    """
    return ['background-color: white' if row.name % 2 != 0 else f'background-color: {colors[row.Status]["Row"]}' for _ in row]

def write_ini(df, writer):
    """
    Writes the updated information to an CSV, Excel and per sheet.
    """

    # Temp copy
    df_temp = df[['Naam', 'Toelichting', 'Type', 'Impact IenW', "Status", "URL"]]

    # Create hyperlinks
    #df_temp['Naam'] = df_temp.apply(lambda row: f'=HYPERLINK("{row["URL"]}", "{row["Naam"]}")', axis=1)

    df_temp.loc[:, 'Naam'] = df_temp.apply(lambda row: f'=HYPERLINK("{row["URL"]}", "{row["Naam"]}")', axis=1)

    df_temp = df_temp.drop(columns=['URL'])

    # header_style = {'selector': 'thead th', 
    #                 'props': [('background-color', 'darkblue'), ('color', 'white')]}


    for status_name, group in df_temp.groupby("Status", observed=False):

        group.index = np.arange(1, len(group) + 1)


        # COLORED ROWS
        styled_group = group.style.apply(highlight_alternate_rows, axis=1)

        styled_group.to_excel(writer, sheet_name=status_name,startrow=1, header=False)

        # COLORED HEADER
                
        # Add format
        header_format = writer.book.add_format({
            'fg_color': colors[status_name]["Header"]
        })

        for col_num, value in enumerate(styled_group.columns.values):
            writer.sheets[status_name].write(0, col_num + 1, value, header_format)

        df.to_excel(writer, sheet_name="Alle initiatieven")
    

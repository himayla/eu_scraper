import numpy as np
import pandas as pd

output_file = 'Europese Digitaliseringsinitiatieven'

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

def read_ini(filename):
    """
    Reads the "Alle initiatieven" tab and returns it as a DataFrame.
    """
    try:
        df_ini = pd.read_excel(f"{filename}.xlsx", sheet_name="Alle initiatieven", index_col=0)#, usecols=['Naam', 'Type', 'Status', 'URL'])
        #df_ini = pd.read_csv("all_initiatives.csv")#, index=False) # Test instead of Alle ini, in CSV

    except:
        df_ini = pd.DataFrame(columns=["Naam", "Toelichting", "Type", "Impact IenW", "Status", "URL"]) 
    return df_ini

def write_ini(df, output_file, csv=False):
    """
    Writes the updated information to the Excel and per tab page.
    """
    # Write out CSV
    if csv:
        df.to_csv(f"{output_file}.csv",index=None)

    df = df[['Naam', 'Toelichting', 'Type', 'Impact IenW', 'Status', 'URL']]

    with pd.ExcelWriter(f"{output_file}.xlsx", engine='xlsxwriter') as writer:
        df.index = np.arange(1, len(df) + 1)

        # Temp compy
        df_temp = df[['Naam', 'Toelichting', 'Type', 'Impact IenW', "Status", "URL"]]
        df_temp['Naam'] = df_temp.apply(lambda row: f'=HYPERLINK("{row["URL"]}", "{row["Naam"]}")', axis=1)
        df_temp = df_temp.drop(columns=['URL'])

        for status_name, group in df_temp.groupby("Status", observed=False):
            group.index = np.arange(1, len(group) + 1)
            group.to_excel(writer, sheet_name=status_name, index=False)

    
        df.to_excel(writer, sheet_name="Alle initiatieven")
    
    
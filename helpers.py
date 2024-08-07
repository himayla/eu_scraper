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
    # TODO: Zorg over adaptieve mogelijkheden als niet alle kolommen er zijn
    try:
        df_ini = pd.read_excel(f"{filename}.xlsx", sheet_name="Alle initiatieven", index_col=0)#, usecols=['Naam', 'Type', 'Status', 'URL'])
    except:
        df_ini = pd.DataFrame(columns=["Naam", "Toelichting", "Type", "Impact IenW", "Status", "URL"]) 
    return df_ini ####### TESTING

def write_ini(df, output_file):
    """
    Writes the updated information to the Excel and per tab page.
    """
    with pd.ExcelWriter(f"{output_file}.xlsx") as writer:
        df.index = np.arange(1, len(df) + 1)

        df.to_excel(writer, sheet_name="Alle initiatieven")

        for status_name, group in df.groupby("Status", observed=False):
            group.index = np.arange(1, len(group) + 1)
            group.to_excel(writer, sheet_name=status_name)
import numpy as np
import pandas as pd

output_file = 'results'

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

color = {
    "Aangekondigd": "blue",
    "Ingediend": "lightblue",
    "Geblokkeerd": "orange",
    "Aangenomen of Voltooid": "green",
    "Withdrawn": "red"
}

def read_ini(filename):
    # TODO: Zorg voor een mogelijkheid als er nog geen outputfile gemaakt wordt
    # TODO: Zorg over adaptieve mogelijkheden als niet alle kolommen er zijn
    try:
        df_ini = pd.read_excel(f"{filename}.xlsx", index_col=0)#, usecols=['Naam', 'Type', 'Status', 'URL'])
    except:
        df_ini = pd.DataFrame(columns=["Naam", "Toelichting", "Type", "Impact IenW", "Status", "URL"]) 
    return df_ini

def highlight_row_condition(row):    
    return [f"background-color: {color}" for _ in row]
    #return [f"background-color: {color}" for _ in row]

def write_ini(df, output_file, df_eval=None):
    # df_new['Status'] = pd.Categorical(df_new['Status'], categories=list(en_to_nl_status.values()), ordered=True)

    with pd.ExcelWriter(f"{output_file}.xlsx") as writer:
        df.index = np.arange(1, len(df) + 1)

        # TODO: Sheet met job informatie
        # df_eval.to_excel(writer, sheet_name="Informatie")
        df.to_excel(writer, sheet_name="Alle initiatieven")

        # TODO: Aparte sheets per status ..
        for status_name, group in df.groupby("Status", observed=False):
            group.index = np.arange(1, len(group) + 1)
            styled_group = group.style.apply(highlight_row_condition, axis=1)

            styled_group.to_excel(writer, sheet_name=status_name)
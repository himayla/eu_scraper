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

def read_ini(filename):
    # TODO: Zorg voor een mogelijkheid als er nog geen outputfile gemaakt wordt
    # TODO: Zorg over adaptieve mogelijkheden als niet alle kolommen er zijn
    df_ini = pd.read_excel(f"{filename}.xlsx", usecols=['Naam', 'Type', 'Status', 'URL'])
    return df_ini

def write_ini(df, output_file, df_eval=None):
    # df_new['Status'] = pd.Categorical(df_new['Status'], categories=list(en_to_nl_status.values()), ordered=True)

    with pd.ExcelWriter(f"{output_file}.xlsx") as writer:

        # TODO: Sheet met job informatie
        # df_eval.to_excel(writer, sheet_name="Informatie")
        df.to_excel(writer, sheet_name="Alle initiatieven")

        # TODO: Aparte sheets per status
        # for status_name, group in df.groupby("Status", observed=False):
        #     group.index = np.arange(1, len(group) + 1)
        #     group.to_excel(writer, sheet_name=status_name)
        

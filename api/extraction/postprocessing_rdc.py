import pandas as pd


def choose_table(all_table):
    all_len = [len(all_table[i][0]) for i in range(len(all_table))]

    if (5 in all_len):
        return 5, pd.DataFrame.from_records(all_table[all_len.index(5)], columns=["Date", "Valeur", "Opération", "Débit", "Crédit"])
    if (4 in all_len):
        return 4, pd.DataFrame.from_records(all_table[all_len.index(4)], columns=["Date", "Opération", "Débit", "Crédit"])


def val_wrong_ligne(datab, cols_to_update=["Date", "Valeur"], cols_to_know_which_to_keep=["Débit", "Crédit"]):
    null_db = datab[((datab[cols_to_update[0]].isnull() & datab[cols_to_update[1]].notna()) | (
        datab[cols_to_update[0]].notna() & datab[cols_to_update[1]].isnull()))]
    ix = (null_db.index)
    for i in ix:
        if((i+1) in ix):
            str_i = (str(datab.loc[i][cols_to_know_which_to_keep[1]]) +
                     str(datab.loc[i][cols_to_know_which_to_keep[0]]))
            str_i_plus_1 = (str(datab.loc[i+1][cols_to_know_which_to_keep[1]])+str(
                datab.loc[i+1][cols_to_know_which_to_keep[0]]))
            if str_i == "NoneNone":
                if str_i_plus_1 != "NoneNone":
                    if str(datab.loc[i][cols_to_update[0]]) != "None":
                        datab.loc[i+1][cols_to_update[0]
                                       ] = datab.loc[i][cols_to_update[0]]
                        datab.loc[i][cols_to_update[0]] = None
                    if str(datab.loc[i][cols_to_update[1]]) != "None":
                        datab.loc[i+1][cols_to_update[1]
                                       ] = datab.loc[i][cols_to_update[1]]
                        datab.loc[i][cols_to_update[1]] = None
            else:
                if str(datab.loc[i][cols_to_update[0]]) != "None":
                    datab.loc[i][cols_to_update[0]
                                 ] = datab.loc[i+1][cols_to_update[0]]
                    datab.loc[i+1][cols_to_update[0]] = None
                if str(datab.loc[i][cols_to_update[1]]) != "None":
                    datab.loc[i][cols_to_update[1]
                                 ] = datab.loc[i+1][cols_to_update[1]]
                    datab.loc[i+1][cols_to_update[1]] = None


# def postprocessing_rdc(extraction, name, field_value, field, polygon, pageNumber):
#     from api.extraction.extraction_function import extraction_put_val

def postprocessing_rdc(all_table):
    n, datab = choose_table(all_table)
    if(n == 5):
        # On regroupe les lignes splité en deux
        null_db = datab[(datab["Débit"].isnull() & datab["Crédit"].isnull(
        ) & datab["Valeur"].isnull() & datab["Date"].isnull())]
        for i in null_db.index:
            datab.loc[i-1]["Opération"] = datab.loc[i -
                                                    1]["Opération"]+" "+datab.loc[i]["Opération"]
            datab.loc[i]["Opération"] = None

        # On met les valeur ou date qui au sauté d'une ligne au bon endoit
        # Attention elle doit etre fait après le regroupement de ligne! (sinon on va mettre les soldes intermédiaire avec les ligne précédentes)
        val_wrong_ligne(datab, cols_to_update=[
                        "Date", "Valeur"], cols_to_know_which_to_keep=["Débit", "Crédit"])

    datab = datab.dropna(axis=0, how='all').reset_index(drop=True)
    # for column in datab.columns:
    #     datab[column] = datab[column].str.replace('|', '')

    return datab

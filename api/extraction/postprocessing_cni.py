import re
from datetime import *


def postprocessing_cni(extraction, name, field_value, field, polygon, pageNumber):
    from api.extraction.extraction_function import extraction_put_val
    key, val, conf = name, field_value, field.confidence
    if key == "Vérification":
        extraction = extraction_put_val(extraction, key, val,
                                        conf, polygon, pageNumber)
    val = " ".join([i.capitalize() for i in val.lower().split(" ")])
    if key == "Vérification":
        val = val.replace('<<<', '%').replace(
            ' ', '%').replace('<<', '%')
        val = re.sub('[+]{2,}', '', val)
        champs = (val.split("%"))
        champs = [i for i in champs if len(i) > 6]

        extraction = extraction_put_val(extraction, "Nom_", champs[0][5:].replace(
            "<", " ").upper(), conf, None, pageNumber)

        prenom = re.sub(
            '<\d+', '%', champs[1]).replace("<", "-")
        prenom = re.sub('\d+', '', prenom).split('%')
        extraction = extraction_put_val(extraction, "Prénom_",
                                        prenom[0].capitalize(), conf, None, pageNumber)
        extraction = extraction_put_val(extraction, "ID_Numero_",
                                        champs[1][:12], conf, None, pageNumber)
        date = (re.sub('[a-zA-Z]+', '', champs[-1])).split('<')
        date = (date[-1])[:6]
        extraction = extraction_put_val(extraction, "Date_de_naissance_",
                                        naissance(date), conf, None, pageNumber)
    elif key == "Epouse":
        extraction = extraction_put_val(extraction, key, val.replace(
            "epouse", "").replace(":", "").upper(), conf, polygon, pageNumber)
    elif key == "Adresse":
        val = val.replace(":", "").replace("( ", "(")
        if val.count("(") > val.count(")"):
            val += ")"
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
    elif key == "Délivrée" or key == "Fin de validité":
        try:
            my_date, futur = date_from_dirty_string(val)
            if key == "Délivrée":
                extraction = extraction_put_val(
                    extraction, key, my_date, conf, polygon, pageNumber)
            else:
                extraction = extraction_put_val(
                    extraction, "Fin de validité", my_date, conf, polygon, pageNumber)

                extraction = extraction_put_val(extraction, "Validité",
                                                futur, conf, None, pageNumber)

        except:
            pass
    elif key == "Nationalité":
        if "franç" in val:
            extraction = extraction_put_val(
                extraction, key,  "Française", conf, polygon, pageNumber)
    elif key == "Sexe":
        if val == "f" or val == "m":
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
    elif key == "Titre":
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
    elif key in ["Initial", ]:
        pass
    else:
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
    return extraction


def naissance(p):
    if((int("20"+p[:2])) < int(str(datetime.today())[:4])+1):
        return(p[-2:]+"."+p[2:4]+"."+"20"+p[:2])
    else:
        return(p[-2:]+"."+p[2:4]+"."+"19"+p[:2])


def date_from_dirty_string(dirty_string):
    dirty_string = re.sub('[^\d]', '', dirty_string)
    if len(dirty_string) == 8:
        dirty_string = dirty_string[:2]+"." + \
            dirty_string[2:4]+"."+dirty_string[-4:]
        my_string = re.sub('[a-z]+', '', dirty_string)
        my_string = re.sub('[\W_ ]+', '.', my_string)
        today = datetime.today()
        ddmmyyyy = my_string.split(".")
        try:
            ddmmyyyy.remove('')
        except:
            pass
        date = datetime(int(ddmmyyyy[2]), int(ddmmyyyy[1]), int(ddmmyyyy[0]))
        validite = "Carte expirée"
        if today < date:
            validite = "Carte valide"

        return(".".join(ddmmyyyy), validite)
    return None, None

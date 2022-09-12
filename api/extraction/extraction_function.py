import random
from api.extraction.postprocessing_cni import postprocessing_cni
from api.extraction.postprocessing_bs import postprocessing_bs
from api.extraction.postprocessing_ir import postprocessing_ir
from api.extraction.postprocessing_ldf import postprocessing_ldf
from api.extraction.postprocessing_rdc import postprocessing_rdc

# Regroupe les appels aux diférentes océrisations (CNI, BS, IR, LDF)


def extraction_toDict(MODEL, extraction, name,
                      field_value, field, polygon, pageNumber):
    if ("CNI" in MODEL):
        postprocessing_cni(extraction, name,
                           field_value, field, polygon, pageNumber)
    elif ("IR" in MODEL):
        postprocessing_ir(
            extraction, name, field_value, field, polygon, pageNumber)
    elif ("BS" in MODEL):
        postprocessing_bs(extraction, name, field_value,
                          field, polygon, pageNumber)
    elif ("LDF" in MODEL):
        postprocessing_ldf(extraction, name, field_value,
                           field, polygon, pageNumber)
    elif ("RDC" in MODEL):
        postprocessing_rdc(extraction, name, field_value,
                           field, polygon, pageNumber)

# Cette fonction permet de remplir le champs des json extrait afin qu'ils ai tous la même structure et ne pas avoir des métadata trop incohérente
# Chaque champs possède :une valeur, une boite englobante permettant de retrouver sa position sue le pdf, la page associé, le niveau de confiance et la couleur de la boite englobante


def extraction_put_val(extraction, key, val, conf, polygon=None, pageNumber=0, color=None):
    bad_confidence = False
    if polygon and float(conf) < 0.35:
        bad_confidence = True
    if not color:
        color_c = [random.random(),
                   random.random(), random.random()]
        # On ne garde pas les couleurs casi blanches car elles ne ressortiront pas à l'image
        if (abs(color_c[0] - color_c[1]) < 0.3 and abs(color_c[2] - color_c[1]) < 0.3) or ((color_c[0]+color_c[0]+color_c[0]) > 1.75):
            color_c[random.randint(0, 2)] = 0
        # On ne garde pas les couleurs casi rouge car elles seront l'exclusivité des extraction avec une faible valeur de confiance
        if (color_c[0] > 0.55 and color_c[1] < 0.2 and color_c[2] < 0.15):
            color_c = [0.1, random.random(), random.random()]
        if bad_confidence:
            color_c = [1, 0, 0]
    if color:
        color_c = color
    extraction[key] = {'value': val,
                       'box': polygon, "pageNumber": pageNumber, "conf": conf, "color": color_c}
    return extraction

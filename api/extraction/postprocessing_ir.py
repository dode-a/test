def postprocessing_ir(extraction, name, field_value, field, polygon, pageNumber):
    from api.extraction.extraction_function import extraction_put_val
    errorMsg = "OCR - Erreur de lecture : "
    key, val, conf = name, field_value, field.confidence
    val = " ".join([i.capitalize() for i in val.split(" ")])
    if "Déclarant" in key:
        val = val.replace("Mme ", "").replace("M ", "")
        dec_list = val.split(" ")
        extraction = extraction_put_val(extraction, "Nom "+key,
                                        dec_list[0].upper(), conf, polygon, pageNumber)
        extraction = extraction_put_val(extraction, "Prénom "+key,
                                        " ".join(dec_list[1:]), conf, None, pageNumber)

    elif "Salaire" in key or "Revenu" in key:
        val = val.replace(" ", "")
        if len(val) > 8:
            extraction = extraction_put_val(
                extraction, key, errorMsg+val, conf, polygon, pageNumber)
        else:
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
    elif "Enfant" in key:
        val = val.replace(" ", "")
        if float(val) % 1 == 0:
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
        else:
            extraction = extraction_put_val(
                extraction, key, errorMsg+val, conf, polygon, pageNumber)
    elif "Nombre de part" == key:
        val = val.replace(",", ".")
        if float(val) % 0.5 == 0:
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
        else:
            extraction = extraction_put_val(
                extraction, key, errorMsg+val, conf, polygon, pageNumber)
    elif "Situation du foyer" == key:
        if val in ["M", "O", "D", "C", "V"]:
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
        else:
            extraction = extraction_put_val(
                extraction, key, errorMsg+val, conf, polygon, pageNumber)
    else:
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)

    return extraction

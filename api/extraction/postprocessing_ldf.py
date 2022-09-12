def postprocessing_ldf(extraction, name, field_value, field, polygon, pageNumber):
    from api.extraction.extraction_function import extraction_put_val
    errorMsg = "OCR - Erreur de lecture : "
    key, val, conf = name, field_value, field.confidence

    if conf < 0.2:
        extraction = extraction_put_val(extraction, key, errorMsg +
                                        val, conf, polygon, pageNumber)
    elif ("Nom" in key or "rand" in key):
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
    else:
        val = " ".join([i.capitalize() for i in val.split(" ")])
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
    return extraction

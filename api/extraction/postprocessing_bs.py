def postprocessing_bs(extraction, name, field_value, field, polygon, pageNumber):
    from api.extraction.extraction_function import extraction_put_val
    from api_insee import ApiInsee
    errorMsg = "OCR - Erreur de lecture : "
    key, val, conf = name, field_value, field.confidence

    val = " ".join([i.capitalize() for i in val.split(" ")])
    if conf < 0.2:
        extraction = extraction_put_val(extraction, key, errorMsg +
                                        val, conf, polygon, pageNumber)
    elif "Siret" == key:
        api = ApiInsee(
            key="AM619tK2njy3o2Bdr2hhcFvcSnYa",
            secret="fA6inziXnSn4nAB0ifGle8fh0osa"
        )
        data = api.siret(val).get()
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)
        try:
            employeurSiret = (data["etablissement"]["uniteLegale"]["denominationUniteLegale"] +
                              ' ({})'.format(data["etablissement"]["uniteLegale"]["categorieEntreprise"]))
            adresseSiret = (data["etablissement"]["adresseEtablissement"]["numeroVoieEtablissement"]+' ' +
                            data["etablissement"]["adresseEtablissement"]["typeVoieEtablissement"]+' ' +
                            data["etablissement"]["adresseEtablissement"]["libelleVoieEtablissement"])
            cp = data["etablissement"]["adresseEtablissement"]["codePostalEtablissement"] + \
                ' ' + \
                data["etablissement"]["adresseEtablissement"]["libelleCommuneEtablissement"]
            extraction = extraction_put_val(extraction, "Employeur SIRET ",
                                            employeurSiret, conf, None, pageNumber)
            extraction = extraction_put_val(extraction, "Adresse SIRET ",
                                            adresseSiret, conf, None, pageNumber)
            extraction = extraction_put_val(extraction, "CP SIRET ",
                                            cp, conf, None, pageNumber)
        except:
            pass
    elif "Salaire" in key or "Revenu" in key:
        val = val.replace(" ", "")
        if len(val) > 8:
            extraction = extraction_put_val(
                extraction, key, errorMsg+val, conf, polygon, pageNumber)
        else:
            extraction = extraction_put_val(extraction, key, val,
                                            conf, polygon, pageNumber)
    else:
        extraction = extraction_put_val(
            extraction, key, val, conf, polygon, pageNumber)

    return extraction

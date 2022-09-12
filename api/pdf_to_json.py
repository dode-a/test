from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
import json

from datetime import *

import pandas as pd

# INITIALISATION DE L'ACCES A AZURE FORM RECOGNISER
credentials = json.load(open('api/credential.json'))
API_KEY = credentials['API_KEY']
ENDPOINT = credentials['ENDPOINT']
MODELS = credentials['MODELS']
# global document_analysis_client
document_analysis_client = DocumentAnalysisClient(
    endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))

# Azure renvoie la positions des points des boites englobantes / par 72
SUPER_PIX = 72


# Renvoie l'extraction faite par notre model à partir d'un pdf
def pdf_to_json(poller, pdf, MODEL):
    from api.extraction.extraction_function import extraction_toDict
    if MODEL != "prebuilt-layout":
        result = poller.result()
        extraction = {"Score": {'value': None, 'box': None, 'pageNumber': 0}, "Titre": {
            'value': None, 'box': None, 'pageNumber': 0}, "Fichier": {'value': None, 'box': None, 'pageNumber': 0}}
        extraction["Fichier"]["value"] = pdf
        for idx, document in enumerate(result.documents):
            print("document.confidence", document.confidence)
            extraction["Score"]["value"] = document.confidence
            for name, field in document.fields.items():
                field_value = field.value if field.value else field.content

                if field_value:
                    pageNumber = field.bounding_regions[0].page_number
                    polygon = field.bounding_regions[0].polygon
                    polygon = [SUPER_PIX*polygon[0][0], SUPER_PIX*polygon[0]
                               [1], SUPER_PIX*polygon[1][0], SUPER_PIX*polygon[-1][-1]]
                    try:
                        extraction_toDict(MODEL, extraction, name,
                                          field_value, field, polygon, pageNumber)
                    except:
                        return({"Score": {'value': 0, 'box': None, 'pageNumber': 0}, "Titre": {
                            'value': "UNKNOWN  : You probably sent a pdf of a BS to as CNI model", 'box': None, 'pageNumber': 0}})

        if extraction["Score"]["value"] < 0.2:
            return({"Score": {'value': extraction["Score"]["value"], 'box': None, 'pageNumber': 0}, "Titre": {
                'value': "OCR - Erreur de lecture - Vérifier la qualité du pdf", 'box': None, 'pageNumber': 0}})

        return(extraction)
    else:
        from api.extraction.postprocessing_rdc import postprocessing_rdc
        all_table = []
        result = poller.result()
        for table_idx, table in enumerate(result.tables):
            no_table = True
            data = [["" for i in range(table.column_count)]
                    for i in range(table.row_count)]
            for cell in table.cells:
                content = str(cell.content)
                if len(content) < 1:
                    content = ""
                data[cell.row_index][cell.column_index] = content

            data = pd.DataFrame.from_records(data, columns=data[0]).replace('', None).dropna(
                axis=0, how='all').dropna(axis=1, how='all').to_numpy().tolist()

            for i in range(len(all_table)):
                if (len(all_table[i][0]) == (len(data[0]))):
                    all_table[i] = all_table[i]+data[1:]
                    no_table = False
                else:
                    pass

            if no_table:
                all_table.append(data[1:])
        datab = postprocessing_rdc(all_table)
        # print(datab)
        # print("====================================")
        pdf_storage = "api/static/pdf_storage/PDF"
        n = int((len(os.listdir(pdf_storage[:-4]))/2) % 11)
        filename_ = "{}.pdf".format(n)
        return datab.to_json(pdf_storage.replace('PDF', filename_).replace('.pdf', ".json"), orient='records')

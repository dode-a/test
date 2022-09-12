from flask import Flask, redirect, render_template
import copy
from flask import request, jsonify
from json2html import *
import base64
from io import BytesIO, BufferedReader
import os
import json
import fitz
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from api.pdf_to_json import *
ALLOWED_EXTENSIONS = {'pdf'}


def app_main_function(request):
    headers = request.headers
    auth = headers.get("Api-Key")
    if auth != 'KiiltOcrApi#2022':
        return jsonify({"message": "ERROR: Wrong Key"})
    json_ = (request.get_json())

    decoded = str(json_["pdf"]).encode("utf-8")

    credentials = json.load(open('api/credential.json'))
    MODEL = credentials["MODELS"][json_["model"]]
    MODEL_ID = os.getenv("CUSTOM_BUILT_MODEL_ID", MODEL)
    doc = BufferedReader(BytesIO(base64.b64decode(decoded)))
    print(MODEL_ID)
    poller = document_analysis_client.begin_analyze_document(
        model=MODEL_ID, document=doc)
    feeds = json.dumps(pdf_to_json(poller, json_["filename"], MODEL),
                       indent=2, ensure_ascii=False)
    return feeds


def display_dict_from_ocrdict(ocrdict, MODEL):
    if MODEL == "RDC":
        return ocrdict
    display_dictionary = copy.deepcopy(ocrdict)
    for key in display_dictionary:
        if type(display_dictionary[key]) == dict:
            display_dictionary[key].pop('box', None)
            display_dictionary[key] = display_dictionary[key]["value"]
    return display_dictionary


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

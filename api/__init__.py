from api_insee import ApiInsee
from datetime import *
from api.pdf_to_json import *
from api.functions import *
from api.display_box import add_display_box_to_pdf
from flask import Flask, redirect, render_template

app = Flask(__name__)


# Cette méthode permet de créer la page web de test de l'océrisation + Postprocesing
@app.route('/', methods=['GET', 'POST'])
def upload_file5():
    # ============================================== 1 - Initialisation des variables et vérifications -==============================================
    if request.method == 'POST':
        pdf_storage = "api/static/pdf_storage/PDF"
        # On vérifie que l'on a bien le bon ficher
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        # On vérifie que l'extention du fichier est conforme à ce que l'on attend
        if file and allowed_file(file.filename):

            MODEL_req = (request.form.get('Model'))
            credentials = json.load(open('api/credential.json'))

            MODEL = credentials["MODELS"][MODEL_req]
            # ============================================== 2 - Stockage des pdfs et des jsons extrait -==============================================
            # Il faudra sauvegarder le ficher dans la BD Brut pour le moment il est stocké dans le code, on stock uniquement les 5 derniers
            filename = secure_filename(file.filename)
            # on utilise filename_ afin d'en garder que 10
            n = int((len(os.listdir(pdf_storage[:-4]))/2) % 11)
            filename_ = "{}.pdf".format(n)
            file_ = pdf_storage.replace('PDF', filename_)
            file.save(file_)

            with open(file_, "rb") as pdf_file:
                MODEL_ID = os.getenv("CUSTOM_BUILT_MODEL_ID", MODEL)
                poller = document_analysis_client.begin_analyze_document(
                    model=MODEL_ID, document=BufferedReader(
                        pdf_file)
                )

            ocrdict = pdf_to_json(poller, filename, MODEL)
            print("**************************************")
            print(type(ocrdict))
            # print(ocrdict)
            print("**************************************")

            # Il faudra stocké le json dans la BD PostgreSQL pour le moment on le stock dans /api/static/pdf_storage
            if MODEL_req != "RDC":
                with open(pdf_storage.replace('PDF', filename_).replace('.pdf', ".json"), 'w') as fp:
                    json.dump(ocrdict, fp)

            # ============================================== 3 - Affichage du pdf avec boite englobante et de l'extraction -===========================

            encoded = add_display_box_to_pdf(
                filename=pdf_storage.replace('PDF', filename_), json_file=pdf_storage.replace('PDF', filename_).replace('.pdf', ".json"), MODEL=MODEL_req)

            with open(pdf_storage.replace('PDF', filename_).replace('.pdf', ".json"), 'r') as j:
                ocrdict = json.loads(j.read())
            # return render_template("index.html", extraction_json=str(json2html.convert(json=json.dumps(table_json,
            #                                                                                            indent=2, ensure_ascii=False))),
            #                        embed_pdf="""<iframe src="data:application/pdf;base64,PDF" width="800" height="650"></iframe>""".replace('PDF', encoded))

            return render_template("index.html", extraction_json=str(json2html.convert(json=json.dumps(display_dict_from_ocrdict(ocrdict, MODEL_req),
                                                                                                       indent=2, ensure_ascii=False))),
                                   embed_pdf="""<iframe src="data:application/pdf;base64,PDF" width="800" height="650"></iframe>""".replace('PDF', encoded))

    return render_template("index.html")


# Permet d'envoyer des fichiers pdfs en base64 via une requête
@ app.route('/ocr', methods=['POST'])
def create_feature_ocr():
    return app_main_function(request)


# Permet de modifier les models via une requêtes en mettant à jour le fichier credential.json
@ app.route('/models', methods=['POST'])
def models():
    headers = request.headers
    auth = headers.get("Api-Key")
    if auth != 'KiiltOcrApi#2022':
        return jsonify({"message": "ERROR: Wrong Key"})
    json_ = (request.get_json())

    credentials = json.load(open('api/credential.json'))
    credentials["MODELS"] = json_["MODELS"]
    print(credentials)
    with open('api/credential.json', 'w') as fp:
        json.dump(credentials, fp)
    return jsonify({"message": "OK it was changed", "new_credentials": credentials})

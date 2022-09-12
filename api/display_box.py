import fitz
import json
import base64


def add_display_box_to_pdf(filename, json_file, MODEL):
    doc = fitz.open(filename)
    print(MODEL)
    if MODEL != "RDC":
        with open(json_file) as json_file:
            data = json.load(json_file)
            data = sorted(data.items(), key=lambda x: x[1]['pageNumber'])
            for element in data:
                if(element[1]['box'] != None):
                    page = doc.load_page(element[1]['pageNumber']-1)
                    if not page.is_wrapped:
                        page.wrap_contents()
                    rect_dezoom = 4
                    rotation = page.derotation_matrix
                    p1 = element[1]['box'][:2]
                    p2 = element[1]['box'][-2:]
                    p3 = fitz.Point(
                        p2[0] + rect_dezoom, (0.35*p1[1]+0.65*p2[1]))*rotation
                    p1 = fitz.Point(p1)*rotation
                    p2 = fitz.Point(p2)*rotation
                    point = (min(p1[0], p2[0])-rect_dezoom, min(p1[1], p2[1])-rect_dezoom, max(
                        p1[0], p2[0])+rect_dezoom, max(p1[1], p2[1])+rect_dezoom)
                    page.draw_rect(
                        point, dashes="[1 1] 0", color=element[1]['color'], fill_opacity=0.7, width=1.4)
                    page.insert_text(p3, "<-"+element[0].split(
                        ' ')[0], fontsize=13, color=element[1]['color'], fill_opacity=0.7, rotate=(page.rotation))
    pl = doc.tobytes()
    encoded = base64.b64encode(pl).decode("utf-8")
    return encoded

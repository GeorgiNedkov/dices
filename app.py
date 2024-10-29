from flask import Flask, render_template, request, send_file
from PIL import Image
from io import BytesIO
import cv2 as cv
import numpy as np
from source.detect import detect

app = Flask(__name__)


@app.route("/", methods=["GET"])
def getView():
    return render_template("index.html")


@app.route("/prediction/image", methods=["POST"])
def upload_file_i():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400
        if file:
            pil_image = Image.open(file.stream).convert("RGB")
            cvImage = np.array(pil_image)
            cvImage = detect(cvImage)["image"]

            im_pil = Image.fromarray(cvImage)
            img_io = BytesIO()
            im_pil.save(img_io, "PNG")
            img_io.seek(0)
            # return send_file(img_io, mimetype='image/png')  # Change download in separatre browser tab
            return send_file(
                img_io,
                mimetype="image/png",
                as_attachment=True,
                download_name="_rmbg.png",
            )


@app.route("/prediction/json", methods=["POST"])
def upload_file_j():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400
        if file:
            pil_image = Image.open(file.stream).convert("L")
            cvImage = np.array(pil_image)
            result = detect(cvImage)

            # return send_file(img_io, mimetype='image/png')  # Change download in separatre browser tab
            return result["json"]


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=31415)

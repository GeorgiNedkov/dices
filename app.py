from flask import Flask, render_template, request, send_file
from io import BytesIO
import cv2 as cv
import numpy as np
from source.detect_2 import detect

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
            file_bytes = np.frombuffer(file.stream.read(), np.uint8)
            cvImage = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)
            cvImage = detect(cvImage)["image"]

            success, encoded_image = cv.imencode(".png", cvImage)
            if not success:
                raise ValueError("Failed to encode image")

            img_io = BytesIO(encoded_image.tobytes())
            img_io.seek(0)

            # return send_file(img_io, mimetype='image/png')  # Change download in separatre browser tab
            return send_file(
                img_io,
                mimetype="image/png",
                as_attachment=True,
                download_name=f"{file.filename}_result.png",
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
            print("start")
            file_bytes = np.frombuffer(file.stream.read(), np.uint8)
            cvImage = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)

            result = detect(cvImage)
            print("end")

            # return send_file(img_io, mimetype='image/png')  # Change download in separatre browser tab
            return result["json"]


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080, threads=8)

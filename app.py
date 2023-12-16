from flask import Flask, request, send_from_directory, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

# Ruta donde se almacenarán las imágenes procesadas
UPLOAD_FOLDER = os.path.join(os.getcwd(), "mysite", "image")

# Asegurémonos de que la carpeta de carga exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def hello_world():
    return "Listar filtros de OpenCV: binarizado, escala de grises, negativo, suavizado, bordes, espejo, rotación, difuminado, contraste, brillo, saturación, tono, sepia, filtro de color, filtro de color con máscara, filtro de color con máscara"


def aplicar_filtro(img, filtro):
    # Lógica para aplicar diferentes filtros
    if filtro == "binarizado":
        _, binarizada = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return binarizada
    elif filtro == "escala_de_grises":
        # Agrega lógica para otros filtros según sea necesario
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif filtro == "negativo":
        return cv2.bitwise_not(img)
    elif filtro == "suavizado":
        return cv2.GaussianBlur(img, (5, 5), 0)
    elif filtro == "binarizadoinverso":
        return cv2.bitwise_not(cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1])


@app.route("/procesar_imagen", methods=["POST"])
def procesar_imagen():
    try:
        imagen = request.files["imagen"]
        filtro = request.form.get("filtro", "binarizado")

        contenido = imagen.read()
        npimg = np.frombuffer(contenido, np.uint8)
        img = cv2.imdecode(
            npimg, cv2.IMREAD_COLOR
        )  # Cambiado a COLOR para manejar imágenes en color

        img_procesada = aplicar_filtro(img, filtro)

        _, img_encoded = cv2.imencode(".png", img_procesada)
        img_bytes = img_encoded.tobytes()

        # Asegurémonos de que la carpeta de uploads exista
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Guardar la imagen con el nombre del filtro en la carpeta UPLOAD_FOLDER
        img_path = os.path.join(UPLOAD_FOLDER, f"{filtro}.png")
        with open(img_path, "wb") as img_file:
            img_file.write(img_bytes)

        # Devolver la ruta relativa de la imagen almacenada
        relative_path = os.path.relpath(img_path, UPLOAD_FOLDER)
        return jsonify({"message": relative_path})

    except Exception as e:
        return str(e), 500


# Ruta para servir archivos estáticos desde la carpeta de uploads
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)

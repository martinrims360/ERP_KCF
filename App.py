from flask import Flask
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_usuarios import cotizaciones_bp

app = Flask(__name__)

app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
print("ESTE ES EL PROYECTO CORRECTO")

if __name__ == "__main__":
    app.run(debug=True)
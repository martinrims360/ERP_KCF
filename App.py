from flask import Flask
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.kardex import kardex_bp
# ❌ Elimina esta línea - está sobrescribiendo el blueprint correcto
# from routes.mantenedor_usuarios import cotizaciones_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(kardex_bp)

print("🚀 ESTE ES EL PROYECTO CORRECTO")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
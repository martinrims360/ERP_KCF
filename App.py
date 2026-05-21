from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import base64

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
_a = base64.b64decode('cG9zdGdyZXNxbDovLy9wb3N0Z3Jlcy50a2Ztd3ZzZW52Z3B5ZXh2ZGNhdDphZG1pbjM1NjE5NjdrY2ZAYXdzLTEtdXMtZWFzdC0xLnBvb2xlci5zdXBhYmFzZS5jb206NjU0My9wb3N0Z3Jlcw==').decode('utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = _a
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sb_secret_k56lhPYVINqZMj_BZexRbw_JzeBx8Hx'

db = SQLAlchemy()
db.init_app(app)

# ==================== BLUEPRINTS ====================
from routes.usuarios import usuarios_bp
from routes.cotizaciones import cotizaciones_bp
from routes.mantenedor_productos import productos_bp
from routes.kardex import kardex_bp

# Registrar blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(cotizaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(kardex_bp, url_prefix='/api')  # ✅ CAMBIO IMPORTANTE

# ✅ Verificar blueprints activos
print("Blueprints registrados:", app.blueprints.keys())

# ✅ Ruta de prueba para verificar que el servidor funciona
@app.route('/')
def home():
    return jsonify({'message': 'Servidor funcionando'})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
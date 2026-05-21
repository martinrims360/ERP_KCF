from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# ==================== CONFIGURACIÓN SUPABASE ====================
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-desarrollo')

# Instancia de SQLAlchemy
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
app.register_blueprint(kardex_bp)

print("🚀 Servidor Flask iniciado correctamente con Supabase")
print("📦 Blueprints: usuarios, cotizaciones, productos, kardex")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea tablas si no existen
    app.run(debug=True, host='0.0.0.0', port=5000)

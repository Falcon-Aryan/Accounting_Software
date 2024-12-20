from flask import Flask
from flask_cors import CORS
from routes.customers import bp as customers_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(customers_bp, url_prefix='/api/customers')

if __name__ == '__main__':
    app.run(debug=True, port=8000)

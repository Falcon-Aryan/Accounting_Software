from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Import and register blueprints
    from app.advanced.routes import advanced_bp
    from app.chart_of_accounts.routes import chart_of_accounts_bp
    from app.company.routes import company_bp
    from app.customers.routes import customers_bp
    from app.estimates.routes import estimates_bp
    from app.invoices.routes import invoices_bp
    from app.transactions.routes import transactions_bp
    from app.products.routes import products_bp

    # Register all blueprints with their prefixes
    app.register_blueprint(advanced_bp, url_prefix='/api/advanced')
    app.register_blueprint(chart_of_accounts_bp, url_prefix='/api/coa')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(estimates_bp, url_prefix='/api/estimates')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(products_bp, url_prefix='/api/ProdServ')

    return app

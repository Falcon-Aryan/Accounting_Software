from flask import Blueprint

chart_of_accounts_bp = Blueprint('chart_of_accounts', __name__)

from . import routes

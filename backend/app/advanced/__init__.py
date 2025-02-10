from flask import Blueprint

advanced_bp = Blueprint('advanced', __name__)

from . import routes

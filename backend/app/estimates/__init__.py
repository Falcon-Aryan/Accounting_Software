from flask import Blueprint

estimates_bp = Blueprint('estimates', __name__)

from . import routes

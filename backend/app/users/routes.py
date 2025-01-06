from flask import request, jsonify
from .models import UserModel
from app.users import users_bp

@users_bp.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Create user in Firebase
        user = UserModel.create_user(email, password)
        
        # Sync the new user with our users.json
        user = UserModel.sync_firebase_user(user['uid'])
        
        return jsonify(user), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/sync', methods=['POST'])
def sync_users():
    """Sync users from Firebase to local storage"""
    try:
        users = UserModel.sync_all_firebase_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/sync/<uid>', methods=['POST'])
def sync_user(uid):
    try:
        user = UserModel.sync_firebase_user(uid)
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/getAll', methods=['GET'])
def get_all_users():
    try:
        users = UserModel.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/get/<uid>', methods=['GET'])
def get_user(uid):
    try:
        user = UserModel.get_user(uid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<uid>/profile', methods=['GET', 'PUT'])
def user_profile(uid):
    """Get or update user profile"""
    try:
        if request.method == 'GET':
            users_data = UserModel._read_users_file()
            if uid not in users_data['users']:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(users_data['users'][uid])
            
        elif request.method == 'PUT':
            data = request.get_json()
            updated_user = UserModel.update_user_profile(uid, data)
            return jsonify(updated_user)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@users_bp.route('/update/<uid>', methods=['PUT'])
def update_user(uid):
    try:
        data = request.get_json()
        user = UserModel.update_user(uid, data)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/delete/<uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        success = UserModel.delete_user(uid)
        
        if not success:
            return jsonify({'error': 'User not found'}), 404
            
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from database.db import execute_query
from dotenv import load_dotenv

load_dotenv()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': '所有字段都是必填的'}), 400

    # 检查用户名是否已存在
    success, result = execute_query(
        "SELECT id FROM users WHERE username = %s OR email = %s",
        (username, email)
    )
    
    if not success:
        return jsonify({'error': '数据库错误'}), 500
    
    if result:
        return jsonify({'error': '用户名或邮箱已存在'}), 409

    # 创建新用户
    hashed_password = generate_password_hash(password)
    success, user_id = execute_query(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, hashed_password)
    )

    if not success:
        return jsonify({'error': '注册失败'}), 500

    return jsonify({'message': '注册成功', 'user_id': user_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'error': '用户名和密码都是必填的'}), 400

    # 查询用户
    success, users = execute_query(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username,)
    )

    if not success:
        return jsonify({'error': '数据库错误'}), 500

    if not users:
        return jsonify({'error': '用户名或密码错误'}), 401

    user = users[0]
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成 JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

    return jsonify({
        'message': '登录成功',
        'token': token,
        'username': user['username']
    }), 200

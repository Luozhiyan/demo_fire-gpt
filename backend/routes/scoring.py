from flask import Blueprint, request, jsonify
from database.db import execute_query
from functools import wraps
import jwt
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

scoring_bp = Blueprint('scoring', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': '未提供token'}), 401
        
        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            success, users = execute_query(
                "SELECT id, username FROM users WHERE id = %s",
                (data['user_id'],)
            )
            
            if not success or not users:
                logger.error(f"用户验证失败: user_id={data['user_id']}")
                return jsonify({'error': '用户不存在'}), 401
                
            current_user = users[0]
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return jsonify({'error': '无效的token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@scoring_bp.route('/api/scoring', methods=['POST'])
@token_required
def submit_score(current_user):
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        score = data.get('score')
        comments = data.get('comments', '')
        
        logger.debug(f"收到评分请求: user_id={current_user['id']}, report_id={report_id}, score={score}")
        
        if not all([report_id, score]):
            return jsonify({'error': '缺少必要参数'}), 400
            
        if not isinstance(score, int) or score < 0 or score > 100:
            return jsonify({'error': '分数必须是0-100之间的整数'}), 400
        
        # 检查是否已有评分记录
        success, existing = execute_query(
            "SELECT id FROM scores WHERE user_id = %s AND report_id = %s",
            (current_user['id'], report_id)
        )
        
        if not success:
            logger.error("检查已有评分记录失败")
            return jsonify({'error': '数据库查询失败'}), 500
        
        if existing:
            # 更新评分
            logger.debug(f"更新评分记录: user_id={current_user['id']}, report_id={report_id}")
            success, _ = execute_query(
                """UPDATE scores 
                   SET score = %s, comments = %s, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = %s AND report_id = %s""",
                (score, comments, current_user['id'], report_id)
            )
        else:
            # 新增评分
            logger.debug(f"创建新评分记录: user_id={current_user['id']}, report_id={report_id}")
            success, _ = execute_query(
                """INSERT INTO scores (user_id, report_id, score, comments) 
                   VALUES (%s, %s, %s, %s)""",
                (current_user['id'], report_id, score, comments)
            )
        
        if not success:
            logger.error("保存评分记录失败")
            return jsonify({'error': '评分提交失败'}), 500
            
        return jsonify({'message': '评分提交成功'}), 200
    except Exception as e:
        logger.error(f"评分提交过程中发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scoring_bp.route('/api/scoring/<report_id>', methods=['GET'])
@token_required
def get_score(current_user, report_id):
    try:
        success, scores = execute_query(
            """SELECT score, comments, created_at, updated_at 
               FROM scores 
               WHERE user_id = %s AND report_id = %s""",
            (current_user['id'], report_id)
        )
        
        if not success:
            logger.error(f"获取评分记录失败: user_id={current_user['id']}, report_id={report_id}")
            return jsonify({'error': '获取评分失败'}), 500
            
        if not scores:
            return jsonify({'message': '未找到评分记录'}), 404
            
        return jsonify(scores[0]), 200
    except Exception as e:
        logger.error(f"获取评分记录时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scoring_bp.route('/api/user_scores', methods=['GET'])
@token_required
def get_user_scores(current_user):
    """获取当前用户的所有评分记录"""
    try:
        success, scores = execute_query(
            """SELECT report_id, score, comments 
               FROM scores 
               WHERE user_id = %s""",
            (current_user['id'],)
        )
        
        if not success:
            logger.error(f"获取用户评分列表失败: user_id={current_user['id']}")
            return jsonify({'error': '获取评分列表失败'}), 500
            
        return jsonify(scores), 200
        
    except Exception as e:
        logger.error(f"获取用户评分列表时发生错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

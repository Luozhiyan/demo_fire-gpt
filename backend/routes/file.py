from flask import Blueprint, request, jsonify, send_file
from utils.file_handler import save_file, generate_preview
import os

bp = Blueprint('file', __name__, url_prefix='/api/files')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    result = save_file(file, UPLOAD_FOLDER)
    if result:
        return jsonify(result)
    return jsonify({'error': '文件上传失败'}), 400

@bp.route('/preview/<path:filename>', methods=['GET'])
def preview_file(filename):
    """获取文件预览"""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    preview = generate_preview(file_path)
    if preview:
        return jsonify(preview)
    return jsonify({'error': '无法生成预览'}), 400

@bp.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """下载文件"""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(file_path, as_attachment=True)

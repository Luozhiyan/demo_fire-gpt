import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from routes.file import bp as file_bp
from routes.report import bp as report_bp
from routes.case import bp as case_bp
from routes.auth import auth_bp
from routes.scoring import scoring_bp
from utils.file_handler import save_file, generate_preview, list_files, get_file_type, delete_file
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置文件上传目录
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 限制上传文件大小为5MB

# 注册蓝图
app.register_blueprint(file_bp)
app.register_blueprint(report_bp, url_prefix='/api')
app.register_blueprint(case_bp)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(scoring_bp)

@app.route('/')
def index():
    return jsonify({"message": "Fire Incident Investigation API"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件处理"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        result = save_file(file, app.config['UPLOAD_FOLDER'])
        if result:
            return jsonify(result)
        
        return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        print(f"文件上传失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """获取所有上传的文件列表"""
    try:
        files = list_files(app.config['UPLOAD_FOLDER'])
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<file_uid>', methods=['DELETE'])
def delete_uploaded_file(file_uid):
    """删除上传的文件"""
    try:
        success = delete_file(file_uid, app.config['UPLOAD_FOLDER'])
        if success:
            return jsonify({'message': '文件删除成功'})
        return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/<filename>')
def preview_file(filename):
    """预览文件"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        # 获取文件类型
        file_type = get_file_type(file_path)
        
        # 图片文件直接返回
        if file_type.startswith('image/'):
            return send_file(file_path)
        
        # PDF文件直接返回
        if file_type == 'application/pdf' or filename.lower().endswith('.pdf'):
            return send_file(file_path, mimetype='application/pdf')
        
        # 其他文件尝试生成预览
        preview = generate_preview(file_path)
        if preview and preview.get('path'):
            return send_file(preview['path'])
        
        return jsonify({'error': '不支持的文件类型预览'}), 400
        
    except Exception as e:
        print(f"预览失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

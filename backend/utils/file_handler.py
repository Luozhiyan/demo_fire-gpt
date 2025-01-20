import os
import mimetypes
from PIL import Image
from datetime import datetime
from werkzeug.utils import secure_filename
import fitz

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx',
    'fig', 'sketch', 'xd'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """获取文件类型"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def save_file(file, upload_folder):
    """保存上传的文件"""
    try:
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            # 添加时间戳到文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(original_filename)
            new_filename = f"{name}_{timestamp}{ext}"
            
            # 确保上传目录存在
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, new_filename)
            file.save(file_path)
            
            return {
                'filename': new_filename,
                'original_name': original_filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'type': get_file_type(file_path),
                'upload_time': timestamp
            }
    except Exception as e:
        print(f"文件保存失败: {str(e)}")
        return None
    return None

def generate_preview(file_path):
    """生成文件预览"""
    if not os.path.exists(file_path):
        return None
        
    mime_type = get_file_type(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # 图片文件直接返回路径
        if mime_type.startswith('image/'):
            return {'type': 'image', 'path': file_path}
        
        # PDF文件处理
        elif mime_type == 'application/pdf' or file_ext == '.pdf':
            return {'type': 'pdf', 'path': file_path}
        
        # Word文档处理
        elif file_ext in ['.doc', '.docx']:
            return {'type': 'doc', 'path': file_path}
        
        # 其他类型文件
        return {'type': 'other', 'path': None}
    except Exception as e:
        print(f"预览生成失败: {str(e)}")
        return None

def list_files(upload_folder):
    """列出上传目录中的所有文件"""
    try:
        if not os.path.exists(upload_folder):
            return []
            
        files = []
        for filename in os.listdir(upload_folder):
            if filename.endswith('_preview.png'):  # 跳过预览文件
                continue
                
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                # 获取原始文件名（去掉时间戳）
                name, ext = os.path.splitext(filename)
                name_parts = name.rsplit('_', 2)  # 分割出时间戳部分
                
                if len(name_parts) >= 3:  # 如果包含时间戳
                    original_name = name_parts[0] + ext
                    timestamp = name_parts[-2] + '_' + name_parts[-1]  # 组合时间戳
                    # 格式化时间戳为易读格式，使用点号分隔日期，不显示秒数
                    formatted_time = f"{timestamp[:4]}.{timestamp[4:6]}.{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}"
                else:
                    original_name = filename
                    formatted_time = datetime.now().strftime('%Y.%m.%d %H:%M')
                
                files.append({
                    'uid': filename,
                    'filename': filename,
                    'original_name': original_name,
                    'size': os.path.getsize(file_path),
                    'type': get_file_type(file_path),
                    'upload_time': formatted_time
                })
        return sorted(files, key=lambda x: x['upload_time'], reverse=True)
    except Exception as e:
        print(f"获取文件列表失败: {str(e)}")
        return []

def delete_file(file_uid, upload_folder):
    """删除指定的文件
    
    Args:
        file_uid: 文件的唯一标识符（文件名）
        upload_folder: 上传文件目录
        
    Returns:
        bool: 删除是否成功
    """
    try:
        file_path = os.path.join(upload_folder, secure_filename(file_uid))
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {str(e)}")
        return False

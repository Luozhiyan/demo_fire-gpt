import os
import json
from flask import Blueprint, jsonify, send_file, request
from pathlib import Path
from datetime import datetime

bp = Blueprint('case', __name__, url_prefix='/api/cases')

# 使用相对路径获取case_show目录
CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'case_show')

@bp.route('/list', methods=['GET'])
def list_cases():
    """获取所有案例列表"""
    try:
        cases = []
        if not os.path.exists(CASE_DIR):
            return jsonify({'error': 'Case directory not found'}), 404
            
        for case_name in os.listdir(CASE_DIR):
            try:
                case_path = os.path.join(CASE_DIR, case_name)
                if os.path.isdir(case_path):
                    cases.append({
                        'id': case_name,
                        'name': f'{case_name}火灾事故'
                    })
            except Exception as e:
                print(f"Error processing case {case_name}: {str(e)}")
                continue
                
        return jsonify(cases)
    except Exception as e:
        print(f"Error in list_cases: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<case_id>/files', methods=['GET'])
def list_case_files(case_id):
    """获取案例的文件结构"""
    try:
        case_path = os.path.join(CASE_DIR, case_id)
        if not os.path.exists(case_path):
            return jsonify({'error': '案例不存在'}), 404

        def get_dir_structure(path):
            items = []
            for item in os.listdir(path):
                # 只处理pic和record目录
                if item not in ['pic', 'record']:
                    continue
                    
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    children = []
                    for child in os.listdir(item_path):
                        child_path = os.path.join(item_path, child)
                        if os.path.isfile(child_path):
                            children.append({
                                'name': child,
                                'type': 'file',
                                'extension': os.path.splitext(child)[1],
                                'parent': {'name': item}
                            })
                    items.append({
                        'name': item,
                        'type': 'directory',
                        'children': children
                    })
            return items

        structure = get_dir_structure(case_path)
        return jsonify(structure)
    except Exception as e:
        print(f"Error in list_case_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<case_id>/file', methods=['GET'])
def get_case_file(case_id):
    """获取案例中的具体文件内容"""
    try:
        file_path = request.args.get('path', '')
        if not file_path:
            return jsonify({'error': '未指定文件路径'}), 400

        full_path = os.path.join(CASE_DIR, case_id, file_path)
        if not os.path.exists(full_path):
            return jsonify({'error': '文件不存在'}), 404

        # 如果是JSON文件，返回解析后的内容
        if full_path.endswith('.json'):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f))
            except Exception as e:
                return jsonify({'error': f'JSON解析错误: {str(e)}'}), 500

        # 如果是图片，直接返回文件
        if any(full_path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return send_file(full_path)

        # 如果是HTML文件，返回文件内容
        if full_path.endswith('.html'):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read(), 200, {'Content-Type': 'text/html'}
            except Exception as e:
                return jsonify({'error': f'HTML读取错误: {str(e)}'}), 500

        return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        print(f"Error in get_case_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<case_id>/score', methods=['POST'])
def submit_score(case_id):
    """提交评分"""
    try:
        case_path = os.path.join(CASE_DIR, case_id)
        if not os.path.exists(case_path):
            return jsonify({'error': '案例不存在'}), 404
        
        data = request.get_json()
        score = data.get('score')
        comment = data.get('comment')
        
        if score is None:
            return jsonify({'error': '评分不能为空'}), 400
        
        # 将评分保存到文件系统
        score_dir = os.path.join(case_path, 'scores')
        if not os.path.exists(score_dir):
            os.makedirs(score_dir)
            
        score_file = os.path.join(score_dir, 'expert_score.json')
        score_data = {
            'score': score,
            'comment': comment,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(score_file, 'w', encoding='utf-8') as f:
            json.dump(score_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'message': '评分提交成功'})
    except Exception as e:
        print(f"Error in submit_score: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<case_id>/graph', methods=['GET'])
def get_case_graph(case_id):
    """获取案例的知识图谱"""
    try:
        graph_path = os.path.join(CASE_DIR, case_id, 'graph.jpg')  # 假设图谱是jpg格式
        if not os.path.exists(graph_path):
            return jsonify({'error': '知识图谱不存在'}), 404
        
        return send_file(graph_path)
    except Exception as e:
        print(f"Error in get_case_graph: {str(e)}")
        return jsonify({'error': str(e)}), 500

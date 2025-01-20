from flask import Blueprint, jsonify, send_file, abort
import os
import json
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('report', __name__, url_prefix='/api')

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'case_show')
logger.info(f"CASE_DIR set to: {CASE_DIR}")

@bp.route('/reports')
def get_reports():
    """获取所有案例列表"""
    logger.info("Handling /reports request")
    cases = []
    try:
        if not os.path.exists(CASE_DIR):
            logger.error(f"CASE_DIR does not exist: {CASE_DIR}")
            return jsonify({'error': 'Case directory not found'}), 404
            
        logger.debug(f"Listing directory: {CASE_DIR}")
        for case_name in os.listdir(CASE_DIR):
            case_path = os.path.join(CASE_DIR, case_name)
            logger.debug(f"Found case: {case_name}, path: {case_path}")
            if os.path.isdir(case_path):
                cases.append({
                    'id': case_name,
                    'name': f'{case_name}火灾事故'
                })
        logger.info(f"Found {len(cases)} cases")
        return jsonify(cases)
    except Exception as e:
        logger.error(f"Error in get_reports: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/<case_id>/files')
def get_case_files(case_id):
    """获取案例文件列表"""
    logger.info(f"Handling /reports/{case_id}/files request")
    case_path = os.path.join(CASE_DIR, case_id)
    if not os.path.exists(case_path):
        logger.error(f"Case directory not found: {case_path}")
        abort(404)
        
    pics = []
    records = []
    
    # 获取图片列表
    pic_path = os.path.join(case_path, 'pic')
    logger.debug(f"Listing directory: {pic_path}")
    if os.path.exists(pic_path):
        pics = [f for f in os.listdir(pic_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        logger.info(f"Found {len(pics)} pictures")
        
    # 获取记录列表
    record_path = os.path.join(case_path, 'record')
    logger.debug(f"Listing directory: {record_path}")
    if os.path.exists(record_path):
        records = [f for f in os.listdir(record_path) if f.lower().endswith('.json')]
        logger.info(f"Found {len(records)} records")
        
    return jsonify({
        'pics': pics,
        'records': records
    })

@bp.route('/reports/<case_id>/report')
def get_case_report(case_id):
    """获取案例报告"""
    logger.info(f"Handling /reports/{case_id}/report request")
    report_path = os.path.join(CASE_DIR, case_id, 'report.json')
    if not os.path.exists(report_path):
        logger.error(f"Report file not found: {report_path}")
        abort(404)
        
    logger.debug(f"Loading report from: {report_path}")
    with open(report_path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

@bp.route('/reports/<case_id>/file/<folder>/<filename>')
def get_case_file(case_id, folder, filename):
    """获取案例文件内容"""
    logger.info(f"Handling /reports/{case_id}/file/{folder}/{filename} request")
    file_path = os.path.join(CASE_DIR, case_id, folder, filename)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        abort(404)
        
    logger.debug(f"Loading file from: {file_path}")
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return send_file(file_path)

@bp.route('/reports/<case_id>/graph')
def get_case_graph(case_id):
    """获取案例知识图谱"""
    logger.info(f"Handling /reports/{case_id}/graph request")
    graph_path = os.path.join(CASE_DIR, case_id, 'graph.html')
    if not os.path.exists(graph_path):
        logger.error(f"Graph file not found: {graph_path}")
        abort(404)
        
    logger.debug(f"Loading graph from: {graph_path}")
    return send_file(graph_path)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from qa_system import CyberSecurityQASystem
import os
import sys

app = Flask(__name__, static_folder='../frontend/dist')
CORS(app)

qa_system = None
is_initialized = False

@app.route('/')
def index():
    print("访问首页")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    print("收到健康检查请求")
    return jsonify({
        'status': 'ok',
        'initialized': is_initialized
    })

@app.route('/api/init', methods=['POST'])
def initialize_system():
    global qa_system, is_initialized
    
    print("=" * 60)
    print("收到初始化系统请求")
    print("=" * 60)
    sys.stdout.flush()
    
    try:
        data = request.get_json()
        force_rebuild = data.get('force_rebuild', False)
        print(f"force_rebuild参数: {force_rebuild}")
        sys.stdout.flush()
        
        if qa_system is None:
            print("创建新的CyberSecurityQASystem实例")
            sys.stdout.flush()
            qa_system = CyberSecurityQASystem()
        
        print("开始调用qa_system.initialize()")
        sys.stdout.flush()
        qa_system.initialize(force_rebuild=force_rebuild)
        is_initialized = True
        
        status = qa_system.get_status()
        
        print("系统初始化成功")
        print("=" * 60 + "\n")
        sys.stdout.flush()
        
        return jsonify({
            'success': True,
            'message': '系统初始化成功',
            'status': status
        })
    
    except Exception as e:
        print(f"系统初始化失败: {str(e)}")
        print("=" * 60 + "\n")
        sys.stdout.flush()
        return jsonify({
            'success': False,
            'error': str(e),
            'is_initialized': False
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    global qa_system, is_initialized
    
    print("\n" + "=" * 60)
    print("收到文档上传请求")
    print("=" * 60)
    sys.stdout.flush()
    
    if 'file' not in request.files:
        print("没有文件上传")
        sys.stdout.flush()
        return jsonify({
            'success': False,
            'error': '没有找到文件'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("文件名为空")
        sys.stdout.flush()
        return jsonify({
            'success': False,
            'error': '文件名不能为空'
        }), 400
    
    try:
        from werkzeug.utils import secure_filename
        
        documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')
        os.makedirs(documents_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(documents_dir, filename)
        
        print(f"正在保存文件: {file_path}")
        file.save(file_path)
        print(f"文件保存成功")
        sys.stdout.flush()
        
        if not is_initialized or qa_system is None:
            print("系统未初始化，需要先初始化")
            sys.stdout.flush()
            return jsonify({
                'success': False,
                'error': '系统未初始化，请先初始化系统',
                'file_saved': True,
                'file_path': file_path
            }), 400
        
        result = qa_system.add_documents(file_path=file_path)
        
        print("文档添加完成")
        print("=" * 60 + "\n")
        sys.stdout.flush()
        
        return jsonify(result)
    
    except Exception as e:
        print(f"上传文档失败: {str(e)}")
        print("=" * 60 + "\n")
        sys.stdout.flush()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/add-documents', methods=['POST'])
def add_documents():
    global qa_system, is_initialized
    
    print("\n" + "=" * 60)
    print("收到添加文档请求")
    print("=" * 60)
    
    if not is_initialized or qa_system is None:
        print("系统未初始化")
        return jsonify({
            'success': False,
            'error': '系统未初始化'
        }), 400
    
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        directory = data.get('directory')
        print(f"文件路径: {file_path}, 目录: {directory}")
        
        result = qa_system.add_documents(
            file_path=file_path,
            directory=directory
        )
        
        print("文档添加成功")
        print("=" * 60 + "\n")
        return jsonify(result)
    
    except Exception as e:
        print(f"添加文档失败: {str(e)}")
        print("=" * 60 + "\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/query', methods=['POST'])
def query():
    global qa_system, is_initialized
    
    print("\n" + "=" * 60)
    print("收到查询请求")
    print("=" * 60)
    
    if not is_initialized or qa_system is None:
        print("系统未初始化")
        return jsonify({
            'success': False,
            'error': '系统未初始化'
        }), 400
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        include_sources = data.get('include_sources', True)
        use_web_search = data.get('use_web_search', True)
        
        print(f"用户问题: {question}")
        print(f"包含来源: {include_sources}")
        print(f"使用网络搜索: {use_web_search}")
        
        result = qa_system.query(question, include_sources=include_sources, use_web_search=use_web_search)
        
        print("查询完成")
        print("=" * 60 + "\n")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"查询失败: {str(e)}")
        print("=" * 60 + "\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    global qa_system, is_initialized
    
    print("\n" + "=" * 60)
    print("收到状态查询请求")
    print("=" * 60)
    
    try:
        if not is_initialized or qa_system is None:
            print("系统未初始化")
            return jsonify({
                'is_initialized': False,
                'status': {
                    'vector_store': {
                        'document_count': 0,
                        'status': '未初始化'
                    },
                    'tools': []
                }
            })
        
        status = qa_system.get_status()
        print(f"系统状态: {status}")
        print("=" * 60 + "\n")
        
        return jsonify({
            'is_initialized': True,
            'status': status
        })
    
    except Exception as e:
        print(f"获取状态失败: {str(e)}")
        return jsonify({
            'is_initialized': False,
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global qa_system, is_initialized
    
    print("\n" + "=" * 60)
    print("收到重置系统请求")
    print("=" * 60)
    
    try:
        if qa_system:
            print("重置QA系统")
            qa_system.reset_system()
        
        qa_system = None
        is_initialized = False
        
        print("系统重置成功")
        print("=" * 60 + "\n")
        return jsonify({
            'success': True,
            'message': '系统已重置'
        })
    
    except Exception as e:
        print(f"重置系统失败: {str(e)}")
        print("=" * 60 + "\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"启动Flask服务器，端口: {port}")
    print(f"调试模式: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)

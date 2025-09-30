#!/usr/bin/env python3
import os
import tempfile
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from api_client import ZhipuAIClient
from table_parser import TableParser
from config import Config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', methods=['OPTIONS'])
def options():
    return '', 200

@app.route('/upload', methods=['OPTIONS'])
def upload_options():
    return '', 200

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和图片粘贴"""
    try:
        # 检查是否有文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '未选择文件'}), 400
            
            if file and allowed_file(file.filename):
                # 保存上传的文件
                filename = secure_filename(file.filename)
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, filename)
                file.save(filepath)
                
                return process_image(filepath)
        
        # 检查是否有base64图片数据
        elif request.json and 'image_data' in request.json:
            image_data = request.json['image_data']
            if image_data and image_data.startswith('data:image'):
                # 提取base64数据
                import base64
                try:
                    header, encoded = image_data.split(',', 1)
                    image_bytes = base64.b64decode(encoded)
                    
                    # 保存临时文件
                    temp_dir = tempfile.gettempdir()
                    filepath = os.path.join(temp_dir, 'pasted_image.png')
                    with open(filepath, 'wb') as f:
                        f.write(image_bytes)
                    
                    return process_image(filepath)
                except Exception as e:
                    return jsonify({'error': f'图片数据解析失败: {str(e)}'}), 400
        
        return jsonify({'error': '无效的请求'}), 400
        
    except Exception as e:
        error_msg = str(e)
        print(f"上传处理失败: {error_msg}")
        
        # 提供详细的错误信息
        if "未选择文件" in error_msg:
            return jsonify({
                'error': '未选择文件',
                'solution': '请选择要上传的图片文件'
            }), 400
        elif "图片数据解析失败" in error_msg:
            return jsonify({
                'error': '图片数据解析失败',
                'solution': '请确保粘贴的是有效的图片数据'
            }), 400
        else:
            return jsonify({
                'error': f'处理失败: {error_msg}',
                'solution': '请检查文件格式和大小，或联系技术支持'
            }), 500

def process_image(image_path):
    """处理图片识别"""
    try:
        # 初始化客户端和解析器
        client = ZhipuAIClient()
        parser = TableParser()
        
        # 调用API识别表格
        response = client.recognize_table(image_path)
        table_data = client.extract_table_data(response)
        
        if not table_data:
            return jsonify({
                'error': '未能识别到表格数据',
                'solution': '请尝试上传更清晰的表格图片，确保图片中的表格完整可见'
            }), 400
        
        # 创建数据框并直接返回数组格式数据
        df = parser.create_dataframe(table_data)
        
        # 将DataFrame转换回数组格式（包含表头）
        table_array = [list(df.columns)] + df.values.tolist()
        
        # 清理临时文件
        os.unlink(image_path)
        
        return jsonify({
            'success': True,
            'table_data': table_array,
            'headers': list(df.columns),
            'row_count': len(df),
            'col_count': len(df.columns)
        })
        
    except Exception as e:
        # 确保清理临时文件
        if os.path.exists(image_path):
            os.unlink(image_path)
        
        # 解析错误信息，提取错误原因和解决方案
        error_msg = str(e)
        error_parts = error_msg.split(' | 解决方案: ')
        
        if len(error_parts) == 2:
            # 错误信息已经包含解决方案
            error_reason = error_parts[0]
            solution = error_parts[1]
        else:
            # 通用错误处理
            error_reason = error_msg
            if "API" in error_msg or "密钥" in error_msg:
                solution = "请检查config.py中的ZHIPU_API_KEY配置，确保API密钥有效"
            elif "网络" in error_msg or "连接" in error_msg or "超时" in error_msg:
                solution = "请检查网络连接，或尝试稍后重试"
            elif "图片" in error_msg or "文件" in error_msg:
                solution = "请检查图片格式和大小，支持PNG、JPG、BMP、TIFF、WebP格式"
            else:
                solution = "请检查应用程序日志获取更多详细信息，或联系技术支持"
        
        # 记录详细错误信息到控制台
        print(f"处理图片时发生错误: {error_reason}")
        print(f"建议解决方案: {solution}")
        
        return jsonify({
            'error': error_reason,
            'solution': solution,
            'error_type': 'api_error' if 'API' in error_reason else 'processing_error'
        }), 500

if __name__ == '__main__':
    # 验证配置
    if not Config.validate_config():
        print("配置验证失败，请检查API密钥设置")
        exit(1)
    
    # 添加Broken pipe错误处理
    from werkzeug.serving import WSGIRequestHandler
    
    class CustomRequestHandler(WSGIRequestHandler):
        def handle(self):
            try:
                super().handle()
            except (BrokenPipeError, ConnectionResetError):
                # 忽略Broken pipe错误，这是客户端断开连接的正常情况
                pass
    
    app.run(debug=True, host='0.0.0.0', port=5000, request_handler=CustomRequestHandler, threaded=True)
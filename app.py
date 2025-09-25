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
        elif 'image_data' in request.json:
            image_data = request.json['image_data']
            if image_data.startswith('data:image'):
                # 提取base64数据
                import base64
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
                
                # 保存临时文件
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, 'pasted_image.png')
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                return process_image(filepath)
        
        return jsonify({'error': '无效的请求'}), 400
        
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

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
            return jsonify({'error': '未能识别到表格数据'}), 400
        
        # 创建数据框并转换为字典
        df = parser.create_dataframe(table_data)
        table_dict = df.to_dict('records')
        
        # 清理临时文件
        os.unlink(image_path)
        
        return jsonify({
            'success': True,
            'table_data': table_dict,
            'headers': list(df.columns),
            'row_count': len(df),
            'col_count': len(df.columns)
        })
        
    except Exception as e:
        # 确保清理临时文件
        if os.path.exists(image_path):
            os.unlink(image_path)
        return jsonify({'error': f'识别失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 验证配置
    if not Config.validate_config():
        print("配置验证失败，请检查API密钥设置")
        exit(1)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
# 表格识别工具

使用智谱AI GLM-4V模型识别图片中的表格，并转换为结构化数据。

## 功能特性

- 支持多种图片格式（PNG、JPG、BMP等）
- 调用智谱AI GLM-4V模型进行表格识别
- 支持多种输出格式（CSV、Excel、JSON）
- 简单的命令行界面
- 表格数据预览功能

## 环境要求

- Python 3.11+
- 智谱AI API密钥

## 安装步骤

1. 激活虚拟环境：
```bash
source venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置API密钥：
```bash
export ZHIPU_API_KEY=your_api_key_here
```

## 使用方法

### Web UI界面（推荐）
```bash
python app.py
```
然后在浏览器中打开 http://localhost:5000

### 命令行界面
```bash
python main.py 图片路径
```

### 指定输出格式
```bash
python main.py 图片路径 -f excel      # 输出为Excel格式
python main.py 图片路径 -f json       # 输出为JSON格式
python main.py 图片路径 -f csv        # 输出为CSV格式（默认）
```

### 指定输出路径
```bash
python main.py 图片路径 -o 输出路径
```

### 预览结果（不保存）
```bash
python main.py 图片路径 --preview
```

### 完整示例
```bash
python main.py screenshot.png -f excel -o result.xlsx --preview
```

## 支持的图片格式

- PNG (.png)
- JPEG (.jpg, .jpeg) 
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## 输出格式说明

- **CSV**: 逗号分隔值文件，适合Excel和数据分析工具
- **Excel**: Microsoft Excel格式，保持表格格式
- **JSON**: JavaScript对象表示法，适合程序处理

## 注意事项

1. 确保已设置正确的API密钥环境变量
2. 图片文件大小建议不超过10MB
3. 表格识别效果取决于图片质量和表格复杂度
4. 程序会自动重试失败的API请求（最多3次）
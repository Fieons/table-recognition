#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

from config import Config
from api_client import ZhipuAIClient
from table_parser import TableParser


def validate_image_file(image_path: str) -> bool:
    """验证图片文件"""
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在 - {image_path}")
        return False
    
    if not os.path.isfile(image_path):
        print(f"错误: 路径不是文件 - {image_path}")
        return False
    
    # 检查文件扩展名
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    file_ext = Path(image_path).suffix.lower()
    
    if file_ext not in valid_extensions:
        print(f"错误: 不支持的文件格式 - {file_ext}")
        print(f"支持的格式: {', '.join(valid_extensions)}")
        return False
    
    return True


def get_output_path(input_path: str, output_format: str) -> str:
    """生成输出文件路径"""
    input_path_obj = Path(input_path)
    
    if output_format == "csv":
        ext = ".csv"
    elif output_format == "excel":
        ext = ".xlsx"
    elif output_format == "json":
        ext = ".json"
    else:
        ext = ".txt"
    
    return str(input_path_obj.with_suffix(ext))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='表格识别工具 - 使用智谱AI GLM-4V模型')
    parser.add_argument('image_path', help='图片文件路径')
    parser.add_argument('-f', '--format', choices=Config.SUPPORTED_FORMATS, 
                       default=Config.DEFAULT_OUTPUT_FORMAT, 
                       help='输出格式 (默认: csv)')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('--preview', action='store_true', 
                       help='预览识别结果而不保存')
    
    args = parser.parse_args()
    
    # 验证配置
    if not Config.validate_config():
        sys.exit(1)
    
    # 验证图片文件
    if not validate_image_file(args.image_path):
        sys.exit(1)
    
    # 生成输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = get_output_path(args.image_path, args.format)
    
    try:
        # 初始化客户端和解析器
        client = ZhipuAIClient()
        parser = TableParser()
        
        print("开始识别表格...")
        
        # 调用API识别表格
        response = client.recognize_table(args.image_path)
        
        # 提取表格数据
        table_data = client.extract_table_data(response)
        
        if not table_data:
            print("未能成功提取表格数据")
            sys.exit(1)
        
        print(f"成功识别表格，共 {len(table_data)} 行数据")
        
        # 预览或保存结果
        if args.preview:
            parser.preview_table(table_data)
        else:
            success = parser.export_table(table_data, output_path, args.format)
            if success:
                print(f"表格数据已保存到: {output_path}")
            else:
                print("保存表格数据失败")
                sys.exit(1)
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
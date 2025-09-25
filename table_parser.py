import pandas as pd
import json
from typing import List, Dict, Any, Optional


class TableParser:
    """表格数据解析器"""
    
    def __init__(self):
        self.supported_formats = ["csv", "excel", "json"]
    
    def create_dataframe(self, table_data: List[List[str]]) -> pd.DataFrame:
        """将表格数据转换为pandas DataFrame"""
        if not table_data:
            raise ValueError("表格数据为空")
        
        # 第一行作为表头
        headers = table_data[0]
        data_rows = table_data[1:] if len(table_data) > 1 else []
        
        return pd.DataFrame(data_rows, columns=headers)
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str) -> bool:
        """保存为CSV文件"""
        try:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return False
    
    def save_to_excel(self, df: pd.DataFrame, output_path: str) -> bool:
        """保存为Excel文件"""
        try:
            df.to_excel(output_path, index=False, engine='openpyxl')
            return True
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            return False
    
    def save_to_json(self, df: pd.DataFrame, output_path: str) -> bool:
        """保存为JSON文件"""
        try:
            # 转换为字典格式
            data_dict = df.to_dict('records')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return False
    
    def export_table(self, table_data: List[List[str]], output_path: str, 
                    format_type: str = "csv") -> bool:
        """导出表格数据到指定格式"""
        
        if format_type not in self.supported_formats:
            print(f"不支持的格式: {format_type}")
            print(f"支持的格式: {', '.join(self.supported_formats)}")
            return False
        
        try:
            df = self.create_dataframe(table_data)
            
            if format_type == "csv":
                return self.save_to_csv(df, output_path)
            elif format_type == "excel":
                return self.save_to_excel(df, output_path)
            elif format_type == "json":
                return self.save_to_json(df, output_path)
            
        except Exception as e:
            print(f"导出表格数据失败: {e}")
            return False
        
        return False
    
    def preview_table(self, table_data: List[List[str]]) -> None:
        """预览表格数据"""
        if not table_data:
            print("表格数据为空")
            return
        
        try:
            df = self.create_dataframe(table_data)
            print("\n表格预览:")
            print("=" * 50)
            print(df)
            print("=" * 50)
            print(f"表格尺寸: {len(df)} 行 × {len(df.columns)} 列")
        except Exception as e:
            print(f"预览表格失败: {e}")
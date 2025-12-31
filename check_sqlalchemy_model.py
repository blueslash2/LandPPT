#!/usr/bin/env python3
"""
SQLAlchemy模型与数据库表结构兼容性检查
验证模型定义是否支持自增，并提供修复建议
"""

import sys
import os
import time
import inspect
from typing import Dict, List, Optional, Any

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.ext.declarative import declarative_base
from landppt.database.models import User, UserSession
from landppt.database.database import engine
from landppt.core.config import app_config

class SQLAlchemyModelChecker:
    """SQLAlchemy模型检查器"""
    
    def __init__(self):
        self.inspector = sqlalchemy_inspect(engine)
        self.base = declarative_base()
        
    def get_model_columns(self, model_class) -> Dict[str, Any]:
        """获取模型列定义"""
        columns = {}
        for attr_name in dir(model_class):
            attr = getattr(model_class, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'columns'):
                column = attr.property.columns[0]
                columns[attr_name] = {
                    'name': column.name,
                    'type': str(column.type),
                    'primary_key': column.primary_key,
                    'nullable': column.nullable,
                    'autoincrement': getattr(column, 'autoincrement', None),
                    'default': column.default
                }
        return columns
    
    def get_table_columns(self, table_name: str) -> Dict[str, Dict]:
        """获取数据库表列信息"""
        columns = {}
        try:
            table_columns = self.inspector.get_columns(table_name)
            for col in table_columns:
                columns[col['name']] = {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': col['default'],
                    'primary_key': col.get('primary_key', False),
                    'autoincrement': col.get('autoincrement', False)
                }
            return columns
        except Exception as e:
            print(f"获取表 {table_name} 列信息失败: {e}")
            return {}
    
    def check_model_autoincrement_support(self, model_class) -> Dict[str, Any]:
        """检查模型自增支持情况"""
        result = {
            'model_name': model_class.__name__,
            'has_autoincrement': False,
            'primary_key_column': None,
            'pk_autoincrement': False,
            'issues': [],
            'recommendations': []
        }
        
        columns = self.get_model_columns(model_class)
        
        # 查找主键列
        pk_columns = [col for col in columns.values() if col['primary_key']]
        
        if not pk_columns:
            result['issues'].append("模型没有定义主键")
            result['recommendations'].append("添加主键列")
        elif len(pk_columns) > 1:
            result['issues'].append("模型有多个主键列")
            result['recommendations'].append("考虑使用复合主键或单一主键")
        else:
            pk_col = pk_columns[0]
            result['primary_key_column'] = pk_col['name']
            result['pk_autoincrement'] = pk_col['autoincrement'] or False
            
            # 检查主键类型
            if 'INTEGER' in pk_col['type'].upper() or 'INT' in pk_col['type'].upper():
                if pk_col['autoincrement'] is None:
                    # SQLAlchemy默认行为：INTEGER PRIMARY KEY 默认自增
                    result['has_autoincrement'] = True
                    result['recommendations'].append("SQLAlchemy会自动为INTEGER主键启用自增")
                elif pk_col['autoincrement'] is True:
                    result['has_autoincrement'] = True
                else:
                    result['has_autoincrement'] = False
                    result['issues'].append("主键列显式禁用了自增")
                    result['recommendations'].append("考虑启用autoincrement=True")
            else:
                result['issues'].append(f"主键列类型不是INTEGER: {pk_col['type']}")
                result['recommendations'].append("主键列应为INTEGER类型以支持自增")
        
        return result
    
    def compare_model_with_table(self, model_class, table_name: str) -> Dict[str, Any]:
        """比较模型定义与数据库表结构"""
        result = {
            'model_name': model_class.__name__,
            'table_name': table_name,
            'mismatches': [],
            'missing_in_model': [],
            'missing_in_table': [],
            'autoincrement_mismatch': False
        }
        
        model_columns = self.get_model_columns(model_class)
        table_columns = self.get_table_columns(table_name)
        
        # 检查模型中的列在表中是否存在
        for col_name, model_col in model_columns.items():
            if col_name not in table_columns:
                result['missing_in_table'].append({
                    'column': col_name,
                    'type': model_col['type'],
                    'details': f"模型中的列 {col_name} 在数据库表中不存在"
                })
            else:
                table_col = table_columns[col_name]
                # 检查类型匹配
                if model_col['type'] != table_col['type']:
                    result['mismatches'].append({
                        'column': col_name,
                        'model_type': model_col['type'],
                        'table_type': table_col['type'],
                        'issue': '类型不匹配'
                    })
                
                # 检查主键匹配
                if model_col['primary_key'] != table_col['primary_key']:
                    result['mismatches'].append({
                        'column': col_name,
                        'model_pk': model_col['primary_key'],
                        'table_pk': table_col['primary_key'],
                        'issue': '主键约束不匹配'
                    })
                
                # 检查自增匹配
                if model_col.get('autoincrement') != table_col.get('autoincrement'):
                    result['autoincrement_mismatch'] = True
                    result['mismatches'].append({
                        'column': col_name,
                        'model_autoincrement': model_col.get('autoincrement'),
                        'table_autoincrement': table_col.get('autoincrement'),
                        'issue': '自增设置不匹配'
                    })
        
        # 检查表中的列在模型中是否存在
        for col_name, table_col in table_columns.items():
            if col_name not in model_columns:
                result['missing_in_model'].append({
                    'column': col_name,
                    'type': table_col['type'],
                    'details': f"数据库表中的列 {col_name} 在模型中未定义"
                })
        
        return result
    
    def generate_model_fix_suggestions(self, model_class) -> List[str]:
        """生成模型修复建议"""
        suggestions = []
        
        # 检查自增支持
        autoincrement_check = self.check_model_autoincrement_support(model_class)
        
        if autoincrement_check['issues']:
            suggestions.append(f"-- {model_class.__name__} 模型问题修复建议:")
            for issue in autoincrement_check['issues']:
                suggestions.append(f"-- 问题: {issue}")
            for rec in autoincrement_check['recommendations']:
                suggestions.append(f"-- 建议: {rec}")
            suggestions.append("")
        
        # 检查主键列定义
        if autoincrement_check['primary_key_column'] == 'id':
            suggestions.append("-- 推荐的主键列定义:")
            suggestions.append("from sqlalchemy import Column, Integer, String")
            suggestions.append("from sqlalchemy.orm import Mapped, mapped_column")
            suggestions.append("")
            suggestions.append("# 选项1: 使用mapped_column（SQLAlchemy 2.0风格）")
            suggestions.append("id: Mapped[int] = mapped_column(Integer, primary_key=True)")
            suggestions.append("")
            suggestions.append("# 选项2: 使用Column（传统风格）")
            suggestions.append("id = Column(Integer, primary_key=True, autoincrement=True)")
            suggestions.append("")
            suggestions.append("# 选项3: 严格自增（不重用删除的ID）")
            suggestions.append("id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)")
        
        return suggestions
    
    def check_database_compatibility(self) -> Dict[str, Any]:
        """全面检查数据库兼容性"""
        results = {
            'database_url': str(app_config.database_url),
            'table_checks': {},
            'overall_status': 'unknown',
            'critical_issues': [],
            'warnings': []
        }
        
        # 检查用户表
        try:
            user_check = self.compare_model_with_table(User, 'users')
            user_autoincrement = self.check_model_autoincrement_support(User)
            
            results['table_checks']['users'] = {
                'model_table_comparison': user_check,
                'autoincrement_support': user_autoincrement
            }
            
            # 分析关键问题
            if user_autoincrement['primary_key_column'] == 'id':
                if not user_autoincrement['has_autoincrement']:
                    results['critical_issues'].append("用户表主键不支持自增，可能导致注册冲突")
            
            if user_check['autoincrement_mismatch']:
                results['warnings'].append("模型与数据库的自增设置不匹配")
            
        except Exception as e:
            results['table_checks']['users'] = {'error': str(e)}
            results['critical_issues'].append(f"用户表检查失败: {e}")
        
        # 检查会话表
        try:
            session_check = self.compare_model_with_table(UserSession, 'user_sessions')
            session_autoincrement = self.check_model_autoincrement_support(UserSession)
            
            results['table_checks']['user_sessions'] = {
                'model_table_comparison': session_check,
                'autoincrement_support': session_autoincrement
            }
        except Exception as e:
            results['table_checks']['user_sessions'] = {'error': str(e)}
        
        # 总体状态评估
        if results['critical_issues']:
            results['overall_status'] = 'critical'
        elif results['warnings']:
            results['overall_status'] = 'warning'
        else:
            results['overall_status'] = 'ok'
        
        return results

def main():
    """主函数"""
    print("=" * 70)
    print("SQLAlchemy模型与数据库兼容性检查工具")
    print("=" * 70)
    print(f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库URL: {app_config.database_url}")
    
    checker = SQLAlchemyModelChecker()
    
    try:
        # 全面兼容性检查
        print("\n" + "=" * 50)
        print("执行全面兼容性检查...")
        compatibility_results = checker.check_database_compatibility()
        
        print(f"\n总体状态: {compatibility_results['overall_status']}")
        
        if compatibility_results['critical_issues']:
            print("\n❌ 关键问题:")
            for issue in compatibility_results['critical_issues']:
                print(f"  - {issue}")
        
        if compatibility_results['warnings']:
            print("\n⚠ 警告:")
            for warning in compatibility_results['warnings']:
                print(f"  - {warning}")
        
        # 详细检查用户表
        print("\n" + "=" * 50)
        print("详细检查用户表 (User模型)")
        print("=" * 50)
        
        user_results = compatibility_results['table_checks']['users']
        if 'error' not in user_results:
            autoincrement_info = user_results['autoincrement_support']
            comparison_info = user_results['model_table_comparison']
            
            print("模型自增支持情况:")
            print(f"  模型名称: {autoincrement_info['model_name']}")
            print(f"  主键列: {autoincrement_info['primary_key_column']}")
            print(f"  支持自增: {'✓' if autoincrement_info['has_autoincrement'] else '✗'}")
            print(f"  主键自增: {'✓' if autoincrement_info['pk_autoincrement'] else '✗'}")
            
            if autoincrement_info['issues']:
                print("  问题:")
                for issue in autoincrement_info['issues']:
                    print(f"    - {issue}")
            
            if autoincrement_info['recommendations']:
                print("  建议:")
                for rec in autoincrement_info['recommendations']:
                    print(f"    - {rec}")
            
            print(f"\n模型与表结构对比:")
            if comparison_info['mismatches']:
                print("  不匹配项:")
                for mismatch in comparison_info['mismatches']:
                    print(f"    - {mismatch['column']}: {mismatch['issue']}")
            
            if comparison_info['autoincrement_mismatch']:
                print("  ⚠ 自增设置不匹配")
            
            # 生成修复建议
            print(f"\n修复建议:")
            suggestions = checker.generate_model_fix_suggestions(User)
            for suggestion in suggestions:
                print(suggestion)
        
        # 生成综合修复方案
        print(f"\n" + "=" * 50)
        print("综合修复方案")
        print("=" * 50)
        
        if compatibility_results['overall_status'] in ['critical', 'warning']:
            print("推荐修复步骤:")
            print("1. 备份数据库")
            print("2. 根据生成的SQL文件修复表结构")
            print("3. 更新模型定义（如果需要）")
            print("4. 测试注册功能")
            
            # 生成修复SQL文件
            sql_content = []
            sql_content.append("-- 数据库表结构修复SQL")
            sql_content.append(f"-- 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            sql_content.append("")
            
            if 'users' in compatibility_results['table_checks'] and 'error' not in compatibility_results['table_checks']['users']:
                user_auto = compatibility_results['table_checks']['users']['autoincrement_support']
                if not user_auto['has_autoincrement'] and user_auto['primary_key_column'] == 'id':
                    sql_content.append("-- 修复用户表主键自增")
                    sql_content.append("-- 注意：这需要重新创建表并迁移数据")
                    sql_content.append("")
                    sql_content.append("-- 步骤1: 备份数据")
                    sql_content.append("CREATE TABLE users_backup AS SELECT * FROM users;")
                    sql_content.append("")
                    sql_content.append("-- 步骤2: 删除原表")
                    sql_content.append("DROP TABLE users;")
                    sql_content.append("")
                    sql_content.append("-- 步骤3: 创建新表（带自增主键）")
                    sql_content.append("CREATE TABLE users (")
                    sql_content.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
                    sql_content.append("    username VARCHAR(50) UNIQUE NOT NULL,")
                    sql_content.append("    password_hash VARCHAR(128) NOT NULL,")
                    sql_content.append("    email VARCHAR(100) UNIQUE,")
                    sql_content.append("    is_active BOOLEAN DEFAULT 1,")
                    sql_content.append("    is_admin BOOLEAN DEFAULT 0,")
                    sql_content.append("    created_at FLOAT,")
                    sql_content.append("    last_login FLOAT")
                    sql_content.append(");")
                    sql_content.append("")
                    sql_content.append("-- 步骤4: 恢复数据（不恢复ID，让数据库重新生成）")
                    sql_content.append("INSERT INTO users (username, password_hash, email, is_active, is_admin, created_at, last_login)")
                    sql_content.append("SELECT username, password_hash, email, is_active, is_admin, created_at, last_login FROM users_backup;")
                    sql_content.append("")
                    sql_content.append("-- 步骤5: 删除备份")
                    sql_content.append("DROP TABLE users_backup;")
                    sql_content.append("")
                    sql_content.append("-- 步骤6: 验证结果")
                    sql_content.append("SELECT COUNT(*) as user_count FROM users;")
                    sql_content.append("SELECT MAX(id) as max_id FROM users;")
            
            # 保存SQL文件
            sql_file = f"fix_database_structure_{int(time.time())}.sql"
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sql_content))
            
            print(f"\n修复SQL已保存到: {sql_file}")
            print("请在数据库管理工具中执行此SQL文件")
        else:
            print("✓ 数据库兼容性良好，无需修复")
        
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
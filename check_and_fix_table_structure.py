#!/usr/bin/env python3
"""
数据库表结构检查和修复建议脚本
用于检查和修复用户表的自增主键问题
"""

import sqlite3
import os
import sys
import time
from typing import Dict, List, Tuple, Optional

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from landppt.core.config import app_config

class DatabaseTableChecker:
    """数据库表结构检查器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def get_table_info(self, table_name: str) -> List[Dict]:
        """获取表结构信息"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            table_info = []
            for col in columns:
                table_info.append({
                    'cid': col[0],           # 列ID
                    'name': col[1],          # 列名
                    'type': col[2],          # 数据类型
                    'notnull': col[3],       # 是否非空
                    'default_value': col[4], # 默认值
                    'pk': col[5]             # 是否主键
                })
            return table_info
        except Exception as e:
            print(f"获取表结构失败: {e}")
            return []
    
    def check_primary_key(self, table_name: str) -> Optional[Dict]:
        """检查主键设置"""
        table_info = self.get_table_info(table_name)
        
        for col in table_info:
            if col['pk'] == 1:  # 是主键
                return col
        return None
    
    def check_autoincrement(self, table_name: str) -> bool:
        """检查是否支持自增"""
        try:
            # 检查表的SQL定义
            self.cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = self.cursor.fetchone()
            
            if result and result[0]:
                create_sql = result[0].upper()
                # 检查是否包含AUTOINCREMENT
                has_autoincrement = 'AUTOINCREMENT' in create_sql
                # 检查主键列是否为INTEGER类型
                has_integer_pk = 'INTEGER PRIMARY KEY' in create_sql
                return has_autoincrement or has_integer_pk
            return False
        except Exception as e:
            print(f"检查自增失败: {e}")
            return False
    
    def get_table_indexes(self, table_name: str) -> List[Dict]:
        """获取表索引信息"""
        try:
            self.cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = self.cursor.fetchall()
            
            index_info = []
            for idx in indexes:
                index_name = idx[1]
                is_unique = idx[2] == 1
                
                # 获取索引列信息
                self.cursor.execute(f"PRAGMA index_info({index_name})")
                columns = self.cursor.fetchall()
                
                index_info.append({
                    'name': index_name,
                    'unique': is_unique,
                    'columns': [col[2] for col in columns]
                })
            return index_info
        except Exception as e:
            print(f"获取索引信息失败: {e}")
            return []
    
    def test_insert_without_id(self, table_name: str) -> Tuple[bool, Optional[int]]:
        """测试不指定ID的插入"""
        try:
            # 获取表结构
            table_info = self.get_table_info(table_name)
            column_names = [col['name'] for col in table_info if col['name'] != 'id']
            
            # 构建测试插入语句
            columns_str = ', '.join(column_names)
            placeholders = ', '.join(['?' for _ in column_names])
            
            test_values = []
            for col in table_info:
                if col['name'] == 'id':
                    continue
                elif col['name'] == 'username':
                    test_values.append(f"test_user_{int(time.time())}")
                elif col['name'] == 'password_hash':
                    test_values.append("test_hash")
                elif col['name'] == 'email':
                    test_values.append(f"test_{int(time.time())}@example.com")
                elif col['name'] == 'is_active':
                    test_values.append(1)
                elif col['name'] == 'is_admin':
                    test_values.append(0)
                elif col['name'] == 'created_at':
                    test_values.append(time.time())
                elif col['name'] == 'last_login':
                    test_values.append(None)
                else:
                    test_values.append(None)
            
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(sql, test_values)
            
            new_id = self.cursor.lastrowid
            self.conn.commit()
            
            # 清理测试数据
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (new_id,))
            self.conn.commit()
            
            return True, new_id
            
        except Exception as e:
            self.conn.rollback()
            return False, None
    
    def generate_fix_sql(self, table_name: str) -> List[str]:
        """生成修复SQL语句"""
        sql_statements = []
        
        # 获取当前表结构
        table_info = self.get_table_info(table_name)
        
        # 检查主键
        pk_col = self.check_primary_key(table_name)
        
        if not pk_col:
            print(f"⚠ 表 {table_name} 没有主键，建议添加")
            
            # 查找id列
            id_col = next((col for col in table_info if col['name'] == 'id'), None)
            
            if id_col:
                # 生成添加主键的SQL
                sql_statements.append(f"-- 为 {table_name} 表的 id 列添加主键约束")
                sql_statements.append(f"-- 注意：这需要重新创建表")
                sql_statements.append("")
                sql_statements.append("-- 方案：创建新表并迁移数据")
                sql_statements.append(self.generate_table_recreation_sql(table_name, add_autoincrement=True))
            else:
                print(f"❌ 表 {table_name} 没有 id 列，无法添加自增主键")
        
        elif pk_col['name'] == 'id' and pk_col['type'].upper() == 'INTEGER':
            # 检查是否支持自增
            if not self.check_autoincrement(table_name):
                print(f"⚠ 表 {table_name} 的 id 列是主键但不支持自增")
                sql_statements.append(f"-- 为 {table_name} 表的 id 列启用自增")
                sql_statements.append(f"-- 当前主键：{pk_col['name']} ({pk_col['type']})")
                sql_statements.append("")
                sql_statements.append("-- 方案：重新创建表并迁移数据")
                sql_statements.append(self.generate_table_recreation_sql(table_name, add_autoincrement=True))
        
        else:
            print(f"✓ 表 {table_name} 已有合适的主键：{pk_col['name']} ({pk_col['type']})")
        
        return sql_statements
    
    def generate_table_recreation_sql(self, table_name: str, add_autoincrement: bool = True) -> str:
        """生成重新创建表的SQL"""
        table_info = self.get_table_info(table_name)
        
        # 构建列定义
        column_defs = []
        for col in table_info:
            if col['name'] == 'id' and add_autoincrement:
                # id列改为自增主键
                column_defs.append(f"{col['name']} INTEGER PRIMARY KEY AUTOINCREMENT")
            elif col['pk'] == 1:
                # 其他主键列
                column_defs.append(f"{col['name']} {col['type']} PRIMARY KEY")
            else:
                # 普通列
                nullable = "NOT NULL" if col['notnull'] else ""
                default = f"DEFAULT {col['default_value']}" if col['default_value'] else ""
                column_defs.append(f"{col['name']} {col['type']} {nullable} {default}".strip())
        
        # 获取索引信息
        indexes = self.get_table_indexes(table_name)
        
        sql_parts = []
        sql_parts.append("-- 1. 备份现有数据")
        sql_parts.append(f"CREATE TABLE {table_name}_backup AS SELECT * FROM {table_name};")
        sql_parts.append("")
        sql_parts.append("-- 2. 删除原表")
        sql_parts.append(f"DROP TABLE {table_name};")
        sql_parts.append("")
        sql_parts.append("-- 3. 创建新表（带自增主键）")
        sql_parts.append(f"CREATE TABLE {table_name} (")
        sql_parts.append(",\n".join(f"    {def_}" for def_ in column_defs))
        sql_parts.append(");")
        sql_parts.append("")
        
        # 添加索引重建
        for idx in indexes:
            if 'sqlite_autoindex' not in idx['name']:  # 跳过SQLite自动索引
                unique = "UNIQUE " if idx['unique'] else ""
                columns = ", ".join(idx['columns'])
                sql_parts.append(f"CREATE {unique}INDEX {idx['name']} ON {table_name} ({columns});")
        
        sql_parts.append("")
        sql_parts.append("-- 4. 恢复数据（不恢复ID，让数据库重新生成）")
        other_columns = [col['name'] for col in table_info if col['name'] != 'id']
        if other_columns:
            columns_str = ", ".join(other_columns)
            sql_parts.append(f"INSERT INTO {table_name} ({columns_str})")
            sql_parts.append(f"SELECT {columns_str} FROM {table_name}_backup;")
        sql_parts.append("")
        sql_parts.append("-- 5. 删除备份表")
        sql_parts.append(f"DROP TABLE {table_name}_backup;")
        sql_parts.append("")
        sql_parts.append("-- 6. 验证数据")
        sql_parts.append(f"SELECT COUNT(*) as total_records FROM {table_name};")
        sql_parts.append(f"SELECT MAX(id) as max_id FROM {table_name};")
        
        return "\n".join(sql_parts)
    
    def check_table_constraints(self, table_name: str) -> Dict[str, bool]:
        """检查表约束"""
        constraints = {
            'has_primary_key': False,
            'has_unique_username': False,
            'has_unique_email': False,
            'supports_autoincrement': False
        }
        
        # 检查主键
        pk_col = self.check_primary_key(table_name)
        constraints['has_primary_key'] = pk_col is not None
        
        # 检查自增支持
        constraints['supports_autoincrement'] = self.check_autoincrement(table_name)
        
        # 检查唯一约束
        indexes = self.get_table_indexes(table_name)
        for idx in indexes:
            if idx['unique']:
                if 'username' in idx['columns']:
                    constraints['has_unique_username'] = True
                if 'email' in idx['columns']:
                    constraints['has_unique_email'] = True
        
        return constraints

def main():
    """主函数"""
    print("=" * 70)
    print("数据库表结构检查和修复建议工具")
    print("=" * 70)
    print(f"检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取数据库路径
    if "sqlite:///" in app_config.database_url:
        db_path = app_config.database_url.replace("sqlite:///", "")
        print(f"数据库路径: {db_path}")
    else:
        print("非SQLite数据库，本工具仅支持SQLite")
        return
    
    # 检查文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 创建检查器
    checker = DatabaseTableChecker(db_path)
    
    if not checker.connect():
        return
    
    try:
        # 检查用户表
        print("\n" + "=" * 50)
        print("检查用户表 (users)")
        print("=" * 50)
        
        # 获取表结构
        table_info = checker.get_table_info('users')
        print("表结构:")
        for col in table_info:
            pk_mark = " ★PRIMARY_KEY" if col['pk'] else ""
            print(f"  {col['name']}: {col['type']}{pk_mark}")
        
        # 检查约束
        constraints = checker.check_table_constraints('users')
        print(f"\n约束检查:")
        print(f"  有主键: {'✓' if constraints['has_primary_key'] else '✗'}")
        print(f"  支持自增: {'✓' if constraints['supports_autoincrement'] else '✗'}")
        print(f"  用户名唯一: {'✓' if constraints['has_unique_username'] else '✗'}")
        print(f"  邮箱唯一: {'✓' if constraints['has_unique_email'] else '✗'}")
        
        # 测试不指定ID的插入
        print(f"\n测试不指定ID插入:")
        success, new_id = checker.test_insert_without_id('users')
        if success:
            print(f"  ✓ 插入成功，新ID: {new_id}")
            if new_id and new_id > 0:
                print(f"  ✓ 数据库支持自动生成ID")
            else:
                print(f"  ⚠ 数据库可能不支持自动生成ID")
        else:
            print(f"  ✗ 插入失败")
        
        # 生成修复SQL
        print(f"\n修复建议:")
        fix_sql = checker.generate_fix_sql('users')
        if fix_sql:
            print("生成的修复SQL语句:")
            print("-" * 50)
            for line in fix_sql:
                print(line)
            print("-" * 50)
            
            # 保存到文件
            sql_file = f"fix_users_table_{int(time.time())}.sql"
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fix_sql))
            print(f"\n修复SQL已保存到: {sql_file}")
        else:
            print("✓ 表结构正常，无需修复")
        
        # 检查其他相关表
        related_tables = ['user_sessions', 'projects']
        for table in related_tables:
            print(f"\n检查关联表: {table}")
            try:
                table_info = checker.get_table_info(table)
                if table_info:
                    pk_col = checker.check_primary_key(table)
                    if pk_col:
                        print(f"  ✓ 有主键: {pk_col['name']} ({pk_col['type']})")
                    else:
                        print(f"  ⚠ 无主键")
                else:
                    print(f"  表不存在")
            except Exception as e:
                print(f"  检查失败: {e}")
        
        # 总结和建议
        print(f"\n" + "=" * 50)
        print("总结和建议")
        print("=" * 50)
        
        if not constraints['has_primary_key']:
            print("❌ 关键问题: users表缺少主键")
            print("建议: 立即执行修复SQL，为id列添加PRIMARY KEY约束")
        elif not constraints['supports_autoincrement']:
            print("⚠ 性能问题: users表主键不支持自增")
            print("建议: 执行修复SQL，启用AUTOINCREMENT功能")
        else:
            print("✓ 表结构正常")
        
        if not constraints['has_unique_username']:
            print("⚠ 数据完整性: 缺少用户名唯一约束")
            print("建议: 添加唯一索引防止重复用户名")
        
        if not constraints['has_unique_email']:
            print("⚠ 数据完整性: 缺少邮箱唯一约束")
            print("建议: 添加唯一索引防止重复邮箱")
        
        print(f"\n修复步骤:")
        print(f"1. 备份数据库")
        print(f"2. 执行生成的SQL文件: {sql_file if fix_sql else '无需执行'}")
        print(f"3. 重启应用验证功能")
        
    finally:
        checker.close()
    
    print(f"\n检查完成。")

if __name__ == "__main__":
    main()
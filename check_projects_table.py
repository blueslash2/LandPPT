import sqlite3
import os


def check_projects_table():
    """
    检查项目表和用户表的定义和数据情况
    """
    # 数据库路径（根据实际项目结构调整）
    db_path = '../../landppt.db'
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在，请检查路径")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查项目表
        check_table(cursor, 'projects', '项目表')
        
        # 检查用户表
        check_table(cursor, 'users', '用户表')

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        conn.close()


def check_table(cursor, table_name, table_type):
    """
    检查指定表的结构和数据
    """
    # 检查表是否存在
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        print(f"\n错误：{table_type} 表 '{table_name}' 不存在")
        return

    # 获取表结构
    print(f"\n===== {table_type} 结构定义 =====")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")

    # 获取数据统计
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cursor.fetchone()[0]
    print(f"\n{table_type} 总数: {total}")

    # 获取前5条数据示例
    if total > 0:
        print(f"\n前5条 {table_type} 数据示例:")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        for i, row in enumerate(rows):
            # 格式化输出，避免过长
            row_str = ', '.join([str(x)[:50] for x in row])
            print(f"  {i+1}. {row_str}")
    else:
        print(f"  没有 {table_type} 数据")

    # 特殊检查：用户表中的管理员用户
    if table_name == 'users':
        cursor.execute("SELECT id, username, is_admin FROM users WHERE is_admin = 1 LIMIT 1")
        admin_user = cursor.fetchone()
        if admin_user:
            print(f"\n✅ 找到管理员用户: ID={admin_user[0]}, 用户名={admin_user[1]}, 管理员={admin_user[2]}")
        else:
            print(f"\n⚠️ 未找到管理员用户 (is_admin=1)，请确保已创建管理员账户")


if __name__ == '__main__':
    print("===== 数据库表检查工具 =====")
    print("此脚本将显示项目表和用户表的结构和数据情况\n")
    check_projects_table()
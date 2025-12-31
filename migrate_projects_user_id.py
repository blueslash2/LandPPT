import sqlite3
import os


def migrate_database():
    """
    为现有项目数据库添加username字段，并将所有项目关联到管理员用户
    """
    # 数据库路径（根据实际项目结构调整）
    db_path = '../../landppt.db'
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在，请检查路径")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查Project表是否已有username列
        cursor.execute("PRAGMA table_info(projects)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'username' in columns:
            print("username 字段已存在，无需迁移")
            conn.close()
            return

        # 获取管理员用户名（is_admin=1）
        cursor.execute("SELECT username FROM users WHERE is_admin = 1 LIMIT 1")
        admin_user = cursor.fetchone()
        if not admin_user:
            print("错误：未找到管理员用户（is_admin=1）")
            print("请确保数据库中存在管理员用户（is_admin=1）")
            conn.close()
            return
        admin_username = admin_user[0]
        print(f"找到管理员用户名: {admin_username}")

        # 创建新表（包含username字段）
        cursor.execute('''
            CREATE TABLE projects_new (
                id INTEGER PRIMARY KEY,
                project_id TEXT UNIQUE,
                title TEXT NOT NULL,
                scenario TEXT NOT NULL,
                topic TEXT NOT NULL,
                requirements TEXT,
                status TEXT DEFAULT 'draft',
                outline TEXT,
                slides_html TEXT,
                slides_data TEXT,
                confirmed_requirements TEXT,
                project_metadata TEXT,
                version INTEGER DEFAULT 1,
                share_token TEXT UNIQUE,
                share_enabled BOOLEAN DEFAULT 0,
                created_at FLOAT DEFAULT 0,
                updated_at FLOAT DEFAULT 0,
                username TEXT
            )
        ''')

        # 复制数据到新表（设置username为管理员用户名）
        cursor.execute('''
            INSERT INTO projects_new (
                id, project_id, title, scenario, topic, requirements, status, outline, slides_html, slides_data, confirmed_requirements, project_metadata, version, share_token, share_enabled, created_at, updated_at, username
            )
            SELECT 
                id, project_id, title, scenario, topic, requirements, status, outline, slides_html, slides_data, confirmed_requirements, project_metadata, version, share_token, share_enabled, created_at, updated_at, ?
            FROM projects
        ''', (admin_username,))

        # 删除原表并重命名新表
        cursor.execute("DROP TABLE projects")
        cursor.execute("ALTER TABLE projects_new RENAME TO projects")
        conn.commit()
        print("✅ 数据库迁移完成！所有项目已关联到管理员用户")
        print("   - 项目数量: " + str(cursor.execute("SELECT COUNT(*) FROM projects").fetchone()[0]))
        print("   - 管理员用户名: " + str(admin_username))

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"意外错误: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    print("===== 项目数据库迁移工具 =====")
    print("此脚本将为所有项目添加username字段并关联到管理员用户")
    print("请确保已备份数据库！\n")
    migrate_database()
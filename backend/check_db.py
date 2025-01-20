from database.db import execute_query

def check_tables():
    # 检查scores表是否存在
    success, tables = execute_query("SHOW TABLES")
    if success:
        print("现有表:", [table['Tables_in_fire_gpt'] for table in tables])
    else:
        print("获取表列表失败")

    # 检查scores表结构
    success, columns = execute_query("SHOW COLUMNS FROM scores")
    if success:
        print("\nscores表结构:")
        for col in columns:
            print(f"{col['Field']}: {col['Type']}")
    else:
        print("获取scores表结构失败，可能表不存在")

if __name__ == "__main__":
    check_tables()

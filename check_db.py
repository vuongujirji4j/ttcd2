import pyodbc

def check_database():
    try:
        # Kết nối đến database
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=MSI\SQLEXPRESS;DATABASE=qlns;Trusted_Connection=yes;'
        print("Đang kết nối đến SQL Server...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Kiểm tra các bảng
        print("\nDanh sách các bảng trong database:")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"- {table[0]}")
            
            # Kiểm tra số lượng bản ghi trong mỗi bảng
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  Số lượng bản ghi: {count}")
            
            # Hiển thị cấu trúc bảng
            print("  Cấu trúc bảng:")
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table[0]}'")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    - {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
            
            # Hiển thị 5 bản ghi đầu tiên nếu có dữ liệu
            if count > 0:
                print("  Dữ liệu mẫu (5 bản ghi đầu tiên):")
                cursor.execute(f"SELECT TOP 5 * FROM {table[0]}")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"    {row}")
            print()
        
        conn.close()
        print("Kiểm tra hoàn tất!")
        
    except Exception as e:
        print(f"Lỗi khi kiểm tra database: {str(e)}")
        raise

if __name__ == "__main__":
    check_database() 
import pyodbc
import os

def setup_database():
    try:
        # Connection string using Windows Authentication
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=master;Trusted_Connection=yes;'
        
        print("Connecting to SQL Server...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT database_id FROM sys.databases WHERE Name = 'qlns'")
        if not cursor.fetchone():
            print("Creating database 'qlns'...")
            cursor.execute("CREATE DATABASE qlns")
            conn.commit()
            print("Database created successfully!")
        else:
            print("Database 'qlns' already exists.")
        
        # Switch to qlns database
        cursor.execute("USE qlns")
        
        # Read and execute SQL script
        sql_file = 'K22CNT2_NguyenKhanhLinh_Project4.sql'
        if os.path.exists(sql_file):
            print(f"Reading SQL script from {sql_file}...")
            with open(sql_file, 'r', encoding='utf-8') as file:
                sql_script = file.read()
                
            # Split script into individual statements
            statements = sql_script.split(';')
            
            # Execute each statement
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except pyodbc.Error as e:
                        print(f"Error executing statement: {str(e)}")
                        print(f"Statement: {statement}")
            
            print("SQL script executed successfully!")
        else:
            print(f"SQL script file {sql_file} not found!")
        
        conn.close()
        print("Database setup completed!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 
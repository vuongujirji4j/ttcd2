import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_DRIVER = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
DB_SERVER = os.getenv('DB_SERVER', 'MSI\\SQLEXPRESS')
DB_DATABASE = os.getenv('DB_DATABASE', 'qlns')
DB_TRUSTED = os.getenv('DB_TRUSTED', 'yes')

if DB_TRUSTED.lower() == 'yes':
    CONNECTION_STRING = f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;'
else:
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
    CONNECTION_STRING = f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;'

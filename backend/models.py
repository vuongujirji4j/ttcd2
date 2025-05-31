import pyodbc
from config import CONNECTION_STRING
from datetime import datetime

class DatabaseConnection:
    @staticmethod
    def get_connection():
        try:
            return pyodbc.connect(CONNECTION_STRING)
        except pyodbc.Error as e:
            print(f"Database connection error: {str(e)}")
            raise Exception(f"Could not connect to database: {str(e)}")

class NhanVien:
    def __init__(self, MaNhanVien=None, HoTen=None, NgaySinh=None, GioiTinh=None, 
                 DiaChi=None, SoDienThoai=None, Email=None, MaPhongBan=None, 
                 ChucVu=None, NgayVaoLam=None):
        self.MaNhanVien = MaNhanVien
        self.HoTen = HoTen
        self.NgaySinh = NgaySinh
        self.GioiTinh = GioiTinh
        self.DiaChi = DiaChi
        self.SoDienThoai = SoDienThoai
        self.Email = Email
        self.MaPhongBan = MaPhongBan
        self.ChucVu = ChucVu
        self.NgayVaoLam = NgayVaoLam

    @staticmethod
    def get_all():
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM NhanVien")
            nhanvien_list = []
            for row in cursor.fetchall():
                nhanvien = NhanVien(
                    MaNhanVien=row[0],
                    HoTen=row[1],
                    NgaySinh=row[2],
                    GioiTinh=row[3],
                    DiaChi=row[4],
                    SoDienThoai=row[5],
                    Email=row[6],
                    MaPhongBan=row[7],
                    ChucVu=row[8],
                    NgayVaoLam=row[9]
                )
                nhanvien_list.append(nhanvien)
            conn.close()
            return nhanvien_list
        except Exception as e:
            print(f"Error getting employees: {str(e)}")
            raise

    @staticmethod
    def get_by_id(id):
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM NhanVien WHERE MaNhanVien = ?", id)
            row = cursor.fetchone()
            if row:
                nhanvien = NhanVien(
                    MaNhanVien=row[0],
                    HoTen=row[1],
                    NgaySinh=row[2],
                    GioiTinh=row[3],
                    DiaChi=row[4],
                    SoDienThoai=row[5],
                    Email=row[6],
                    MaPhongBan=row[7],
                    ChucVu=row[8],
                    NgayVaoLam=row[9]
                )
                conn.close()
                return nhanvien
            conn.close()
            return None
        except Exception as e:
            print(f"Error getting employee by ID: {str(e)}")
            raise

    def create(self):
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO NhanVien (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, 
                                    Email, MaPhongBan, ChucVu, NgayVaoLam)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.HoTen, self.NgaySinh, self.GioiTinh, self.DiaChi, 
                  self.SoDienThoai, self.Email, self.MaPhongBan, self.ChucVu, 
                  self.NgayVaoLam))
            conn.commit()
            self.MaNhanVien = cursor.rowcount
            conn.close()
            return self
        except Exception as e:
            print(f"Error creating employee: {str(e)}")
            raise

    def update(self):
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE NhanVien
                SET HoTen = ?, NgaySinh = ?, GioiTinh = ?, DiaChi = ?,
                    SoDienThoai = ?, Email = ?, MaPhongBan = ?, ChucVu = ?,
                    NgayVaoLam = ?
                WHERE MaNhanVien = ?
            """, (self.HoTen, self.NgaySinh, self.GioiTinh, self.DiaChi,
                  self.SoDienThoai, self.Email, self.MaPhongBan, self.ChucVu,
                  self.NgayVaoLam, self.MaNhanVien))
            conn.commit()
            conn.close()
            return self
        except Exception as e:
            print(f"Error updating employee: {str(e)}")
            raise

    @staticmethod
    def delete(id):
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM NhanVien WHERE MaNhanVien = ?", id)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting employee: {str(e)}")
            raise

class PhongBan:
    def __init__(self, MaPhongBan=None, TenPhongBan=None, MoTa=None, TruongPhong=None):
        self.MaPhongBan = MaPhongBan
        self.TenPhongBan = TenPhongBan
        self.MoTa = MoTa
        self.TruongPhong = TruongPhong

    @staticmethod
    def get_all():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PhongBan")
        phongban_list = []
        for row in cursor.fetchall():
            phongban = PhongBan(
                MaPhongBan=row[0],
                TenPhongBan=row[1],
                MoTa=row[2],
                TruongPhong=row[3]
            )
            phongban_list.append(phongban)
        conn.close()
        return phongban_list

    @staticmethod
    def get_by_id(id):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PhongBan WHERE MaPhongBan = ?", id)
        row = cursor.fetchone()
        if row:
            phongban = PhongBan(
                MaPhongBan=row[0],
                TenPhongBan=row[1],
                MoTa=row[2],
                TruongPhong=row[3]
            )
            conn.close()
            return phongban
        conn.close()
        return None

    def create(self):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO PhongBan (TenPhongBan, MoTa, TruongPhong)
            VALUES (?, ?, ?)
        """, (self.TenPhongBan, self.MoTa, self.TruongPhong))
        conn.commit()
        self.MaPhongBan = cursor.rowcount
        conn.close()
        return self

    def update(self):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PhongBan
            SET TenPhongBan = ?, MoTa = ?, TruongPhong = ?
            WHERE MaPhongBan = ?
        """, (self.TenPhongBan, self.MoTa, self.TruongPhong, self.MaPhongBan))
        conn.commit()
        conn.close()
        return self

    @staticmethod
    def delete(id):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PhongBan WHERE MaPhongBan = ?", id)
        conn.commit()
        conn.close()
        return True

class ChamCong:
    def __init__(self, MaChamCong=None, MaNhanVien=None, Ngay=None, GioVao=None, GioRa=None):
        self.MaChamCong = MaChamCong
        self.MaNhanVien = MaNhanVien
        self.Ngay = Ngay
        self.GioVao = GioVao
        self.GioRa = GioRa

    @staticmethod
    def get_all():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ChamCong")
        chamcong_list = []
        for row in cursor.fetchall():
            chamcong = ChamCong(
                MaChamCong=row[0],
                MaNhanVien=row[1],
                Ngay=row[2],
                GioVao=row[3],
                GioRa=row[4]
            )
            chamcong_list.append(chamcong)
        conn.close()
        return chamcong_list

    @staticmethod
    def get_by_id(id):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ChamCong WHERE MaChamCong = ?", id)
        row = cursor.fetchone()
        if row:
            chamcong = ChamCong(
                MaChamCong=row[0],
                MaNhanVien=row[1],
                Ngay=row[2],
                GioVao=row[3],
                GioRa=row[4]
            )
            conn.close()
            return chamcong
        conn.close()
        return None

    def create(self):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ChamCong (MaNhanVien, Ngay, GioVao, GioRa)
            VALUES (?, ?, ?, ?)
        """, (self.MaNhanVien, self.Ngay, self.GioVao, self.GioRa))
        conn.commit()
        self.MaChamCong = cursor.rowcount
        conn.close()
        return self

    def update(self):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ChamCong
            SET MaNhanVien = ?, Ngay = ?, GioVao = ?, GioRa = ?
            WHERE MaChamCong = ?
        """, (self.MaNhanVien, self.Ngay, self.GioVao, self.GioRa, self.MaChamCong))
        conn.commit()
        conn.close()
        return self

    @staticmethod
    def delete(id):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ChamCong WHERE MaChamCong = ?", id)
        conn.commit()
        conn.close()
        return True 
from flask import Flask, request, jsonify
import pyodbc

# Cấu hình kết nối đến SQL Server
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-87R90NS;"
    "Database=qlns;"
    "Trusted_Connection=yes;"
)
con = pyodbc.connect(conn_str)

app = Flask(__name__)

# ──────────────────────────────
# 1. QUẢN LÝ NHÂN VIÊN
# Lấy danh sách nhân viên
@app.route('/nhanvien', methods=['GET'])
def get_nhanvien():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM NhanVien")
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        employees = [dict(zip(cols, row)) for row in rows]
        return jsonify(employees)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới nhân viên
@app.route('/nhanvien', methods=['POST'])
def add_nhanvien():
    try:
        data = request.get_json()
        # Các trường cần có: HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, Email, MaPhongBan, ChucVu, NgayVaoLam
        ho_ten      = data.get('HoTen')
        ngay_sinh   = data.get('NgaySinh')
        gioi_tinh   = data.get('GioiTinh')
        dia_chi     = data.get('DiaChi')
        sdt         = data.get('SoDienThoai')
        email       = data.get('Email')
        ma_phongban = data.get('MaPhongBan')
        chuc_vu     = data.get('ChucVu')
        ngay_vao    = data.get('NgayVaoLam')

        cursor = con.cursor()
        sql = """INSERT INTO NhanVien 
                 (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, Email, MaPhongBan, ChucVu, NgayVaoLam)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (ho_ten, ngay_sinh, gioi_tinh, dia_chi, sdt, email, ma_phongban, chuc_vu, ngay_vao))
        con.commit()
        # Lấy ID vừa thêm (sử dụng @@IDENTITY cho SQL Server)
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm nhân viên thành công", "MaNhanVien": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cập nhật nhân viên
@app.route('/nhanvien/<int:maNV>', methods=['PUT'])
def update_nhanvien(maNV):
    try:
        data = request.get_json()
        ho_ten      = data.get('HoTen')
        ngay_sinh   = data.get('NgaySinh')
        gioi_tinh   = data.get('GioiTinh')
        dia_chi     = data.get('DiaChi')
        sdt         = data.get('SoDienThoai')
        email       = data.get('Email')
        ma_phongban = data.get('MaPhongBan')
        chuc_vu     = data.get('ChucVu')
        ngay_vao    = data.get('NgayVaoLam')

        cursor = con.cursor()
        sql = """UPDATE NhanVien 
                 SET HoTen = ?, NgaySinh = ?, GioiTinh = ?, DiaChi = ?, SoDienThoai = ?, Email = ?, MaPhongBan = ?, ChucVu = ?, NgayVaoLam = ?
                 WHERE MaNhanVien = ?"""
        cursor.execute(sql, (ho_ten, ngay_sinh, gioi_tinh, dia_chi, sdt, email, ma_phongban, chuc_vu, ngay_vao, maNV))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật nhân viên thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Xóa nhân viên
@app.route('/nhanvien/<int:maNV>', methods=['DELETE'])
def delete_nhanvien(maNV):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM NhanVien WHERE MaNhanVien = ?", (maNV,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa nhân viên thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ──────────────────────────────
# 2. QUẢN LÝ PHÒNG BAN
# Lấy danh sách phòng ban
@app.route('/phongban', methods=['GET'])
def get_phongban():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM PhongBan")
        cols = [desc[0] for desc in cursor.description]
        departments = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(departments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới phòng ban
@app.route('/phongban', methods=['POST'])
def add_phongban():
    try:
        data = request.get_json()
        ten_phongban = data.get('TenPhongBan')
        mo_ta       = data.get('MoTa')
        truong_phong= data.get('TruongPhong')  # Có thể để NULL nếu chưa có
        
        cursor = con.cursor()
        sql = "INSERT INTO PhongBan (TenPhongBan, MoTa, TruongPhong) VALUES (?, ?, ?)"
        cursor.execute(sql, (ten_phongban, mo_ta, truong_phong))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm phòng ban thành công", "MaPhongBan": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật phòng ban
@app.route('/phongban/<int:maPB>', methods=['PUT'])
def update_phongban(maPB):
    try:
        data = request.get_json()
        ten = data.get('TenPhongBan')
        mota = data.get('MoTa')
        truongphong = data.get('TruongPhong')

        cursor = con.cursor()
        cursor.execute("UPDATE PhongBan SET TenPhongBan = ?, MoTa = ?, TruongPhong = ? WHERE MaPhongBan = ?",
                       (ten, mota, truongphong, maPB))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật phòng ban thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa phòng ban
@app.route('/phongban/<int:maPB>', methods=['DELETE'])
def delete_phongban(maPB):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM PhongBan WHERE MaPhongBan = ?", (maPB,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa phòng ban thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────
# 3. QUẢN LÝ CHẤM CÔNG
# Lấy danh sách chấm công
@app.route('/chamcong', methods=['GET'])
def get_chamcong():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM ChamCong")
        cols = [desc[0] for desc in cursor.description]
        records = [dict(zip(cols, [str(val) if val is not None else None for val in row])) 
                  for row in cursor.fetchall()]
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới chấm công
@app.route('/chamcong', methods=['POST'])
def add_chamcong():
    try:
        data = request.get_json()
        ma_nv    = data.get('MaNhanVien')
        ngay     = data.get('Ngay')
        gio_vao  = data.get('GioVao')
        gio_ra   = data.get('GioRa')
        
        cursor = con.cursor()
        sql = "INSERT INTO ChamCong (MaNhanVien, Ngay, GioVao, GioRa) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (ma_nv, ngay, gio_vao, gio_ra))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm chấm công thành công", "MaChamCong": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật chấm công
@app.route('/chamcong/<int:maCC>', methods=['PUT'])
def update_chamcong(maCC):
    try:
        data = request.get_json()
        ma_nv = data.get('MaNhanVien')
        ngay = data.get('Ngay')
        gio_vao = data.get('GioVao')
        gio_ra = data.get('GioRa')

        cursor = con.cursor()
        cursor.execute("UPDATE ChamCong SET MaNhanVien=?, Ngay=?, GioVao=?, GioRa=? WHERE MaChamCong=?",
                       (ma_nv, ngay, gio_vao, gio_ra, maCC))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật chấm công thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa chấm công
@app.route('/chamcong/<int:maCC>', methods=['DELETE'])
def delete_chamcong(maCC):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM ChamCong WHERE MaChamCong = ?", (maCC,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa chấm công thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ──────────────────────────────
# 4. QUẢN LÝ LƯƠNG
# Lấy danh sách thông tin lương
@app.route('/luong', methods=['GET'])
def get_luong():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Luong")
        cols = [desc[0] for desc in cursor.description]
        records = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới thông tin lương
@app.route('/luong', methods=['POST'])
def add_luong():
    try:
        data = request.get_json()
        ma_nv          = data.get('MaNhanVien')
        thang          = data.get('Thang')
        nam            = data.get('Nam')
        luong_co_ban   = data.get('LuongCoBan')
        phu_cap        = data.get('PhuCap')
        khau_tru       = data.get('KhauTru')
        luong_thuc     = data.get('LuongThucNhan')
        
        cursor = con.cursor()
        sql = """INSERT INTO Luong 
                 (MaNhanVien, Thang, Nam, LuongCoBan, PhuCap, KhauTru, LuongThucNhan)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (ma_nv, thang, nam, luong_co_ban, phu_cap, khau_tru, luong_thuc))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm thông tin lương thành công", "MaLuong": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật thông tin lương
@app.route('/luong/<int:maLuong>', methods=['PUT'])
def update_luong(maLuong):
    try:
        data = request.get_json()
        cursor = con.cursor()
        cursor.execute("""
            UPDATE Luong 
            SET MaNhanVien=?, Thang=?, Nam=?, LuongCoBan=?, PhuCap=?, KhauTru=?, LuongThucNhan=?
            WHERE MaLuong=?""",
            (data.get('MaNhanVien'), data.get('Thang'), data.get('Nam'), data.get('LuongCoBan'),
             data.get('PhuCap'), data.get('KhauTru'), data.get('LuongThucNhan'), maLuong))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật thông tin lương thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa thông tin lương
@app.route('/luong/<int:maLuong>', methods=['DELETE'])
def delete_luong(maLuong):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM Luong WHERE MaLuong = ?", (maLuong,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa thông tin lương thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ──────────────────────────────
# 5. QUẢN LÝ ĐÁNH GIÁ (DANHGIA)
# Lấy danh sách đánh giá
@app.route('/danhgia', methods=['GET'])
def get_danhgia():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM DanhGia")
        cols = [desc[0] for desc in cursor.description]
        records = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới đánh giá
@app.route('/danhgia', methods=['POST'])
def add_danhgia():
    try:
        data = request.get_json()
        ma_nv      = data.get('MaNhanVien')
        ky_danhgia = data.get('KyDanhGia')
        diem_so    = data.get('DiemSo')
        nhan_xet   = data.get('NhanXet')
        
        cursor = con.cursor()
        sql = """INSERT INTO DanhGia 
                 (MaNhanVien, KyDanhGia, DiemSo, NhanXet)
                 VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (ma_nv, ky_danhgia, diem_so, nhan_xet))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm đánh giá thành công", "MaDanhGia": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật đánh giá
@app.route('/danhgia/<int:maDG>', methods=['PUT'])
def update_danhgia(maDG):
    try:
        data = request.get_json()
        cursor = con.cursor()
        cursor.execute("""
            UPDATE DanhGia 
            SET MaNhanVien=?, KyDanhGia=?, DiemSo=?, NhanXet=?
            WHERE MaDanhGia=?""",
            (data.get('MaNhanVien'), data.get('KyDanhGia'), data.get('DiemSo'), data.get('NhanXet'), maDG))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật đánh giá thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa đánh giá
@app.route('/danhgia/<int:maDG>', methods=['DELETE'])
def delete_danhgia(maDG):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM DanhGia WHERE MaDanhGia = ?", (maDG,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa đánh giá thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ──────────────────────────────
# 6. QUẢN LÝ HỢP ĐỒNG (HOPDONG)
# Lấy danh sách hợp đồng
@app.route('/hopdong', methods=['GET'])
def get_hopdong():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM HopDong")
        cols = [desc[0] for desc in cursor.description]
        records = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới hợp đồng
@app.route('/hopdong', methods=['POST'])
def add_hopdong():
    try:
        data = request.get_json()
        ma_nv         = data.get('MaNhanVien')
        loai_hopdong  = data.get('LoaiHopDong')
        ngay_batdau   = data.get('NgayBatDau')
        ngay_ketthuc  = data.get('NgayKetThuc')
        luong_co_ban  = data.get('LuongCoBan')
        phu_cap       = data.get('PhuCap')
        trang_thai    = data.get('TrangThai') or 'Đang hiệu lực'
        
        cursor = con.cursor()
        sql = """INSERT INTO HopDong
                 (MaNhanVien, LoaiHopDong, NgayBatDau, NgayKetThuc, LuongCoBan, PhuCap, TrangThai)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (ma_nv, loai_hopdong, ngay_batdau, ngay_ketthuc, luong_co_ban, phu_cap, trang_thai))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm hợp đồng thành công", "MaHopDong": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật hợp đồng
@app.route('/hopdong/<int:maHD>', methods=['PUT'])
def update_hopdong(maHD):
    try:
        data = request.get_json()
        cursor = con.cursor()
        cursor.execute("""
            UPDATE HopDong 
            SET MaNhanVien=?, LoaiHopDong=?, NgayBatDau=?, NgayKetThuc=?, LuongCoBan=?, PhuCap=?, TrangThai=?
            WHERE MaHopDong=?""",
            (data.get('MaNhanVien'), data.get('LoaiHopDong'), data.get('NgayBatDau'), data.get('NgayKetThuc'),
             data.get('LuongCoBan'), data.get('PhuCap'), data.get('TrangThai'), maHD))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật hợp đồng thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa hợp đồng
@app.route('/hopdong/<int:maHD>', methods=['DELETE'])
def delete_hopdong(maHD):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM HopDong WHERE MaHopDong = ?", (maHD,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa hợp đồng thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ──────────────────────────────
# 7. QUẢN LÝ ĐƠN NGHỈ PHÉP (DONNGHIPHEP)
# Lấy danh sách đơn nghỉ phép
@app.route('/donnghiphep', methods=['GET'])
def get_donnghiphep():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM DonNghiPhep")
        cols = [desc[0] for desc in cursor.description]
        records = [dict(zip(cols, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Thêm mới đơn nghỉ phép
@app.route('/donnghiphep', methods=['POST'])
def add_donnghiphep():
    try:
        data = request.get_json()
        ma_nv         = data.get('MaNhanVien')
        ngay_batdau   = data.get('NgayBatDau')
        ngay_ketthuc  = data.get('NgayKetThuc')
        ly_do         = data.get('LyDo')
        trang_thai    = data.get('TrangThai') or 'Chờ duyệt'
        
        cursor = con.cursor()
        sql = """INSERT INTO DonNghiPhep
                 (MaNhanVien, NgayBatDau, NgayKetThuc, LyDo, TrangThai)
                 VALUES (?, ?, ?, ?, ?)"""
        cursor.execute(sql, (ma_nv, ngay_batdau, ngay_ketthuc, ly_do, trang_thai))
        con.commit()
        cursor.execute("SELECT @@IDENTITY")
        new_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({"message": "Thêm đơn nghỉ phép thành công", "MaDon": new_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Cập nhật đơn nghỉ phép
@app.route('/donnghiphep/<int:maDon>', methods=['PUT'])
def update_donnghiphep(maDon):
    try:
        data = request.get_json()
        cursor = con.cursor()
        cursor.execute("""
            UPDATE DonNghiPhep 
            SET MaNhanVien=?, NgayBatDau=?, NgayKetThuc=?, LyDo=?, TrangThai=?
            WHERE MaDon=?""",
            (data.get('MaNhanVien'), data.get('NgayBatDau'), data.get('NgayKetThuc'),
             data.get('LyDo'), data.get('TrangThai'), maDon))
        con.commit()
        cursor.close()
        return jsonify({"message": "Cập nhật đơn nghỉ phép thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Xóa đơn nghỉ phép
@app.route('/donnghiphep/<int:maDon>', methods=['DELETE'])
def delete_donnghiphep(maDon):
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM DonNghiPhep WHERE MaDon = ?", (maDon,))
        con.commit()
        cursor.close()
        return jsonify({"message": "Xóa đơn nghỉ phép thành công"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

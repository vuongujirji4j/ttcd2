from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
from routes import api
from models import DatabaseConnection
from config import CONNECTION_STRING
import pyodbc
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Thay đổi secret key của bạn
CORS(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# Kết nối database
def get_db_connection():
    conn = pyodbc.connect(CONNECTION_STRING)
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('api.login'))
        return f(*args, **kwargs)
    return decorated_function

def require_roles(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role_id' not in session:
                return redirect(url_for('api.login'))
            role_id = session.get('role_id')
            # Map role_id sang tên quyền
            role_map = {1: 'Admin', 2: 'TruongPhong', 3: 'NhanVien'}
            user_role = role_map.get(role_id)
            if user_role not in role_names:
                flash('Bạn không có quyền truy cập chức năng này!', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
@login_required
def home():
    # Thử kết nối database
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Tổng số nhân viên
        cursor.execute("SELECT COUNT(*) FROM NhanVien")
        tong_nv = cursor.fetchone()[0]
        # Tổng số phòng ban
        cursor.execute("SELECT COUNT(*) FROM PhongBan")
        tong_pb = cursor.fetchone()[0]
        # Tổng chi phí lương (giả sử có bảng Luong, trường LuongThucNhan)
        cursor.execute("SELECT SUM(LuongThucNhan) FROM Luong")
        tong_luong = cursor.fetchone()[0] or 0
        # Số cảnh báo (giả sử có bảng DanhGia, cảnh báo là điểm < 60)
        cursor.execute("SELECT COUNT(*) FROM DanhGia WHERE DiemSo < 60")
        canh_bao = cursor.fetchone()[0]
        # Danh sách nhân viên mới (3 người mới nhất)
        cursor.execute("SELECT TOP 3 HoTen, MaPhongBan FROM NhanVien ORDER BY MaNhanVien DESC")
        nhanvien_moi = cursor.fetchall()
        # Danh sách phòng ban (3 phòng ban đầu tiên)
        cursor.execute("SELECT TOP 3 TenPhongBan, TruongPhong, (SELECT HoTen FROM NhanVien WHERE MaNhanVien = TruongPhong) AS TruongPhongTen, (SELECT COUNT(*) FROM NhanVien WHERE MaPhongBan = PhongBan.MaPhongBan) AS SoLuong FROM PhongBan")
        phongban_list = cursor.fetchall()
        conn.close()
        return render_template('index.html', tong_nv=tong_nv, tong_pb=tong_pb, tong_luong=tong_luong, canh_bao=canh_bao, nhanvien_moi=nhanvien_moi, phongban_list=phongban_list)
    except Exception as e:
        return f"Không thể kết nối database: {str(e)}", 500

@app.route('/nhanvien')
@login_required
def nhanvien_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy danh sách nhân viên với tên phòng ban
    cursor.execute("""
        SELECT nv.MaNhanVien, nv.HoTen, nv.NgaySinh, nv.GioiTinh, nv.DiaChi, 
               nv.SoDienThoai, nv.Email, pb.TenPhongBan, nv.ChucVu, nv.NgayVaoLam
        FROM NhanVien nv
        LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
        ORDER BY pb.TenPhongBan, nv.HoTen
    """)
    nhanviens = cursor.fetchall()
    
    # Lấy danh sách phòng ban với số lượng nhân viên
    cursor.execute("""
        SELECT pb.TenPhongBan, pb.MoTa, nv.HoTen as TruongPhong,
               (SELECT COUNT(*) FROM NhanVien WHERE MaPhongBan = pb.MaPhongBan) as SoNhanVien
        FROM PhongBan pb
        LEFT JOIN NhanVien nv ON pb.TruongPhong = nv.MaNhanVien
        ORDER BY pb.TenPhongBan
    """)
    phongban_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('nhanvien_list.html', nhanviens=nhanviens, phongban_list=phongban_list)

@app.route('/nhanvien/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def add_nhanvien():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Lấy dữ liệu từ form (đúng tên trường trong form HTML)
            hoten = request.form['HoTen']
            ngaysinh = request.form['NgaySinh']
            gioitinh = request.form['GioiTinh']
            diachi = request.form['DiaChi']
            sodienthoai = request.form['SoDienThoai']
            email = request.form['Email']
            phongban = request.form['MaPhongBan']
            chucvu = request.form['ChucVu']
            ngayvaolam = request.form['NgayVaoLam']
            # Thêm nhân viên mới
            cursor.execute("""
                INSERT INTO NhanVien (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, 
                                    Email, MaPhongBan, ChucVu, NgayVaoLam)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hoten, ngaysinh, gioitinh, diachi, sodienthoai, email, phongban, chucvu, ngayvaolam))
            conn.commit()
            flash('Thêm nhân viên thành công!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('nhanvien_list'))
        except Exception as e:
            flash(f'Lỗi khi thêm nhân viên: {str(e)}', 'danger')
            return redirect(url_for('add_nhanvien'))
    # GET request - hiển thị form thêm
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaPhongBan, TenPhongBan FROM PhongBan ORDER BY TenPhongBan")
    phongbans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('nhanvien_add.html', phongbans=phongbans)

@app.route('/nhanvien/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def edit_nhanvien(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NhanVien WHERE MaNhanVien = ?", (id,))
    nhanvien = cursor.fetchone()
    cursor.execute("SELECT MaPhongBan, TenPhongBan FROM PhongBan ORDER BY TenPhongBan")
    phongbans = cursor.fetchall()
    if request.method == 'POST':
        try:
            hoten = request.form['HoTen']
            ngaysinh = request.form['NgaySinh']
            gioitinh = request.form['GioiTinh']
            diachi = request.form['DiaChi']
            sodienthoai = request.form['SoDienThoai']
            email = request.form['Email']
            phongban = request.form['MaPhongBan']
            chucvu = request.form['ChucVu']
            ngayvaolam = request.form['NgayVaoLam']
            cursor.execute("""
                UPDATE NhanVien SET HoTen=?, NgaySinh=?, GioiTinh=?, DiaChi=?, SoDienThoai=?, Email=?, MaPhongBan=?, ChucVu=?, NgayVaoLam=? WHERE MaNhanVien=?
            """, (hoten, ngaysinh, gioitinh, diachi, sodienthoai, email, phongban, chucvu, ngayvaolam, id))
            conn.commit()
            flash('Cập nhật nhân viên thành công!', 'success')
            return redirect(url_for('nhanvien_list'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật nhân viên: {str(e)}', 'danger')
    cursor.close()
    conn.close()
    return render_template('nhanvien_edit.html', nhanvien=nhanvien, phongbans=phongbans)

@app.route('/nhanvien/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin')
def delete_nhanvien(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kiểm tra xem nhân viên có phải là trưởng phòng không
        cursor.execute("SELECT COUNT(*) FROM PhongBan WHERE TruongPhong=?", (id,))
        is_truongphong = cursor.fetchone()[0] > 0
        
        if is_truongphong:
            flash('Không thể xóa nhân viên đang là trưởng phòng!', 'danger')
            return redirect(url_for('nhanvien_list'))
        
        # Xóa nhân viên
        cursor.execute("DELETE FROM NhanVien WHERE MaNhanVien=?", (id,))
        conn.commit()
        
        flash('Xóa nhân viên thành công!', 'success')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        flash(f'Lỗi khi xóa nhân viên: {str(e)}', 'danger')
    
    return redirect(url_for('nhanvien_list'))

@app.route('/phongban')
@login_required
def phongban_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pb.MaPhongBan, pb.TenPhongBan, pb.MoTa, nv.HoTen as TruongPhongTen
            FROM PhongBan pb
            LEFT JOIN NhanVien nv ON pb.TruongPhong = nv.MaNhanVien
        ''')
        phongbans = cursor.fetchall()
        conn.close()
        return render_template('phongban_list.html', phongbans=phongbans)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('phongban_list.html', phongbans=[])

@app.route('/phongban/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def add_phongban():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute("""
                INSERT INTO PhongBan (TenPhongBan, MoTa, TruongPhong)
                VALUES (?, ?, ?)
            """, (
                request.form['TenPhongBan'],
                request.form['MoTa'],
                request.form['TruongPhong']
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Thêm phòng ban thành công!', 'success')
            return redirect(url_for('phongban_list'))
        conn.close()
        return render_template('phongban_add.html', nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi thêm phòng ban: {str(e)}', 'danger')
        return render_template('phongban_add.html', nhanviens=[])

@app.route('/phongban/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def edit_phongban(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute("""
                UPDATE PhongBan SET TenPhongBan=?, MoTa=?, TruongPhong=? WHERE MaPhongBan=?
            """, (
                request.form['TenPhongBan'],
                request.form['MoTa'],
                request.form['TruongPhong'],
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật phòng ban thành công!', 'success')
            return redirect(url_for('phongban_list'))
        else:
            cursor.execute("SELECT MaPhongBan, TenPhongBan, MoTa, TruongPhong FROM PhongBan WHERE MaPhongBan=?", (id,))
            phongban = cursor.fetchone()
            conn.close()
            if not phongban:
                from flask import flash
                flash('Không tìm thấy phòng ban', 'danger')
                return redirect(url_for('phongban_list'))
            return render_template('phongban_edit.html', phongban=phongban, nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('phongban_list'))

@app.route('/phongban/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin')
def delete_phongban(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PhongBan WHERE MaPhongBan=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa phòng ban thành công!', 'success')
        return redirect(url_for('phongban_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa phòng ban: {str(e)}', 'danger')
        return redirect(url_for('phongban_list'))

@app.route('/chamcong')
@login_required
def chamcong_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Lấy danh sách nhân viên có chấm công
        cursor.execute('''
            SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan
            FROM NhanVien nv
            LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
            WHERE EXISTS (SELECT 1 FROM ChamCong cc WHERE cc.MaNhanVien = nv.MaNhanVien)
        ''')
        nhanviens = cursor.fetchall()
        chamcong_data = []
        for nv in nhanviens:
            ma_nv = nv.MaNhanVien
            # Lấy danh sách chấm công của nhân viên này
            cursor.execute('''
                SELECT cc.Ngay, pb.TenPhongBan, cc.GioVao, cc.GioRa,
                    CASE WHEN cc.GioVao > '08:00' THEN 1 ELSE 0 END AS DiMuon,
                    cc.MaChamCong
                FROM ChamCong cc
                LEFT JOIN PhongBan pb ON pb.MaPhongBan = (SELECT MaPhongBan FROM NhanVien WHERE MaNhanVien = cc.MaNhanVien)
                WHERE cc.MaNhanVien = ?
                ORDER BY cc.Ngay DESC
            ''', (ma_nv,))
            chamcong_list = cursor.fetchall()
            tong_ngay_lam = len(chamcong_list)
            tong_di_muon = sum([cc.DiMuon for cc in chamcong_list])
            chamcong_data.append({
                'MaNhanVien': ma_nv,
                'HoTen': nv.HoTen,
                'TenPhongBan': nv.TenPhongBan,
                'tong_ngay_lam': tong_ngay_lam,
                'tong_di_muon': tong_di_muon,
                'chamcong_list': chamcong_list
            })
        conn.close()
        return render_template('chamcong_list.html', nhanviens=chamcong_data)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('chamcong_list.html', nhanviens=[])

@app.route('/chamcong/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong', 'NhanVien')
def add_chamcong():
    if request.method == 'POST':
        if session.get('role_id') == 3:  # Nhân viên
            ma_nv_form = int(request.form.get('MaNhanVien'))
            if ma_nv_form != session.get('ma_nhanvien'):
                flash('Bạn chỉ được phép chấm công cho chính mình!', 'danger')
                return redirect(url_for('chamcong_list'))
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan FROM NhanVien nv LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan")
            nhanviens = cursor.fetchall()
            # Tạo dict MaNhanVien -> TenPhongBan để JS sử dụng
            pb_map = {str(nv.MaNhanVien): nv.TenPhongBan for nv in nhanviens}
            if request.method == 'POST':
                cursor.execute("""
                    INSERT INTO ChamCong (MaNhanVien, Ngay, GioVao, GioRa, TrangThai)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    request.form['MaNhanVien'],
                    request.form['Ngay'],
                    request.form['GioVao'],
                    request.form['GioRa'],
                    request.form.get('TrangThai', '')
                ))
                conn.commit()
                conn.close()
                from flask import flash
                flash('Thêm chấm công thành công!', 'success')
                return redirect(url_for('chamcong_list'))
            conn.close()
            return render_template('chamcong_add.html', nhanviens=nhanviens, pb_map=pb_map)
        except Exception as e:
            from flask import flash
            flash(f'Lỗi thêm chấm công: {str(e)}', 'danger')
            return render_template('chamcong_add.html', nhanviens=[], pb_map={})
    # GET request - hiển thị form thêm
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan FROM NhanVien nv LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan")
    nhanviens = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('chamcong_add.html', nhanviens=nhanviens, pb_map={})

@app.route('/chamcong/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def edit_chamcong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan FROM NhanVien nv LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan")
        nhanviens = cursor.fetchall()
        pb_map = {str(nv.MaNhanVien): nv.TenPhongBan for nv in nhanviens}
        if request.method == 'POST':
            cursor.execute("""
                UPDATE ChamCong SET MaNhanVien=?, Ngay=?, GioVao=?, GioRa=?, TrangThai=? WHERE MaChamCong=?
            """, (
                request.form['MaNhanVien'],
                request.form['Ngay'],
                request.form['GioVao'],
                request.form['GioRa'],
                request.form.get('TrangThai', ''),
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật chấm công thành công!', 'success')
            return redirect(url_for('chamcong_list'))
        else:
            cursor.execute("SELECT MaChamCong, MaNhanVien, Ngay, GioVao, GioRa, TrangThai FROM ChamCong WHERE MaChamCong=?", (id,))
            chamcong = cursor.fetchone()
            conn.close()
            if not chamcong:
                from flask import flash
                flash('Không tìm thấy bản ghi chấm công', 'danger')
                return redirect(url_for('chamcong_list'))
            return render_template('chamcong_edit.html', chamcong=chamcong, nhanviens=nhanviens, pb_map=pb_map)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('chamcong_list'))

@app.route('/chamcong/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def delete_chamcong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ChamCong WHERE MaChamCong=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa chấm công thành công!', 'success')
        return redirect(url_for('chamcong_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa chấm công: {str(e)}', 'danger')
        return redirect(url_for('chamcong_list'))

@app.route('/luong')
@login_required
def luong_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Lấy danh sách nhân viên có lương, thêm ChucVu
        cursor.execute('''
            SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan, nv.ChucVu
            FROM NhanVien nv
            LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
            WHERE EXISTS (SELECT 1 FROM Luong l WHERE l.MaNhanVien = nv.MaNhanVien)
        ''')
        nhanviens = cursor.fetchall()
        luong_data = []
        for nv in nhanviens:
            ma_nv = nv.MaNhanVien
            # Lấy danh sách lương của nhân viên này
            cursor.execute('''
                SELECT l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.KhauTru, l.LuongThucNhan, l.MaLuong
                FROM Luong l
                WHERE l.MaNhanVien = ?
                ORDER BY l.Nam DESC, l.Thang DESC
            ''', (ma_nv,))
            luong_list = cursor.fetchall()
            tong_luong = sum([l.LuongThucNhan or 0 for l in luong_list])
            tong_phucap = sum([l.PhuCap or 0 for l in luong_list])
            tong_khautru = sum([l.KhauTru or 0 for l in luong_list])
            luong_data.append({
                'MaNhanVien': ma_nv,
                'HoTen': nv.HoTen,
                'TenPhongBan': nv.TenPhongBan,
                'ChucVu': nv.ChucVu,
                'tong_luong': tong_luong,
                'tong_phucap': tong_phucap,
                'tong_khautru': tong_khautru,
                'luong_list': luong_list
            })
        conn.close()
        return render_template('luong_list.html', nhanviens=luong_data)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('luong_list.html', nhanviens=[])

@app.route('/luong/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def add_luong():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            luongcoban = float(request.form['LuongCoBan'])
            phucap = float(request.form['PhuCap'])
            khautru = float(request.form['KhauTru'])
            luongthucnhan = luongcoban + phucap - khautru
            cursor.execute("""
                INSERT INTO Luong (MaNhanVien, Thang, Nam, LuongCoBan, PhuCap, KhauTru, LuongThucNhan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form['MaNhanVien'],
                request.form['Thang'],
                request.form['Nam'],
                luongcoban,
                phucap,
                khautru,
                luongthucnhan
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Thêm lương thành công!', 'success')
            return redirect(url_for('luong_list'))
        conn.close()
        return render_template('luong_add.html', nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi thêm lương: {str(e)}', 'danger')
        return render_template('luong_add.html', nhanviens=[])

@app.route('/luong/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def edit_luong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            luongcoban = float(request.form['LuongCoBan'])
            phucap = float(request.form['PhuCap'])
            khautru = float(request.form['KhauTru'])
            luongthucnhan = luongcoban + phucap - khautru
            cursor.execute("""
                UPDATE Luong SET MaNhanVien=?, Thang=?, Nam=?, LuongCoBan=?, PhuCap=?, KhauTru=?, LuongThucNhan=? WHERE MaLuong=?
            """, (
                request.form['MaNhanVien'],
                request.form['Thang'],
                request.form['Nam'],
                luongcoban,
                phucap,
                khautru,
                luongthucnhan,
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật lương thành công!', 'success')
            return redirect(url_for('luong_list'))
        else:
            cursor.execute("SELECT MaLuong, MaNhanVien, Thang, Nam, LuongCoBan, PhuCap, KhauTru, LuongThucNhan FROM Luong WHERE MaLuong=?", (id,))
            luong = cursor.fetchone()
            conn.close()
            if not luong:
                from flask import flash
                flash('Không tìm thấy bản ghi lương', 'danger')
                return redirect(url_for('luong_list'))
            return render_template('luong_edit.html', luong=luong, nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('luong_list'))

@app.route('/luong/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin')
def delete_luong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Luong WHERE MaLuong=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa lương thành công!', 'success')
        return redirect(url_for('luong_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa lương: {str(e)}', 'danger')
        return redirect(url_for('luong_list'))

@app.route('/danhgia')
@login_required
def danhgia_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Lấy danh sách nhân viên có đánh giá
        cursor.execute('''
            SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan
            FROM NhanVien nv
            LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
            WHERE EXISTS (SELECT 1 FROM DanhGia dg WHERE dg.MaNhanVien = nv.MaNhanVien)
        ''')
        nhanviens = cursor.fetchall()
        dg_data = []
        for nv in nhanviens:
            ma_nv = nv.MaNhanVien
            # Lấy danh sách đánh giá của nhân viên này
            cursor.execute('''
                SELECT dg.Thang, dg.Nam, dg.DiemSo, dg.NhanXet, dg.XepLoai, dg.MaDanhGia
                FROM DanhGia dg
                WHERE dg.MaNhanVien = ?
                ORDER BY dg.Nam DESC, dg.Thang DESC
            ''', (ma_nv,))
            dg_list = cursor.fetchall()
            dg_data.append({
                'MaNhanVien': ma_nv,
                'HoTen': nv.HoTen,
                'TenPhongBan': nv.TenPhongBan,
                'danhgia_list': dg_list
            })
        conn.close()
        return render_template('danhgia_list.html', nhanviens=dg_data)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('danhgia_list.html', nhanviens=[])

@app.route('/danhgia/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def add_danhgia():
    # Nếu là nhân viên, chỉ cho phép thêm cho chính mình
    if session.get('role_id') == 3:
        # ... kiểm tra và chỉ cho phép MaNhanVien = session['user_id'] hoặc session['username'] ...
        pass
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute('''
                INSERT INTO DanhGia (MaNhanVien, Thang, Nam, DiemSo, NhanXet, XepLoai)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form['MaNhanVien'],
                request.form['Thang'],
                request.form['Nam'],
                request.form['DiemSo'],
                request.form['NhanXet'],
                request.form['XepLoai']
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Thêm đánh giá thành công!', 'success')
            return redirect(url_for('danhgia_list'))
        conn.close()
        return render_template('danhgia_add.html', nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi thêm đánh giá: {str(e)}', 'danger')
        return render_template('danhgia_add.html', nhanviens=[])

@app.route('/danhgia/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def edit_danhgia(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute('''
                UPDATE DanhGia SET MaNhanVien=?, Thang=?, Nam=?, DiemSo=?, NhanXet=?, XepLoai=? WHERE MaDanhGia=?
            ''', (
                request.form['MaNhanVien'],
                request.form['Thang'],
                request.form['Nam'],
                request.form['DiemSo'],
                request.form['NhanXet'],
                request.form['XepLoai'],
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật đánh giá thành công!', 'success')
            return redirect(url_for('danhgia_list'))
        else:
            cursor.execute("SELECT MaDanhGia, MaNhanVien, Thang, Nam, DiemSo, NhanXet, XepLoai FROM DanhGia WHERE MaDanhGia=?", (id,))
            dg = cursor.fetchone()
            conn.close()
            if not dg:
                from flask import flash
                flash('Không tìm thấy bản ghi đánh giá', 'danger')
                return redirect(url_for('danhgia_list'))
            return render_template('danhgia_edit.html', danhgia=dg, nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('danhgia_list'))

@app.route('/danhgia/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def delete_danhgia(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DanhGia WHERE MaDanhGia=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa đánh giá thành công!', 'success')
        return redirect(url_for('danhgia_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa đánh giá: {str(e)}', 'danger')
        return redirect(url_for('danhgia_list'))

@app.route('/hopdong')
@login_required
def hopdong_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Lấy danh sách nhân viên có hợp đồng
        cursor.execute('''
            SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan
            FROM NhanVien nv
            LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
            WHERE EXISTS (SELECT 1 FROM HopDong hd WHERE hd.MaNhanVien = nv.MaNhanVien)
        ''')
        nhanviens = cursor.fetchall()
        hd_data = []
        for nv in nhanviens:
            ma_nv = nv.MaNhanVien
            # Lấy danh sách hợp đồng của nhân viên này
            cursor.execute('''
                SELECT hd.MaHopDong, hd.LoaiHopDong, hd.NgayBatDau, hd.NgayKetThuc, hd.LuongCoBan, hd.PhuCap, hd.TrangThai
                FROM HopDong hd
                WHERE hd.MaNhanVien = ?
                ORDER BY hd.NgayBatDau DESC
            ''', (ma_nv,))
            hd_list = cursor.fetchall()
            hd_data.append({
                'MaNhanVien': ma_nv,
                'HoTen': nv.HoTen,
                'TenPhongBan': nv.TenPhongBan,
                'hopdong_list': hd_list
            })
        conn.close()
        return render_template('hopdong_list.html', nhanviens=hd_data)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('hopdong_list.html', nhanviens=[])

@app.route('/hopdong/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def add_hopdong():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute('''
                INSERT INTO HopDong (MaNhanVien, LoaiHopDong, NgayBatDau, NgayKetThuc, LuongCoBan, PhuCap, TrangThai)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['MaNhanVien'],
                request.form['LoaiHopDong'],
                request.form['NgayBatDau'],
                request.form['NgayKetThuc'],
                request.form['LuongCoBan'],
                request.form['PhuCap'],
                request.form['TrangThai']
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Thêm hợp đồng thành công!', 'success')
            return redirect(url_for('hopdong_list'))
        conn.close()
        return render_template('hopdong_add.html', nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi thêm hợp đồng: {str(e)}', 'danger')
        return render_template('hopdong_add.html', nhanviens=[])

@app.route('/hopdong/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin')
def edit_hopdong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute('''
                UPDATE HopDong SET MaNhanVien=?, LoaiHopDong=?, NgayBatDau=?, NgayKetThuc=?, LuongCoBan=?, PhuCap=?, TrangThai=? WHERE MaHopDong=?
            ''', (
                request.form['MaNhanVien'],
                request.form['LoaiHopDong'],
                request.form['NgayBatDau'],
                request.form['NgayKetThuc'],
                request.form['LuongCoBan'],
                request.form['PhuCap'],
                request.form['TrangThai'],
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật hợp đồng thành công!', 'success')
            return redirect(url_for('hopdong_list'))
        else:
            cursor.execute("SELECT MaHopDong, MaNhanVien, LoaiHopDong, NgayBatDau, NgayKetThuc, LuongCoBan, PhuCap, TrangThai FROM HopDong WHERE MaHopDong=?", (id,))
            hd = cursor.fetchone()
            conn.close()
            if not hd:
                from flask import flash
                flash('Không tìm thấy bản ghi hợp đồng', 'danger')
                return redirect(url_for('hopdong_list'))
            return render_template('hopdong_edit.html', hopdong=hd, nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('hopdong_list'))

@app.route('/hopdong/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin')
def delete_hopdong(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM HopDong WHERE MaHopDong=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa hợp đồng thành công!', 'success')
        return redirect(url_for('hopdong_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa hợp đồng: {str(e)}', 'danger')
        return redirect(url_for('hopdong_list'))

@app.route('/donnghiphep')
@login_required
def donnghiphep_list():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        # Lấy danh sách nhân viên có đơn nghỉ phép
        cursor.execute('''
            SELECT nv.MaNhanVien, nv.HoTen, pb.TenPhongBan
            FROM NhanVien nv
            LEFT JOIN PhongBan pb ON nv.MaPhongBan = pb.MaPhongBan
            WHERE EXISTS (SELECT 1 FROM DonNghiPhep dnp WHERE dnp.MaNhanVien = nv.MaNhanVien)
        ''')
        nhanviens = cursor.fetchall()
        dnp_data = []
        for nv in nhanviens:
            ma_nv = nv.MaNhanVien
            # Lấy danh sách đơn nghỉ phép của nhân viên này
            cursor.execute('''
                SELECT dnp.MaDon, dnp.NgayBatDau, dnp.NgayKetThuc, dnp.LyDo, dnp.TrangThai
                FROM DonNghiPhep dnp
                WHERE dnp.MaNhanVien = ?
                ORDER BY dnp.NgayBatDau DESC
            ''', (ma_nv,))
            dnp_list = cursor.fetchall()
            dnp_data.append({
                'MaNhanVien': ma_nv,
                'HoTen': nv.HoTen,
                'TenPhongBan': nv.TenPhongBan,
                'donnghiphep_list': dnp_list
            })
        conn.close()
        return render_template('donnghiphep_list.html', nhanviens=dnp_data)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('donnghiphep_list.html', nhanviens=[])

@app.route('/donnghiphep/add', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong', 'NhanVien')
def add_donnghiphep():
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            # Nếu là nhân viên, chỉ cho phép tạo cho chính mình và trạng thái luôn là 'Chờ duyệt'
            ma_nv = request.form['MaNhanVien']
            if session.get('role_id') == 3:
                ma_nv = session.get('ma_nhanvien')
            cursor.execute('''
                INSERT INTO DonNghiPhep (MaNhanVien, NgayBatDau, NgayKetThuc, LyDo, TrangThai)
                VALUES (?, ?, ?, ?, N'Chờ duyệt')
            ''', (
                ma_nv,
                request.form['NgayBatDau'],
                request.form['NgayKetThuc'],
                request.form['LyDo']
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Thêm đơn nghỉ phép thành công!', 'success')
            return redirect(url_for('donnghiphep_list'))
        conn.close()
        return render_template('donnghiphep_add.html', nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi thêm đơn nghỉ phép: {str(e)}', 'danger')
        return render_template('donnghiphep_add.html', nhanviens=[])

@app.route('/donnghiphep/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_roles('Admin', 'TruongPhong')
def edit_donnghiphep(id):
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM NhanVien")
        nhanviens = cursor.fetchall()
        if request.method == 'POST':
            cursor.execute('''
                UPDATE DonNghiPhep SET MaNhanVien=?, NgayBatDau=?, NgayKetThuc=?, LyDo=?, TrangThai=? WHERE MaDon=?
            ''', (
                request.form['MaNhanVien'],
                request.form['NgayBatDau'],
                request.form['NgayKetThuc'],
                request.form['LyDo'],
                request.form['TrangThai'],
                id
            ))
            conn.commit()
            conn.close()
            from flask import flash
            flash('Cập nhật đơn nghỉ phép thành công!', 'success')
            return redirect(url_for('donnghiphep_list'))
        else:
            cursor.execute("SELECT MaDon, MaNhanVien, NgayBatDau, NgayKetThuc, LyDo, TrangThai FROM DonNghiPhep WHERE MaDon=?", (id,))
            dnp = cursor.fetchone()
            conn.close()
            if not dnp:
                from flask import flash
                flash('Không tìm thấy bản ghi đơn nghỉ phép', 'danger')
                return redirect(url_for('donnghiphep_list'))
            return render_template('donnghiphep_edit.html', donnghiphep=dnp, nhanviens=nhanviens)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return redirect(url_for('donnghiphep_list'))

@app.route('/donnghiphep/delete/<int:id>', methods=['POST'])
@login_required
@require_roles('Admin', 'TruongPhong', 'NhanVien')
def delete_donnghiphep(id):
    # Nếu là nhân viên, chỉ cho phép xóa đơn của mình
    if session.get('role_id') == 3:
        # ... kiểm tra quyền sở hữu đơn ...
        pass
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DonNghiPhep WHERE MaDon=?", (id,))
        conn.commit()
        conn.close()
        from flask import flash
        flash('Xóa đơn nghỉ phép thành công!', 'success')
        return redirect(url_for('donnghiphep_list'))
    except Exception as e:
        from flask import flash
        flash(f'Lỗi xóa đơn nghỉ phép: {str(e)}', 'danger')
        return redirect(url_for('donnghiphep_list'))

@app.route('/baocao')
@login_required
def baocao():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Tổng số nhân viên
        cursor.execute("SELECT COUNT(*) FROM NhanVien")
        tong_nv = cursor.fetchone()[0]
        # Tổng số phòng ban
        cursor.execute("SELECT COUNT(*) FROM PhongBan")
        tong_pb = cursor.fetchone()[0]
        # Tổng lương đã trả
        cursor.execute("SELECT SUM(LuongThucNhan) FROM Luong")
        tong_luong = cursor.fetchone()[0] or 0
        # Tổng số ngày công (số bản ghi chấm công)
        cursor.execute("SELECT COUNT(*) FROM ChamCong")
        tong_chamcong = cursor.fetchone()[0]
        # Tổng số đơn nghỉ phép
        cursor.execute("SELECT COUNT(*) FROM DonNghiPhep")
        tong_donnghiphep = cursor.fetchone()[0]
        # Tổng số hợp đồng
        cursor.execute("SELECT COUNT(*) FROM HopDong")
        tong_hopdong = cursor.fetchone()[0]
        conn.close()
        return render_template('baocao.html', tong_nv=tong_nv, tong_pb=tong_pb, tong_luong=tong_luong, tong_chamcong=tong_chamcong, tong_donnghiphep=tong_donnghiphep, tong_hopdong=tong_hopdong)
    except Exception as e:
        from flask import flash
        flash(f'Lỗi: {str(e)}', 'danger')
        return render_template('baocao.html', tong_nv=0, tong_pb=0, tong_luong=0, tong_chamcong=0, tong_donnghiphep=0, tong_hopdong=0)

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất!', 'success')
    return redirect(url_for('api.login'))

if __name__ == '__main__':
    app.run(debug=True) 
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from models import NhanVien, PhongBan, ChamCong
from datetime import datetime
from werkzeug.security import check_password_hash
import pyodbc
from config import CONNECTION_STRING

api = Blueprint('api', __name__)

# NhanVien routes
@api.route('/nhanvien')
def nhanvien_list():
    try:
        nhanviens = NhanVien.get_all()
        # Get department names for each employee
        phongbans = {pb.MaPhongBan: pb.TenPhongBan for pb in PhongBan.get_all()}
        for nv in nhanviens:
            nv.TenPhongBan = phongbans.get(nv.MaPhongBan, '')
        return render_template('nhanvien_list.html', nhanviens=nhanviens)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('index'))

@api.route('/nhanvien/add', methods=['GET', 'POST'])
def add_nhanvien():
    if request.method == 'POST':
        try:
            data = request.form
            nhanvien = NhanVien(
                HoTen=data.get('HoTen'),
                NgaySinh=datetime.strptime(data.get('NgaySinh'), '%Y-%m-%d') if data.get('NgaySinh') else None,
                GioiTinh=data.get('GioiTinh'),
                DiaChi=data.get('DiaChi'),
                SoDienThoai=data.get('SoDienThoai'),
                Email=data.get('Email'),
                MaPhongBan=data.get('MaPhongBan'),
                ChucVu=data.get('ChucVu'),
                NgayVaoLam=datetime.strptime(data.get('NgayVaoLam'), '%Y-%m-%d') if data.get('NgayVaoLam') else None
            )
            nhanvien.create()
            flash('Thêm nhân viên thành công!', 'success')
            return redirect(url_for('api.nhanvien_list'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('api.add_nhanvien'))
    
    try:
        phongbans = PhongBan.get_all()
        return render_template('nhanvien_add.html', phongbans=phongbans)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('api.nhanvien_list'))

@api.route('/nhanvien/<int:id>/edit', methods=['GET', 'POST'])
def edit_nhanvien(id):
    try:
        nhanvien = NhanVien.get_by_id(id)
        if not nhanvien:
            flash('Không tìm thấy nhân viên!', 'danger')
            return redirect(url_for('api.nhanvien_list'))

        if request.method == 'POST':
            data = request.form
            nhanvien.HoTen = data.get('HoTen')
            nhanvien.NgaySinh = datetime.strptime(data.get('NgaySinh'), '%Y-%m-%d') if data.get('NgaySinh') else None
            nhanvien.GioiTinh = data.get('GioiTinh')
            nhanvien.DiaChi = data.get('DiaChi')
            nhanvien.SoDienThoai = data.get('SoDienThoai')
            nhanvien.Email = data.get('Email')
            nhanvien.MaPhongBan = data.get('MaPhongBan')
            nhanvien.ChucVu = data.get('ChucVu')
            nhanvien.NgayVaoLam = datetime.strptime(data.get('NgayVaoLam'), '%Y-%m-%d') if data.get('NgayVaoLam') else None
            
            nhanvien.update()
            flash('Cập nhật nhân viên thành công!', 'success')
            return redirect(url_for('api.nhanvien_list'))

        phongbans = PhongBan.get_all()
        return render_template('nhanvien_edit.html', nhanvien=nhanvien, phongbans=phongbans)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('api.nhanvien_list'))

@api.route('/nhanvien/<int:id>/delete', methods=['POST'])
def delete_nhanvien(id):
    try:
        nhanvien = NhanVien.get_by_id(id)
        if not nhanvien:
            flash('Không tìm thấy nhân viên!', 'danger')
            return redirect(url_for('nhanvien_list'))
        
        NhanVien.delete(id)
        flash('Xóa nhân viên thành công!', 'success')
        return redirect(url_for('nhanvien_list'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('nhanvien_list'))

# PhongBan routes
@api.route('/phongban', methods=['GET'])
def get_phongban_list():
    phongban_list = PhongBan.get_all()
    return jsonify([{
        'MaPhongBan': pb.MaPhongBan,
        'TenPhongBan': pb.TenPhongBan,
        'MoTa': pb.MoTa,
        'TruongPhong': pb.TruongPhong
    } for pb in phongban_list])

@api.route('/phongban/<int:id>', methods=['GET'])
def get_phongban(id):
    phongban = PhongBan.get_by_id(id)
    if phongban:
        return jsonify({
            'MaPhongBan': phongban.MaPhongBan,
            'TenPhongBan': phongban.TenPhongBan,
            'MoTa': phongban.MoTa,
            'TruongPhong': phongban.TruongPhong
        })
    return jsonify({'error': 'Phòng ban không tồn tại'}), 404

@api.route('/phongban', methods=['POST'])
def create_phongban():
    data = request.get_json()
    phongban = PhongBan(
        TenPhongBan=data.get('TenPhongBan'),
        MoTa=data.get('MoTa'),
        TruongPhong=data.get('TruongPhong')
    )
    phongban = phongban.create()
    return jsonify({
        'MaPhongBan': phongban.MaPhongBan,
        'TenPhongBan': phongban.TenPhongBan,
        'MoTa': phongban.MoTa,
        'TruongPhong': phongban.TruongPhong
    }), 201

@api.route('/phongban/<int:id>', methods=['PUT'])
def update_phongban(id):
    phongban = PhongBan.get_by_id(id)
    if not phongban:
        return jsonify({'error': 'Phòng ban không tồn tại'}), 404
    
    data = request.get_json()
    phongban.TenPhongBan = data.get('TenPhongBan', phongban.TenPhongBan)
    phongban.MoTa = data.get('MoTa', phongban.MoTa)
    phongban.TruongPhong = data.get('TruongPhong', phongban.TruongPhong)
    
    phongban = phongban.update()
    return jsonify({
        'MaPhongBan': phongban.MaPhongBan,
        'TenPhongBan': phongban.TenPhongBan,
        'MoTa': phongban.MoTa,
        'TruongPhong': phongban.TruongPhong
    })

@api.route('/phongban/<int:id>', methods=['DELETE'])
def delete_phongban(id):
    phongban = PhongBan.get_by_id(id)
    if not phongban:
        return jsonify({'error': 'Phòng ban không tồn tại'}), 404
    
    PhongBan.delete(id)
    return jsonify({'message': 'Xóa phòng ban thành công'})

# ChamCong routes
@api.route('/chamcong', methods=['GET'])
def get_chamcong_list():
    chamcong_list = ChamCong.get_all()
    return jsonify([{
        'MaChamCong': cc.MaChamCong,
        'MaNhanVien': cc.MaNhanVien,
        'Ngay': cc.Ngay.strftime('%Y-%m-%d') if cc.Ngay else None,
        'GioVao': cc.GioVao.strftime('%H:%M:%S') if cc.GioVao else None,
        'GioRa': cc.GioRa.strftime('%H:%M:%S') if cc.GioRa else None
    } for cc in chamcong_list])

@api.route('/chamcong/<int:id>', methods=['GET'])
def get_chamcong(id):
    chamcong = ChamCong.get_by_id(id)
    if chamcong:
        return jsonify({
            'MaChamCong': chamcong.MaChamCong,
            'MaNhanVien': chamcong.MaNhanVien,
            'Ngay': chamcong.Ngay.strftime('%Y-%m-%d') if chamcong.Ngay else None,
            'GioVao': chamcong.GioVao.strftime('%H:%M:%S') if chamcong.GioVao else None,
            'GioRa': chamcong.GioRa.strftime('%H:%M:%S') if chamcong.GioRa else None
        })
    return jsonify({'error': 'Chấm công không tồn tại'}), 404

@api.route('/chamcong', methods=['POST'])
def create_chamcong():
    data = request.get_json()
    chamcong = ChamCong(
        MaNhanVien=data.get('MaNhanVien'),
        Ngay=datetime.strptime(data.get('Ngay'), '%Y-%m-%d') if data.get('Ngay') else None,
        GioVao=datetime.strptime(data.get('GioVao'), '%H:%M:%S').time() if data.get('GioVao') else None,
        GioRa=datetime.strptime(data.get('GioRa'), '%H:%M:%S').time() if data.get('GioRa') else None
    )
    chamcong = chamcong.create()
    return jsonify({
        'MaChamCong': chamcong.MaChamCong,
        'MaNhanVien': chamcong.MaNhanVien,
        'Ngay': chamcong.Ngay.strftime('%Y-%m-%d') if chamcong.Ngay else None,
        'GioVao': chamcong.GioVao.strftime('%H:%M:%S') if chamcong.GioVao else None,
        'GioRa': chamcong.GioRa.strftime('%H:%M:%S') if chamcong.GioRa else None
    }), 201

@api.route('/chamcong/<int:id>', methods=['PUT'])
def update_chamcong(id):
    chamcong = ChamCong.get_by_id(id)
    if not chamcong:
        return jsonify({'error': 'Chấm công không tồn tại'}), 404
    
    data = request.get_json()
    chamcong.MaNhanVien = data.get('MaNhanVien', chamcong.MaNhanVien)
    chamcong.Ngay = datetime.strptime(data.get('Ngay'), '%Y-%m-%d') if data.get('Ngay') else chamcong.Ngay
    chamcong.GioVao = datetime.strptime(data.get('GioVao'), '%H:%M:%S').time() if data.get('GioVao') else chamcong.GioVao
    chamcong.GioRa = datetime.strptime(data.get('GioRa'), '%H:%M:%S').time() if data.get('GioRa') else chamcong.GioRa
    
    chamcong = chamcong.update()
    return jsonify({
        'MaChamCong': chamcong.MaChamCong,
        'MaNhanVien': chamcong.MaNhanVien,
        'Ngay': chamcong.Ngay.strftime('%Y-%m-%d') if chamcong.Ngay else None,
        'GioVao': chamcong.GioVao.strftime('%H:%M:%S') if chamcong.GioVao else None,
        'GioRa': chamcong.GioRa.strftime('%H:%M:%S') if chamcong.GioRa else None
    })

@api.route('/chamcong/<int:id>', methods=['DELETE'])
def delete_chamcong(id):
    chamcong = ChamCong.get_by_id(id)
    if not chamcong:
        return jsonify({'error': 'Chấm công không tồn tại'}), 404
    
    ChamCong.delete(id)
    return jsonify({'message': 'Xóa chấm công thành công'})

@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            conn = pyodbc.connect(CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, Username, PasswordHash, RoleID, MaNhanVien FROM [User] WHERE Username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            if user and user.PasswordHash == password:
                session['user_id'] = user.UserID
                session['username'] = user.Username
                session['role_id'] = user.RoleID
                session['ma_nhanvien'] = user.MaNhanVien
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
        except Exception as e:
            flash(f'Lỗi đăng nhập: {str(e)}', 'danger')
    return render_template('login.html')

@api.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất!', 'success')
    return redirect(url_for('api.login')) 
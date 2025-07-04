CREATE DATABASE qlns; 
USE qlns; 

-- Bảng NhanVien
CREATE TABLE NhanVien (
    MaNhanVien INT PRIMARY KEY IDENTITY(1,1),
    HoTen NVARCHAR(100) NOT NULL,
    NgaySinh DATE,
    GioiTinh VARCHAR(10),
    DiaChi NVARCHAR(255),
    SoDienThoai VARCHAR(20),
    Email NVARCHAR(100),
    MaPhongBan INT,
    ChucVu NVARCHAR(50),
    NgayVaoLam DATE
);

-- Bảng PhongBan
CREATE TABLE PhongBan (
    MaPhongBan INT PRIMARY KEY IDENTITY(1,1),
    TenPhongBan NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(255),
    TruongPhong INT,
    FOREIGN KEY (TruongPhong) REFERENCES NhanVien(MaNhanVien)
);

-- Bổ sung khóa ngoại từ NhanVien đến PhongBan
ALTER TABLE NhanVien
ADD FOREIGN KEY (MaPhongBan) REFERENCES PhongBan(MaPhongBan);

-- Bảng ChamCong
CREATE TABLE ChamCong (
    MaChamCong INT PRIMARY KEY IDENTITY(1,1),
    MaNhanVien INT,
    Ngay DATE,
    GioVao TIME,
    GioRa TIME,
    TrangThai NVARCHAR(50) NULL,
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);

-- Bảng Luong
CREATE TABLE Luong (
    MaLuong INT PRIMARY KEY IDENTITY(1,1),
    MaNhanVien INT,
    Thang INT,
    Nam INT,
    LuongCoBan DECIMAL(10,2),
    PhuCap DECIMAL(10,2),
    KhauTru DECIMAL(10,2),
    LuongThucNhan DECIMAL(10,2),
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);

-- Bảng DanhGia
CREATE TABLE DanhGia (
    MaDanhGia INT PRIMARY KEY IDENTITY(1,1),
    MaNhanVien INT,
    KyDanhGia VARCHAR(20),
    DiemSo INT,
    NhanXet NVARCHAR(255),
    Thang INT,
    Nam INT,
    XepLoai NVARCHAR(10),
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);

-- Bảng HopDong
CREATE TABLE HopDong (
    MaHopDong INT IDENTITY(1,1) PRIMARY KEY,
    MaNhanVien INT NOT NULL,
    LoaiHopDong NVARCHAR(100),
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE,
    LuongCoBan DECIMAL(10,2),
    PhuCap DECIMAL(10,2),
    TrangThai NVARCHAR(50) DEFAULT 'Đang hiệu lực',
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);

-- Bảng DonNghiPhep
CREATE TABLE DonNghiPhep (
    MaDon INT IDENTITY(1,1) PRIMARY KEY,
    MaNhanVien INT NOT NULL,
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE NOT NULL,
    LyDo NVARCHAR(255),
    TrangThai NVARCHAR(50) DEFAULT 'Chờ duyệt',
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);

-- Bảng Role (Quyền)
CREATE TABLE Role (
    RoleID INT PRIMARY KEY IDENTITY(1,1),
    RoleName NVARCHAR(50) NOT NULL -- (Admin, TruongPhong, NhanVien)
);

-- Bảng User (Tài khoản đăng nhập)
CREATE TABLE [User] (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(50) NOT NULL UNIQUE,
    Email NVARCHAR(100),
    PasswordHash NVARCHAR(255) NOT NULL,
    MaNhanVien INT, -- Liên kết với nhân viên (nếu có)
    RoleID INT NOT NULL,
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien),
    FOREIGN KEY (RoleID) REFERENCES Role(RoleID)
);

-- Chèn dữ liệu vào PhongBan
INSERT INTO PhongBan (TenPhongBan, MoTa, TruongPhong)
VALUES 
(N'Phòng Kỹ Thuật', N'Quản lý kỹ thuật', NULL),
(N'Phòng Nhân Sự', N'Quản lý nhân sự', NULL),
(N'Phòng Kinh Doanh', N'Phát triển kinh doanh', NULL);

-- Chèn dữ liệu vào NhanVien
INSERT INTO NhanVien (HoTen, NgaySinh, GioiTinh, DiaChi, SoDienThoai, Email, MaPhongBan, ChucVu, NgayVaoLam)
VALUES 
(N'Nguyễn Văn A', '1985-05-15', N'Nam', N'123 Đường ABC, Quận XYZ', '0987654321', 'nguyenvana@example.com', 1, N'Trưởng phòng', '2021-01-01'),
(N'Lê Thị C', '1988-03-22', N'Nữ', N'789 Đường GHI, Quận DEF', '0912345678', 'lethic@example.com', 2, N'Trưởng phòng', '2020-06-10'),
(N'Trần Thị B', '1990-07-20', N'Nữ', N'456 Đường DEF, Quận ABC', '0976543210', 'tranthib@example.com', 1, N'Nhân viên', '2021-02-15'),
(N'Phạm Quốc Dũng', '1995-12-01', N'Nam', N'321 Đường XYZ, Quận GHI', '0901234567', 'phamquocdung@example.com', 2, N'Nhân viên', '2022-03-05');

-- Thêm các quyền cơ bản
INSERT INTO Role (RoleName) VALUES (N'Admin'), (N'TruongPhong'), (N'NhanVien');

-- Thêm tài khoản admin mẫu (không gắn MaNhanVien)
INSERT INTO [User] (Username, Email, PasswordHash, RoleID) VALUES 
('admin', 'admin@example.com', 'admin123', 1);

-- Thêm tài khoản trưởng phòng (MaNhanVien = 1, 2)
INSERT INTO [User] (Username, Email, PasswordHash, MaNhanVien, RoleID) VALUES
('NguyenVanA', 'nguyenvana@example.com', 'NguyenVanA123', 1, 2),
('LeThiC', 'lethic@example.com', 'LeThiC123', 2, 2);

-- Thêm tài khoản nhân viên (MaNhanVien = 3, 4)
INSERT INTO [User] (Username, Email, PasswordHash, MaNhanVien, RoleID) VALUES
('TranThiB', 'tranthib@example.com', 'TranThiB123', 3, 3),
('PhamQuocDung', 'phamquocdung@example.com', 'PhamQuocDung123', 4, 3);

-- Chèn dữ liệu vào ChamCong
INSERT INTO ChamCong (MaNhanVien, Ngay, GioVao, GioRa)
VALUES 
(1, '2023-11-01', '08:00:00', '17:00:00'),
(2, '2023-11-01', '08:30:00', '17:30:00');

-- Chèn dữ liệu vào Luong
INSERT INTO Luong (MaNhanVien, Thang, Nam, LuongCoBan, PhuCap, KhauTru, LuongThucNhan)
VALUES 
(1, 11, 2023, 10000000, 2000000, 500000, 11500000),
(2, 11, 2023, 9000000, 1500000, 400000, 10100000);

-- Chèn dữ liệu vào DanhGia
INSERT INTO DanhGia (MaNhanVien, KyDanhGia, DiemSo, NhanXet)
VALUES 
(1, N'Quý 4 2023', 90, N'Hoàn thành tốt công việc'),
(2, N'Quý 4 2023', 85, N'Năng động, tích cực');

-- Chèn dữ liệu vào HopDong
INSERT INTO HopDong (MaNhanVien, LoaiHopDong, NgayBatDau, NgayKetThuc, LuongCoBan, PhuCap, TrangThai)
VALUES 
(1, N'Hợp đồng lao động 1 năm', '2024-01-01', '2024-12-31', 10000000, 2000000, N'Đang hiệu lực'),
(2, N'Hợp đồng thử việc', '2024-02-01', '2024-04-30', 7000000, 1000000, N'Đang hiệu lực');

-- Chèn dữ liệu vào DonNghiPhep
INSERT INTO DonNghiPhep (MaNhanVien, NgayBatDau, NgayKetThuc, LyDo, TrangThai)
VALUES 
(1, '2024-03-10', '2024-03-12', N'Nghỉ ốm', N'Đã duyệt'),
(2, '2024-04-15', '2024-04-20', N'Về quê có việc gia đình', N'Chờ duyệt');

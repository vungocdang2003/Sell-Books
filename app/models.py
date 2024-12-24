import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
import enum


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykhoitao = Column(DateTime,default=datetime.now())


class LoaiTaiKhoan(enum.Enum):
    ADMIN = 1
    NHANVIEN = 2
    KHACHHANG = 3


class GioiTinh(enum.Enum):
    Nam = 0
    Nu = 1


class TaiKhoan(db.Model, UserMixin):
    __abstract__ = True
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(200), default=None)
    user_role = Column(Enum(LoaiTaiKhoan))

    def __str__(self):
        return self.username


class TaiKhoanKhachHang(TaiKhoan):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    giohang = relationship("GioHang", back_populates="taikhoankhachhang",uselist=False)
    binhluan = relationship("BinhLuan", backref="taikhoankhachhang1", lazy=True)

    def __str__(self):
        return self.name


class DiaChi(BaseModel):
    diachi = Column(String(100), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", backref="diachi", lazy=True)


class SDT(BaseModel):
    sdt = Column(String(12), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", backref="sdt")
    hoadon = relationship("HoaDon", backref="sdt", lazy=True)


class GioHang(db.Model):
    id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), primary_key=True)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", back_populates="giohang", uselist= False)
    ngaykhoitao = Column(DateTime, default=datetime.now())


class NhanVien(BaseModel):
    cccd = Column(String(20), nullable=False, unique=True)
    hoten = Column(String(50), nullable=False)
    gioitinh = Column(Enum(GioiTinh), nullable=False)
    taikhoannhanvien = relationship("TaiKhoanNhanVien", back_populates="nhanvien", uselist=False)

    def __str__(self):
        return self.hoten


class TaiKhoanNhanVien(TaiKhoan):
    id = Column(Integer, ForeignKey('nhan_vien.id'), primary_key=True)
    nhanvien = relationship("NhanVien", back_populates="taikhoannhanvien", uselist=False)

    def __str__(self):
        return self.name


class TheLoai(BaseModel):
    tentheloai = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.tentheloai


class TacGia(BaseModel):
    tentacgia = Column(String(100), nullable=False, unique=True)
    def __str__(self):
        return self.tentacgia


class NhaXuatBan(BaseModel):
    tennxb = Column(String(100), nullable=False, unique=True)
    def __str__(self):
        return self.tennxb


class SanPham(db.Model):
    id = Column(String(20),primary_key=True, nullable=False)
    tensanpham = Column(String(100), nullable=False, unique=True)
    tacgia_id = Column(Integer, ForeignKey(TacGia.id), nullable=False)
    nhaxuatban_id = Column(Integer, ForeignKey(NhaXuatBan.id), nullable=False)
    gia = Column(Float, default=0)
    anhbia = Column(String(200))
    soluongtonkho = Column(Integer)
    ngayphathanh = Column(DateTime, default=datetime.now(), nullable=False)
    mota = Column(String(200), nullable=False, default="Ko co mo ta")
    binhluan = relationship("BinhLuan", backref="sanpham", lazy=True)
    tacgia = relationship("TacGia", backref="sach1", lazy=True)
    nhaxuatban = relationship("NhaXuatBan", backref="sach2", lazy=True)

    def __str__(self):
        return self.tensanpham


class BinhLuan(BaseModel):
    sanpham_id = Column(String(20),ForeignKey(SanPham.id), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    noidung = Column(String(1000), nullable=False)


class GioHang_SanPham(BaseModel):
    giohang_id = Column(Integer, ForeignKey(GioHang.id), nullable=False)
    sanpham_id = Column(String(20), ForeignKey(SanPham.id), nullable=False)
    soluong = Column(Integer, nullable=False)


class SanPham_TheLoai(BaseModel):
    sanpham_id = Column(String(20), ForeignKey(SanPham.id), nullable=False)
    theloai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    sanpham = relationship("SanPham", backref="sanpham_theloai1", lazy=True)
    theloai = relationship("TheLoai", backref="sanpham_theloai2", lazy=True)


class HoaDon(db.Model):
    id = Column(String(10), primary_key=True, nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=True)
    taikhoannhanvien_id = Column(Integer, ForeignKey(TaiKhoanNhanVien.id), nullable=True)
    diachi_id = Column(Integer, ForeignKey(DiaChi.id), nullable=True)
    sdt_id = Column(Integer, ForeignKey(SDT.id), nullable=True)
    ngaykhoitao = Column(DateTime, default=datetime.now())
    taikhoankhachhang = relationship("TaiKhoanKhachHang", backref="hoadon1", lazy=True)
    taikhoannhanvien = relationship("TaiKhoanNhanVien", backref="hoadon2", lazy=True)
    __table_args__ = (CheckConstraint('taikhoankhachhang_id IS NOT NULL or taikhoannhanvien_id IS NOT NULL'),)
    tongsoluong = Column(Integer, default=0)
    tongtien = Column(Float, default=0)


class ChiTietHoaDon(BaseModel):
    hoadon_id = Column(String(10), ForeignKey(HoaDon.id), nullable=False)
    sanpham_id = Column(String(20), ForeignKey(SanPham.id), nullable=False)
    soluong = Column(Integer, nullable= False)


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()

        # nv1 = NhanVien(cccd='1234567',hoten = 'Vu Ngoc Dang', gioitinh = GioiTinh.Nam)
        # db.session.add(nv1)
        # db.session.commit()

        # tk_admin = TaiKhoanNhanVien(name = "Vu Ngoc Dang", username = "admin", password = str(hashlib.md5('123456789'.encode('utf-8')).hexdigest()), user_role = LoaiTaiKhoan.ADMIN, id=1)
        # db.session.add(tk_admin)
        # db.session.commit()

        # nv2 = NhanVien(cccd='2345678',hoten = 'Nguyen Van B', gioitinh = GioiTinh.Nam)
        # db.session.add(nv2)
        # db.session.commit()
        #
        # tk_nhanvien = TaiKhoanNhanVien(name="Nguyen Van B", username="nv1",
        #                             password=str(hashlib.md5('123456789'.encode('utf-8')).hexdigest()),
        #                             user_role=LoaiTaiKhoan.NHANVIEN, id= 3)
        # db.session.add(tk_nhanvien)
        # db.session.commit()
        #
        # tk_khachhang = TaiKhoanKhachHang(email="ngocdang18062003@gmail.com", name="Vu Ngoc Danggg", username="ngocdang2003",
        #                             password=str(hashlib.md5('ngocdang2003'.encode('utf-8')).hexdigest()),
        #                             user_role=LoaiTaiKhoan.KHACHHANG)
        # db.session.add(tk_khachhang)
        # db.session.commit()

        # sanpham1 = SanPham(id = 'MG123', tensanpham ='Tham tu lung danh Conan', gia=100000, soluongtonkho=100)
        # db.session.add(sanpham1)
        # db.session.commit()
        #
        # nxb1 = NhaXuatBan(tennxb='Kim Dong')
        # tg1 = TacGia(tentacgia='Yaoyama Goso')
        # db.session.add_all([nxb1, tg1])
        # db.session.commit()

        pass
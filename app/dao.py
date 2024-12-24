from flask import session

from app.models import GioHang, SanPham, TheLoai, SanPham_TheLoai, TaiKhoanKhachHang, LoaiTaiKhoan, TheLoai, TaiKhoanNhanVien, \
    GioHang_SanPham, HoaDon, DiaChi, SDT, ChiTietHoaDon, TacGia, NhaXuatBan, BinhLuan
from app import app, db, utils
from sqlalchemy import func
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash


def get_sach(kw = None, theloai_id = None, page = None, page_size = None, min_price = None, max_price = None, order = None):
    sachs = SanPham.query
    if kw:
        sachs = sachs.filter(SanPham.tensanpham.contains(kw))
    if theloai_id:
        sachs = sachs.filter(SanPham.id.__eq__(SanPham_TheLoai.id)).filter(SanPham_TheLoai.theloai_id.__eq__(theloai_id))
    if max_price:
        sachs = sachs.filter(SanPham.gia <= max_price)
    if min_price:
        sachs = sachs.filter(SanPham.gia >= min_price)
    if order and order == 'best-sell':
        sachs = sachs.outerjoin(ChiTietHoaDon, ChiTietHoaDon.sanpham_id.__eq__(SanPham.id)).group_by(SanPham.id).order_by(func.sum(ChiTietHoaDon.soluong).desc())
    elif order == 'title-asc':
        sachs = sachs.order_by(SanPham.tensanpham.asc())
    elif order == 'title-desc':
        sachs = sachs.order_by(SanPham.tensanpham.desc())
    elif order == 'price-asc':
        sachs = sachs.order_by(SanPham.gia.asc())
    elif order == 'price-desc':
        sachs = sachs.order_by(SanPham.gia.desc())
    elif order == 'date-asc':
        sachs = sachs.order_by(SanPham.ngayphathanh.asc())
    elif order == 'date-desc':
        sachs = sachs.order_by(SanPham.ngayphathanh.desc())
    if page:
        page = int(page)
        if page_size is None:
            page_size = app.config['PAGE_SIZE']
        start = (page-1)*page_size
        sachs= sachs.slice(start, start+page_size)
    return sachs.all()


def get_so_luong_sach():
    return SanPham.query.count()


def get_so_luong_sach_theo_the_loai():
    return db.session.query(TheLoai.id, TheLoai.tentheloai,
                            func.count(SanPham_TheLoai.sanpham_id)) \
            .join(SanPham_TheLoai,
                            SanPham_TheLoai.theloai_id.__eq__(TheLoai.id), isouter=True) \
            .group_by(TheLoai.id).all()


def get_sach_by_id(sach_id):
    return SanPham.query.get(sach_id)


def get_sach_the_loai():
    return SanPham_TheLoai.query.all()


def get_the_loai_by_sach_id(sach_id):
    sach_theloai = SanPham_TheLoai.query.filter(SanPham_TheLoai.sanpham_id.__eq__(sach_id)).all()
    theloai = []
    for s in sach_theloai:
        theloai.append(TheLoai.query.get(s.theloai_id))
    return theloai


def get_tac_gia_by_id(tacgia_id):
    return TacGia.query.get(tacgia_id)


def get_nha_xuat_ban_by_id(nhaxuatban_id):
    return  NhaXuatBan.query.get(nhaxuatban_id)


def get_tai_khoan_khach_hang_by_id(user_id):
    return  TaiKhoanKhachHang.query.get(user_id)


def get_tai_khoan_khach_hang_by_email(user_email):
    return TaiKhoanKhachHang.query.get(user_email)


def get_so_luong_tai_khoan_khach_hang():
    return TaiKhoanKhachHang.query.count()


def get_tai_khoan_nhan_vien_by_id(user_id):
    return TaiKhoanNhanVien.query.get(user_id)


def auth_user(username, password, loaitaikhoan, email):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    if loaitaikhoan == LoaiTaiKhoan.ADMIN or loaitaikhoan == LoaiTaiKhoan.NHANVIEN:
        user = TaiKhoanNhanVien.query.filter(
            TaiKhoanNhanVien.username.__eq__(username.strip()),
            TaiKhoanNhanVien.password.__eq__(password),
            TaiKhoanNhanVien.user_role.__eq__(loaitaikhoan)
        ).first()

        if user:
            return user
        else:
            return None  # Trả về None nếu không tìm thấy người dùng

    # Xử lý Khách hàng nếu có
    if loaitaikhoan == LoaiTaiKhoan.KHACHHANG:
        taikhoan = TaiKhoanKhachHang.query.filter(
            TaiKhoanKhachHang.email.__eq__(email),
            TaiKhoanKhachHang.password.__eq__(password)
        ).first()

        if taikhoan:
            return taikhoan
        else:
            return None  # Trả về None nếu không tìm thấy người dùng


def add_tai_khoan_khach_hang(name, email, username, password):
    taikhoan = TaiKhoanKhachHang(name= name, email= email, username =username, password= str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()), user_role= LoaiTaiKhoan.KHACHHANG)
    giohang = GioHang(taikhoankhachhang=taikhoan)
    db.session.add(taikhoan)
    db.session.commit()
    db.session.add(giohang)
    db.session.commit()


def doi_mat_khau_khach_hang(email, password):
    taikhoan = get_tai_khoan_khach_hang_by_email(email)
    taikhoan.password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    db.session.commit()


def check_tai_khoan(email, username):
    checkemail = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.email.__eq__(email)).all()
    checkusername = TaiKhoanKhachHang.query.filter(TaiKhoanKhachHang.username.__eq__(username)).all()
    msg = "Tai khoan da ton tai!"
    if checkemail:
        return msg
    if checkusername:
        return msg
    return None


def get_the_loai(id=None):
    if id:
        return TheLoai.query.get(id)
    return TheLoai.query.all()


def get_gio_hang(khachhang_id):
    giohang = GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(khachhang_id)).all()
    gio_hang= {}
    for g in giohang:
        sach = SanPham.query.filter(SanPham.id.__eq__(g.sach.id)).first()
        gio_hang[sach.id] = {
            "sach_id": sach.id,
            "ten sach": sach.tensanpham,
            "gia": sach.gia,
            "so luong": sach.soluong,
            "anh bia": sach.anhbia
        }
        return gio_hang


def get_total_gio_hang(khachhang_id):
    giohang = GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(khachhang_id)).all()
    amount = 0
    quantity = 0
    for g in giohang:
        soluong = g.soluong
        sach = SanPham.query.filter(SanPham.id.__eq__(g.sach.id)).first()
        gia = sach.gia
        amount += gia*soluong
        quantity += soluong
    return {
        "total_amount":amount,
        "total_quantity": quantity
    }


def add_gio_hang(khachhang_id, sanpham_id, soluong = 1):
    giohang = GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(khachhang_id)).filter(GioHang_SanPham.sanpham_id.__eq__(sanpham_id)).first()
    if giohang:
        giohang.soluong += soluong
        db.session.commit()
    else:
        giohang_sanpham = GioHang_SanPham(giohang_id = khachhang_id, sanpham_id= sanpham_id, soluong= soluong)
        db.session.add(giohang_sanpham)
        db.session.commit()


def update_gio_hang(khachhang_id, sanpham_id, soluong):
    giohang = GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(khachhang_id)).filter(GioHang_SanPham.sanpham_id.__eq__(sanpham_id)).first()
    giohang.soluong=soluong
    db.session.commit()


def delete_gio_hang(khachhang_id, sanpham_id):
    giohang = GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(khachhang_id)).filter(GioHang_SanPham.sanpham_id.__eq__(sanpham_id)).first()
    db.session.delete(giohang)
    db.session.commit()


def check_hang_ton_kho(sanpham_id, soluong):
    sach = SanPham.query.get(sanpham_id)
    if sach.soluongtonkho >= soluong:
        return True
    return False


def lap_hoa_don(id, taikhoankhachhang_id = None, taikhoannhanvien_id = None, diachi = None, sdt = None):
    if taikhoannhanvien_id != None:
        giosach = session.get('giosach')
        giohang = utils.count_gio_hang(giosach)
        hoadon = HoaDon(id=id, taikhoannhanvien_id=taikhoannhanvien_id, tongsoluong=giohang['total_quantity'], tongtien= giohang['total_amount'])
        db.session.add(hoadon)
        db.session.commit()
        for g in giosach.values():
            chitiethoadon = ChiTietHoaDon(hoadon_id = id, sanpham_id= g['id'], soluong= g['quantity'])
            sach = SanPham.query.get(g['id'])
            sach.soluongtonkho -= g['quantity']
            db.session.add(chitiethoadon)
            db.session.commit()
        del session['giosach']
        if taikhoankhachhang_id != None and diachi != None and sdt != None:
            giohang = get_total_gio_hang(taikhoankhachhang_id)
            checkdiachi = DiaChi.query.filter(DiaChi.diachi.__eq__(diachi)).filter(DiaChi.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()
            checksdt = SDT.query.filter(SDT.sdt.__eq__(sdt)).filter(SDT.taikhoankhachhang_id.__eq__(taikhoankhachhang_id)).first()

            if checkdiachi is None:
                diachi = DiaChi(diachi=diachi, taikhoankhachhang_id=taikhoankhachhang_id)
                db.session.add(diachi)
            else:
                diachi = checkdiachi
            if checksdt is None:
                sdt = SDT(sdt= sdt, taikhoankhachhang_id=taikhoankhachhang_id)
                db.session.add(sdt)
            else:
                sdt = checksdt
            db.session.commit()

            hoadon = HoaDon(id =id, taikhoankhachhang_id =taikhoankhachhang_id, diachi=diachi, sdt=sdt, tongsoluong = giohang['total_quantity'], tongtien= giohang['total_amount'])
            db.session.add(hoadon)
            db.session.commit()
            gio_hang =GioHang_SanPham.query.filter(GioHang_SanPham.giohang_id.__eq__(taikhoankhachhang_id)).all()
            for g in gio_hang:
                db.session.delete(g)
            db.session.commit()


def check_binh_luan(sanpham_id, khachhang_id):
    hoadon = HoaDon.query.filter(HoaDon.taikhoankhachhang_id.__eq__(khachhang_id)).all()
    for h in hoadon:
        chitiethoadon = ChiTietHoaDon.query.filter(ChiTietHoaDon.hoadon_id.__eq__(h.id)).filter(ChiTietHoaDon.sanpham_id.__eq__(sanpham_id))
        if chitiethoadon:
            return True
        return False


def them_binh_luan(sanpham_id, khachhang_id, binhluan):
    binhluan = BinhLuan(sanpham_id= sanpham_id, taikhoankhachhang_id = khachhang_id, noidung = binhluan)
    db.session.add(binhluan)
    db.session.commit()


def get_binh_luan(sanpham_id, page=None, page_size= None):
    binhluan= BinhLuan.query.filter(BinhLuan.sanpham_id.__eq__(sanpham_id))
    if page:
        page = int(page)
        if page_size is None:
            page_size = app.config['PAGE_SIZE']
        start = (page-1)* page_size
        binhluan = binhluan.slice(start, start+page_size)
    binhluan = binhluan.all()
    binhLuan ={}
    for b in binhluan:
        khachhang = TaiKhoanKhachHang.query.get(b.taikhoankhachhang_id)
        binhLuan[b.id]={
            "ten khach hang": khachhang.name,
            "ngay binh luan": b.ngaykhoitao,
            "noi dung": b.noidung
        }
    return binhLuan


def get_so_sach_da_ban(sanpham_id):
    result = (
        db.session.query(func.sum(ChiTietHoaDon.soluong)).filter(ChiTietHoaDon.sanpham_id==sanpham_id).first()
    )
    if result and result[0] is not None:
        total_quantity = result[0]
    else:
        total_quantity = 0
    return total_quantity


def revenue_stats(kw=None):
    query = db.session.query(SanPham.id, SanPham.tensanpham, func.sum(ChiTietHoaDon.soluong*SanPham.gia)).join(ChiTietHoaDon,ChiTietHoaDon.sanpham_id==SanPham.id)
    if kw:
        query = query.filter(SanPham.tensanpham.contains(kw))

    return query.group_by(SanPham.id).all()


def revenue_mont_stats(year = 2024):
    query = db.session.query(func.extract('year', HoaDon.ngaykhoitao),func.sum(ChiTietHoaDon.soluong*SanPham.gia)).join(ChiTietHoaDon,ChiTietHoaDon.hoadon_id.__eq__(HoaDon.id)).join(SanPham, SanPham.id.__eq__(ChiTietHoaDon.sanpham_id)).group_by(func.extract('year', HoaDon.ngaykhoitao))
    return  query.all()


def get_chi_tiet_hoa_don_by_id(hoadon_id):
    return ChiTietHoaDon.query.filter(ChiTietHoaDon.hoadon_id.__eq__(hoadon_id)).all()


def get_hoa_don_by_id(hoadon_id):
    return HoaDon.query.get(hoadon_id)


def revenue_year_stats():
    query = db.session.query(func.extract('year', HoaDon.ngaykhoitao),func.sum(ChiTietHoaDon.soluong*SanPham.gia)).join(ChiTietHoaDon, ChiTietHoaDon.hoadon_id.__eq__(HoaDon.id)).join(SanPham, SanPham.id.__eq__(ChiTietHoaDon.sanpham_id)).group_by(func.extract('year', HoaDon.ngaykhoitao))
    return  query.all()


if __name__=='__main__':
    with app.app_context():
        pass
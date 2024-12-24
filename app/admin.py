import hashlib

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from app.models import SanPham, TheLoai, SanPham_TheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien, LoaiTaiKhoan
from flask_login import logout_user, current_user
from flask import redirect, request


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.get_so_luong_sach_theo_the_loai())


admin = Admin(app=app, name='QUẢN LÝ NHÀ SÁCH', template_mode='bootstrap4', index_view=MyAdminIndexView())


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_role == LoaiTaiKhoan.NHANVIEN or current_user.user_role == LoaiTaiKhoan.ADMIN)


class AuthenticatedAdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN


class AuthenticatedNhanVienBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.NHANVIEN


class SanPhamView(AuthenticatedAdmin):
    column_display_pk = True
    can_create = True
    column_list = ['id', 'tensanpham', 'gia', 'soluongtonkho', 'nhaxuatban', 'sach_theloai1']
    column_labels = {
        'id': 'ID',
        'tensanpham': 'Tên sách',
        'gia': 'Giá',
        'soluongtonkho': 'Số lượng tồn kho',
        'tacgia': 'Tác giả',
        'sach_theloai1': 'Thể loại',
        'mota': 'Mô tả',
        'ngayphathanh': 'Ngày phát hành',
        'nhaxuatban': 'Nhà xuất bản',
        'anhbia': 'Ảnh bìa'
    }
    can_export = True
    column_searchable_list = ['tensanpham']
    column_filters = ['gia', 'tensanpham']
    column_editable_list = ['id', 'tensanpham', 'gia', 'anhbia', 'soluongtonkho']
    details_modal = True
    edit_modal = True
    form_columns = ['id', 'tensanpham', 'tacgia', 'nhaxuatban', 'ngayphathanh', 'gia', 'anhbia', 'soluongtonkho', 'mota']

    # column_display_pk = True
    # can_create = True
    #
    # # Đảm bảo column_list là list, không phải tuple
    # column_list = ['id', 'tensanpham', 'gia', 'soluongtonkho', 'nhaxuatban', 'sanpham_theloai1']
    #
    # # Đảm bảo column_labels là dictionary, không phải tuple
    # column_labels = {
    #     'id': "ID",
    #     'tensanpham': 'Tên Sách',
    #     'gia': 'Giá',
    #     'soluongtonkho': 'Số Lượng Tồn Kho',
    #     'tacgia': 'Tác Giả',
    #     'sanpham_theloai1': 'Thể Loại',
    #     'mota': 'Mô Tả',
    #     'ngayphathanh': 'Ngày Phát Hành',
    #     'nhaxuatban': 'Nhà Xuất Bản',
    #     'anhbia': 'Ảnh Bìa'
    # }
    #
    # # Kiểm tra lại các cột có thể tìm kiếm và lọc
    # column_searchable_list = ['tensanpham']
    # column_filters = ['gia', 'tensanpham']
    #
    # # Đảm bảo column_editable_list là list
    # column_editable_list = ['id', 'tensanpham', 'gia', 'anhbia', 'soluongtonkho']
    #
    # details_modal = True
    # edit_modal = True
    # form_columns = ['id', 'tensanpham', 'tacgia', 'nhaxuatban', 'ngayphathanh', 'gia', 'anhbia', 'soluongtonkho', 'mota']


class TheLoaiView(AuthenticatedAdmin):
    # column_list phải là một danh sách (list), không phải tuple
    column_list = ['id', 'tentheloai', 'ngaykhoitao']

    # column_labels phải là một dictionary (dict)
    column_labels = {
        'id': 'ID',
        'tentheloai': 'Tên thể loại',
        'ngaykhoitao': 'Ngày khởi tạo'
    }

    # Cho phép xuất dữ liệu
    can_export = True

    # column_searchable_list là danh sách các cột có thể tìm kiếm
    column_searchable_list = ['tentheloai']

    # column_filters là danh sách các cột có thể lọc
    column_filters = ['tentheloai']

    # column_editable_list là danh sách các cột có thể chỉnh sửa
    column_editable_list = ['tentheloai']

    # form_columns là danh sách các trường hiển thị trong form
    form_columns = ['tentheloai', 'ngaykhoitao']

    # Hiển thị modal chi tiết và modal chỉnh sửa
    details_modal = True
    edit_modal = True


class SanPhamTheLoaiView(AuthenticatedAdmin):
    Column_list=['id','sanpham','theloai']
    column_labels={
        'id': 'ID',
        'sanpham_id': 'Sach id',
        'theloai_id': 'The loai id'
    }
    can_export = True


class NhanVienView(AuthenticatedAdmin):
    column_list= ['id', 'cccd', 'hoten','gioitinh', 'taikhoannhanvien']
    form_columns = ['cccd', 'hoten', 'gioitinh']
    column_labels = {
        'id': 'ID',
        'cccd': 'CCCD',
        'hoten': 'Ho ten',
        'gioitinh': 'Gioi tinh',
        'taikhoannhanvien': 'Tai khoan nhan vien'
    }


class LogoutView(AuthenticatedAdminBaseView):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')


class StatsView(AuthenticatedUser):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        year = request.args.get('year')
        if year:
            year = int(year)
        else:
            year= 2024
        return self.render('admin/stats.html', stats = dao.revenue_stats(kw = kw), mont_stats= dao.revenue_mont_stats(year=year), year_stats = dao.revenue_year_stats())


class TaiKhoanNhanVienView(AuthenticatedAdmin):
    form_column = ['nhanvien', 'name', 'username', 'password', 'avatar', 'user_role']
    column_labels= {
        'nhanvien': 'Nhan vien',
        'name': 'Ho ten',
        'username': 'Username',
        'password': 'Password',
        'avatar': 'Avatrar'
    }
    def on_model_change(self, form, model, is_created):
        if 'password' in request.form and request.form['password']:
            model.password = str(hashlib.md5(request.form['password'].encode('utf-8')).hexdigest())


class ReturnView(AuthenticatedNhanVienBaseView):
    @expose('/')
    def returnview(self):
        return redirect('/nhanvien')


admin.add_view(SanPhamView(SanPham, db.session, name= 'San pham'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='The loai'))
admin.add_view(SanPhamTheLoaiView(SanPham_TheLoai, db.session, name= 'Sach_The loai'))
admin.add_view(TaiKhoanNhanVienView(TaiKhoanNhanVien, db.session, name= 'Tai khoan nhan vien'))
admin.add_view(NhanVienView(NhanVien, db.session, name= 'Nhan vien'))
admin.add_view(StatsView(name='Thong ke bao cao'))
admin.add_view(ReturnView(name=' Quay ve'))
admin.add_view(LogoutView(name= 'Dang xuat'))


import math
import random
import string
from datetime import datetime
from flask import redirect, render_template, request, session, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, login, dao, utils, oauth, admin
from app.models import LoaiTaiKhoan


@app.route("/")
def trang_chu():
    kw = request.args.get('kw')
    theloai_id = request.args.get('theloai')
    page = request.args.get('page')
    price_range = request.args.get('price_range')
    order = request.args.get('order')
    if order == 'manual':
        order= None
    min_price = None
    max_price = None
    if price_range:
        price = price_range.split(':')
        min_price= int(price[0])
        max_price = (price[1])
        if max_price == 'max':
            max_price = None
        else:
            max_price = int(max_price)
    sachs = {}
    page_size = app.config['PAGE_SIZE']
    if page is None:
        page = 1
    if kw:
        sach =dao.get_sach(kw=kw, theloai_id=theloai_id, page=page, min_price=min_price, max_price=max_price, order=order)
        num = len(dao.get_sach(kw, theloai_id, min_price, max_price))
        return render_template('timkiem.html', sach=sach, pages= math.ceil(num/page_size), page=page, kw=kw, price_range=price_range, order=order)
    if theloai_id is None:
        theloai = dao.get_the_loai()
        for t in theloai:
            sach = dao.get_sach(kw, t.id, page, 3)
            sachs[t.id] = []
            for s in sach:
                sachs[t.id].append({
                    "id": s.id,
                    "tensach": s.tensanpham,
                    "gia": s.gia,
                    "anhbia": s.anhbia,
                    "soluongtonkho": s.soluongtonkho
                })
        return render_template('index.html', sach= sachs)
    sach = dao.get_sach(kw=kw, theloai_id=theloai_id, page=page, min_price=min_price, max_price=max_price, order=order)
    sachs={}
    sachs[theloai_id]=[]
    for s in sach:
        sachs[theloai_id].append({
            "id": s.id,
            "tensach": s.tensanpham,
            "gia": s.gia,
            "anhbia": s.anhbia,
            "soluongtonkho": s.soluongtonkho
        })
    theloai = dao.get_the_loai(theloai_id)
    num = len(dao.get_sach(kw=None, theloai_id=theloai_id, min_price=min_price, max_price=max_price, order=order))
    return render_template('theloai.html', sach=sachs, t= theloai, pages= math.ceil(num/page_size), page=page, price_range=price_range, order=order)


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.ADMIN, email=None)
    if user:
        login_user(user=user)
        session['user_role'] = 'ADMIN'
    return redirect('/admin')


@app.route('/dangnhap', methods=['get', 'post'])
def dang_nhap():
    msg = request.args.get('msg', '')
    if request.method == "GET":
        if msg != '':
            return render_template('dangnhap.html', msg=msg)
        return render_template('dangnhap.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.args.get('next')
        user = dao.auth_user(username=None, password=password, loaitaikhoan=LoaiTaiKhoan.KHACHHANG, email=email)
        if type(user) is str:
            return render_template('dangnhap.html', msg=user)
        else:
            login_user(user=user)
            session['user_role'] = "KHACHHANG"

            print(next_page)
            if next_page:
                print("hello")
                return redirect(next_page)
            return redirect('/')


@app.route('/dangxuat')
def dang_xuat():
    logout_user()
    del session['user_role']
    return redirect('/')


@app.route('/nhanvien/logout')
def nhan_vien_dang_xuat():
    logout_user()
    del session['user_role']
    if "giosach" in session:
        del session['giosach']
    return redirect('/nhanvien')


@app.route('/dangky', methods =['get','post'])
def dang_ky():
    if request.method == "GET":
        return render_template('dangky.html')
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        msg = dao.check_tai_khoan(email, username)
        if msg:
            return render_template('dangky.html', msg=msg)
        session['name'] = name
        session['email'] = email
        session['password'] = password
        return redirect('/dangnhap')


@app.route('/quenmatkhau', methods = ['get','post'])
def quen_mat_khau():
    msg =request.args.get('msg')
    if request.method == 'POST':
        email = request.form.get('email')
        check = dao.get_tai_khoan_khach_hang_by_email(email)
        if not check:
            return redirect(url_for('quen_mat_khau'), msg='Tai khoan da ton tai')
        session['email'] = email
    doimatkhau = False
    if 'doimatkhau' in session and session['doimatkhau'] is True:
        doimatkhau = True
    return render_template('quenmatkhau.html', doimatkhau=doimatkhau, msg=msg)


@app.route('/doimatkhau', methods = ['post'])
def doi_mat_khau():
    password = request.form.get('password')
    email = session['email']
    dao.doi_mat_khau_khach_hang(email,password)
    del session['doimatkhau']
    return redirect(url_for('dang_nhap', msg= 'Doi mat khau thanh cong'))


@app.route('/api/cart', methods=['post'])
def add_to_cart():
    data = request.json
    sach_id = str(data.get('sach_id'))
    soluong = int(data.get('soluong'))
    khachhang_id = current_user.id
    dao.add_gio_hang(khachhang_id, sach_id, soluong)
    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = dao.get_gio_hang(current_user.id)
    if cart and product_id in cart:
        soluong = request.json.get('soluong')
        dao.update_gio_hang(current_user.id, product_id, soluong)
    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route('/api/cart/<product_id>', methods =['delete'])
def delete_cart(product_id):
    cart = dao.get_total_gio_hang(current_user.id)
    if cart and product_id in cart:
        dao.delete_gio_hang(current_user.id, product_id)
    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route('/giohang')
@login_required
def gio_hang():
    if current_user.user_role == LoaiTaiKhoan.KHACHHANG:
        giohang = dao.get_gio_hang(current_user.id)
        msg = request.args.get('msg')
        soluongtonkho= {}
        for g in giohang.values():
            sach = dao.get_sach_by_id(g['sach_id'])
            soluongtonkho[g['sach_id']] = sach.soluongtonkho
        return render_template('giohang.html', gioHang = giohang, msg=msg, soluongtonkho=soluongtonkho)
    else:
        return "Co loi xay ra"


@app.route('/checkthongtin', methods=['post'])
def check_thong_tin():
    giohang = dao.get_gio_hang(current_user.id)
    for g in giohang.values():
        check = dao.check_hang_ton_kho(g['sach_id'],g['soluong'])
        print(check)
        if check is False:
            msg = "Sach" + str(g['tensanpham'])+ "khong du hang"
            return redirect(url_for("gio_hang", msg=msg))
    sdt = request.form.get('sdt')
    diachi = request.form.get('diachi')
    phuongthucthanhtoan = request.form.get('phuongthucthanhtoan')
    if phuongthucthanhtoan=='tienmat':
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        hoadon_id = str(current_user.id) + random_string
        khachhang = dao.get_tai_khoan_khach_hang_by_id(current_user.id)
        subject = 'Xac nhan thong tin thanh toan'
        msg = ("Don hang"+hoadon_id+'thanh toan thanh cong.\n Don hang se duoc gui den'++str(diachi)+".\n"+"So dien thoai lien lac:"+str(sdt)+".\n"+'Cam on vi da mua hang')
        dao.lap_hoa_don(id = hoadon_id, taikhoankhachhang_id=current_user.id, diachi=diachi, sdt=sdt)
        return redirect(url_for('gio_hang', msg='Dat hang thanh cong'))


@app.route('/sach/<sach_id>')
def chi_tiet_san_pham(sach_id):
    page = request.args.get('page')
    page_size = 5
    if page:
        page=int(page)
    else:
        page=1
    sach = dao.get_sach_by_id(sach_id)
    tacgia = dao.get_tac_gia_by_id(sach.tacgia.id)
    nhaxuatban= dao.get_nha_xuat_ban_by_id(sach.nhaxuatban.id)
    theloai = dao.get_the_loai_by_sach_id(sach_id)
    binhluan = dao.get_binh_luan(sach_id, page=page, page_size=page_size)
    num = len(dao.get_binh_luan(sach_id))
    soluongdaban =dao.get_so_sach_da_ban(sach_id)
    return render_template('chitietsanpham.html', sach=sach, tacgia=tacgia, nhaxuatban=nhaxuatban, theloai=theloai, binhluan=binhluan, pages=math.ceil(num/page_size), page=page, soluongbinhluan =num, soluongdaban=soluongdaban)


@app.route('/api/binhluan', methods =['post'])
@login_required
def them_binh_luan():
    data = request.json
    sach_id =str(data.get('sach_id'))
    khachhang_id = current_user.id
    binhluan = str(data.get('binhluan'))
    check = dao. check_binh_luan(sach_id, khachhang_id)
    if check is None:
        dao.them_binh_luan(sach_id, khachhang_id, binhluan)
    return jsonify(check)


@app.route('/nhanvien')
def nhan_vien():
    msg = request.args.get('msg')
    kw = request.args.get('kw')
    page = request.args.get('page')
    if not page:
        page = 1
    sach = dao.get_sach(kw=kw, page=page, page_size=1)
    pages= len(dao.get_sach(kw=kw))
    giosach = None
    if 'giosach' in session:
        giosach= session.get('giosach')
    return render_template('nhanvien.html', sach=sach, giosachs= giosach, total_gio_sach= utils.count_gio_hang(giosach), page= page, pages=pages, kw=kw, msg=msg)


@app.route('/api/giosach', methods=['post'])
def add_gio_sach():
    data = request.json
    giosach = session.get('giosach')
    if giosach is None:
        giosach={}
    id = str(data.get('id'))
    if id in giosach:
        giosach[id]['quantity'] += 1
    else:
        giosach[id]={
            "id": id,
            "name": data.get('name'),
            "price": data.get('price'),
            "quantity": 1
        }
    session['giosach'] = giosach
    return jsonify(utils.count_gio_hang(giosach))


@app.route('/api/giosach/<product_id>', methods = ['put'])
def update_gio_sach(product_id):
    giosach = session.get('giosach')
    if giosach and product_id in giosach:
        quantity = request.json.get('quantity')
        giosach[product_id]['quantity'] = int(quantity)
    session['giosach'] = giosach
    return jsonify(utils.count_gio_hang(giosach))


@app.route('/api/giosach/<product_id>', methods = ['delete'])
def delete_gio_sach(product_id):
    giosach = session.get('giosach')
    if giosach and product_id in giosach:
        del giosach[product_id]
    session['giosach'] = giosach
    return jsonify(utils.count_gio_hang(giosach))


@login.user_loader
def get_user(user_id):
    user_role = session.get('user_role')
    if user_role == 'ADMIN' or user_role == 'NHANVIEN':
        return dao.get_tai_khoan_nhan_vien_by_id(user_id)
    elif user_role == 'KHACHHANG':
        return dao.get_tai_khoan_khach_hang_by_id(user_id)


@app.context_processor
def total_giohang():
    if current_user.is_authenticated:
        return {
            'theloai': dao.get_the_loai(),
            'giohang': dao.get_total_gio_hang(current_user.id)
        }
    return {
        'theloai': dao.get_the_loai()
    }


@app.route('/nhanvien/login', methods =['post'])
def nhan_vien_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.NHANVIEN, email=None)
    if user:
        login_user(user=user)
        session['user_role'] = 'NHANVIEN'
    return redirect('/nhanvien')


@app.route('/nhanvien/payment', methods =['post'])
def lap_hoa_don():
    giohang = session.get('giosach')
    for g in giohang.values():
        check = dao.check_hang_ton_kho(g['id'], g['quantity'])
        if check is False:
            msg = 'Sach'+ str(g['name']) + 'khong du hang!'
            return redirect(url_for('nhan_vien', msg=msg))
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k= 6))
    hoadon_id = str(current_user.id) + random_string
    nhanvien = dao.get_tai_khoan_nhan_vien_by_id(current_user.id)
    dao.lap_hoa_don(id = hoadon_id, taikhoannhanvien_id= current_user.id)
    session['hoadon_id'] = hoadon_id
    return redirect('/hoadon')


@app.route('/hoadon')
def hoa_don():
    referrer = request.referrer
    if referrer and 'nhanvien' in referrer:
        hoadon = None
        sachs = None
        if 'hoadon_id' in session and session['hoadon_id']:
            hoadon_id = session.get('hoadon_id')
            del session['hoadon_id']
            hoadon = dao.get_hoa_don_by_id(hoadon_id)
            chitiethoadon = dao.get_chi_tiet_hoa_don_by_id(hoadon_id)
            sachs ={}
            for g in chitiethoadon:
                sach = dao.get_sach_by_id(g.sanpham_id)
                sachs[g.id] ={
                    "id": g.sanpham_id,
                    "ten sach": g.tensanpham,
                    "gia": g.gia,
                    "so luong": g.soluong
                }
        return render_template("hoadon.html", hoadon=hoadon, chitiethoadon= sachs)
    else:
        return "Co loi xay ra!"


@app.route('/payment', methods =['GET', 'POST'])
def payment():
    referrer = request.referrer
    if referrer and 'giohang' in referrer:
        id = current_user.id
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        hoadon_id = str(id) +random_string
        return render_template('payment.html', title = 'Thanh toan', hoadon_id = hoadon_id)


if __name__ == '__main__':
    app.run(host='localhost', port= 5000, debug=True)
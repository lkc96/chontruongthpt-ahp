from app import db
from geoalchemy2 import Geometry

class Truong(db.Model):
    __tablename__ = 'truong'

    truong_id = db.Column(db.Integer, primary_key=True)
    ten_truong = db.Column(db.String(100))
    laoi_truong = db.Column(db.String(100))
    quan_huyen_id = db.Column(db.Integer, db.ForeignKey('quan_huyen.gid'))
    dia_chi = db.Column(db.String(100))
    vi_tri_dia_ly = db.Column(Geometry(geometry_type='POINT', srid=4326))

    # Relationships
    chat_luong = db.relationship('ChatLuongGiaoDuc', backref='truong', uselist=False)
    hoat_dong = db.relationship('HoatDongNgoaiKhoa', backref='truong', uselist=False)
    co_so = db.relationship('CoSoVatChat', backref='truong', uselist=False)
    hoc_phi = db.relationship('HocPhi', backref='truong', uselist=False)


class ChatLuongGiaoDuc(db.Model):
    __tablename__ = 'chat_luong_giao_duc'

    chat_luong_giao_duc_id = db.Column(db.Integer, primary_key=True)
    truong_id = db.Column(db.Integer, db.ForeignKey('truong.truong_id'))
    tyle_đh = db.Column(db.Float)
    tyle_đh_ch = db.Column(db.Float)
    tyle_tn = db.Column(db.Float)
    tyle_tn_ch = db.Column(db.Float)
    chuongtrinhgddb = db.Column(db.String(100))
    chuongtrinhgddb_ch = db.Column(db.Float)
    loaihinhdaotao = db.Column(db.String(100))
    loaihinhdaotao_ch = db.Column(db.Float)
    kiemdinhclgd = db.Column(db.String(100))
    kiemdinhclgd_ch = db.Column(db.Float)
    diem_chuan_hoa = db.Column(db.Float)

class HoatDongNgoaiKhoa(db.Model):
    __tablename__ = 'hoat_dong_ngoai_khoa'

    hoat_dong_ngoai_khoa_id = db.Column(db.Integer, primary_key=True)
    truong_id = db.Column(db.Integer, db.ForeignKey('truong.truong_id'))
    hoatdongngoaikhoa = db.Column(db.Boolean)
    hoatdongngoaikhoa_ch = db.Column(db.Float)
    clb = db.Column(db.Boolean)
    clb_ch = db.Column(db.Float)
    diem_chuan_hoa = db.Column(db.Float)


class CoSoVatChat(db.Model):
    __tablename__ = 'co_so_vat_chat'

    co_so_vat_chat_id = db.Column(db.Integer, primary_key=True)
    truong_id = db.Column(db.Integer, db.ForeignKey('truong.truong_id'))
    phonghoc = db.Column(db.String(100))
    phonghoc_ch = db.Column(db.Float)
    thietbicongnghe = db.Column(db.String(100))
    thietbicongnghe_ch = db.Column(db.Float)
    thuvien = db.Column(db.Boolean)
    thuvien_ch = db.Column(db.Float)
    sanchoi = db.Column(db.Boolean)
    sanchoi_ch = db.Column(db.Float)
    xeduaruoc = db.Column(db.Boolean)
    xeduaruoc_ch = db.Column(db.Float)
    diem_chuan_hoa = db.Column(db.Float)

class HocPhi(db.Model):
    __tablename__ = 'hoc_phi'

    hoc_phi_id = db.Column(db.Integer, primary_key=True)
    truong_id = db.Column(db.Integer, db.ForeignKey('truong.truong_id'))
    hoc_phi_chinh = db.Column(db.Integer)
    hoc_phi_ch = db.Column(db.Float)
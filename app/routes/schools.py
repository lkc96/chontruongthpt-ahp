from flask import Blueprint, render_template, jsonify, request
from app.models import Truong, ChatLuongGiaoDuc, CoSoVatChat, HoatDongNgoaiKhoa, HocPhi
from app import db
from fractions import Fraction
import math

bp = Blueprint('schools', __name__)

# Route lấy dữ liệu bảng Truong
@bp.route('/')
def index():
    truongs = Truong.query.all()
    return render_template('index.html', truongs=truongs)

# Route chọn phương án trường THPT
@bp.route('/get_school_info', methods=['POST'])
def get_school_info():
    data = request.get_json()
    if not data or 'truong_ids' not in data:
        return jsonify({"error": "Invalid data"}), 400

    truong_ids = data.get('truong_ids', [])

    truongs = (
        db.session.query(
            Truong.truong_id,
            Truong.ten_truong,
            ChatLuongGiaoDuc.diem_chuan_hoa.label("diem_clgd"),
            CoSoVatChat.diem_chuan_hoa.label("diem_csvc"),
            HoatDongNgoaiKhoa.diem_chuan_hoa.label("diem_hd"),
            HocPhi.hoc_phi_ch.label("diem_hp")
        )
        .join(ChatLuongGiaoDuc, Truong.truong_id == ChatLuongGiaoDuc.truong_id)
        .join(CoSoVatChat, Truong.truong_id == CoSoVatChat.truong_id)
        .join(HoatDongNgoaiKhoa, Truong.truong_id == HoatDongNgoaiKhoa.truong_id)
        .join(HocPhi, Truong.truong_id == HocPhi.truong_id)
        .filter(Truong.truong_id.in_(truong_ids))
        .all()
    )

    results = []
    diem_clgd = []
    diem_csvc = []
    diem_hd = []
    diem_hp = []
    labels = []

    for t in truongs:
        results.append({
            "truong_id": t.truong_id,
            "ten_truong": t.ten_truong,
            "clgd": t.diem_clgd,
            "csvc": t.diem_csvc,
            "hdnk": t.diem_hd,
            "hocphi": t.diem_hp
        })
        labels.append(t.ten_truong)
        diem_clgd.append(t.diem_clgd)
        diem_csvc.append(t.diem_csvc)
        diem_hd.append(t.diem_hd)
        diem_hp.append(t.diem_hp)

    def build_ahp_matrix(values, inverse=False):
        n = len(values)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                v1 = values[i]
                v2 = values[j]
                if inverse:  # học phí: càng thấp càng tốt
                    row.append(round(v2 / v1, 3) if v1 != 0 else 0)
                else:
                    row.append(round(v1 / v2, 3) if v2 != 0 else 0)
            matrix.append(row)
        return matrix

    return jsonify({
        "truongs": results,
        "labels": labels,
        "matrix_clgd": build_ahp_matrix(diem_clgd),
        "matrix_csvc": build_ahp_matrix(diem_csvc),
        "matrix_hd": build_ahp_matrix(diem_hd),
        "matrix_hp": build_ahp_matrix(diem_hp, inverse=True)  # học phí càng thấp càng tốt
    })

def float_to_fraction_str(x):
    try:
        return str(Fraction(x).limit_denominator(9))  # Giới hạn mẫu là 9 hoặc 10 để dễ đọc
    except:
        return str(x)
# Hàm tính trọng số
def calculate_weights(matrix):
    n = len(matrix)
    geo_means = []

    # 1. Tính trung bình hình học từng dòng
    for row in matrix:
        product = Fraction(1)
        for value in row:
            product *= value
        geo_mean = product ** (Fraction(1, n))
        geo_means.append(geo_mean)

    # 2. Chuẩn hóa (normalization)
    total = sum(geo_means)
    weights = [gm / total for gm in geo_means]

    return weights
# Tham số RI
RI_TABLE = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45
}
# Hàm tính toán chỉ số nhất quán
def calculate_consistency_ratio(matrix, weights):
    n = len(matrix)
    
    # Bước 1: Tính A * w
    aw = []
    for i in range(n):
        row_sum = sum([matrix[i][j] * weights[j] for j in range(n)])
        aw.append(row_sum)

    # Bước 2: Tính lambda_max
    lambda_max = sum([aw[i] / weights[i] for i in range(n)]) / n

    # Bước 3: CI
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0

    # Bước 4: CR
    ri = RI_TABLE.get(n, 1.45)  # mặc định nếu n > 9
    cr = ci / ri if ri != 0 else 0

    return lambda_max, ci, cr


@bp.route('/ahp_matrices', methods=['POST'])
def ahp_matrices():
    data = request.get_json()
    truong_ids = data.get('truong_ids', [])

    if not truong_ids:
        return "Không có ID trường được chọn", 400

    truongs = Truong.query.filter(Truong.truong_id.in_(truong_ids)).all()

    labels = [t.ten_truong for t in truongs]
    clgd = [t.chat_luong.diem_chuan_hoa for t in truongs]
    csvc = [t.co_so.diem_chuan_hoa for t in truongs]
    hd = [t.hoat_dong.diem_chuan_hoa for t in truongs]
    hp = [t.hoc_phi.hoc_phi_ch for t in truongs]

    def build_ahp_matrix(values, reverse=False):
        n = len(values)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                if values[i] == 0 or values[j] == 0:
                    row.append(Fraction(0, 1))
                else:
                    val = values[j] / values[i] if reverse else values[i] / values[j]
                    row.append(Fraction(val).limit_denominator())
            row = [elem if isinstance(elem, Fraction) else Fraction(elem) for elem in row]
            matrix.append(row)
        return matrix
    matrix_clgd = build_ahp_matrix(clgd)
    matrix_csvc = build_ahp_matrix(csvc)
    matrix_hd = build_ahp_matrix(hd)
    matrix_hp = build_ahp_matrix(hp, reverse=True)

    weights_clgd = calculate_weights(matrix_clgd)
    weights_csvc = calculate_weights(matrix_csvc)
    weights_hd = calculate_weights(matrix_hd)
    weights_hp = calculate_weights(matrix_hp)

    lambda_max_clgd, ci_clgd, cr_clgd = calculate_consistency_ratio(matrix_clgd, weights_clgd)
    lambda_max_csvc, ci_csvc, cr_csvc = calculate_consistency_ratio(matrix_csvc, weights_csvc)
    lambda_max_hd, ci_hd, cr_hd = calculate_consistency_ratio(matrix_hd, weights_hd)
    lambda_max_hp, ci_hp, cr_hp = calculate_consistency_ratio(matrix_hp, weights_hp)

    return render_template('ahp_matrices.html',
                       labels=labels,
                       matrix_clgd=matrix_clgd,
                       matrix_csvc=matrix_csvc,
                       matrix_hd=matrix_hd,
                       matrix_hp=matrix_hp,
                       weights_clgd=weights_clgd,
                       weights_csvc=weights_csvc,
                       weights_hd=weights_hd,
                       weights_hp=weights_hp,
                       lambda_clgd=lambda_max_clgd, ci_clgd=ci_clgd, cr_clgd=cr_clgd,
                       lambda_csvc=lambda_max_csvc, ci_csvc=ci_csvc, cr_csvc=cr_csvc,
                       lambda_hd=lambda_max_hd, ci_hd=ci_hd, cr_hd=cr_hd,
                       lambda_hp=lambda_max_hp, ci_hp=ci_hp, cr_hp=cr_hp)

@bp.route('/ahp_calculate_final', methods=['POST'])
def ahp_calculate_final():
    data = request.get_json()
    criteria_matrix = data.get("criteria_matrix")
    truong_ids = data.get("truong_ids", [])

    if not criteria_matrix or not truong_ids:
        return jsonify({"error": "Thiếu dữ liệu!"}), 400

    # Lấy dữ liệu các trường
    truongs = (
        db.session.query(
            Truong.truong_id,
            Truong.ten_truong,
            ChatLuongGiaoDuc.diem_chuan_hoa.label("clgd"),
            CoSoVatChat.diem_chuan_hoa.label("csvc"),
            HoatDongNgoaiKhoa.diem_chuan_hoa.label("hdnk"),
            HocPhi.hoc_phi_ch.label("hocphi")
        )
        .join(ChatLuongGiaoDuc, Truong.truong_id == ChatLuongGiaoDuc.truong_id)
        .join(CoSoVatChat, Truong.truong_id == CoSoVatChat.truong_id)
        .join(HoatDongNgoaiKhoa, Truong.truong_id == HoatDongNgoaiKhoa.truong_id)
        .join(HocPhi, Truong.truong_id == HocPhi.truong_id)
        .filter(Truong.truong_id.in_(truong_ids))
        .all()
    )

    # Xây dựng ma trận cho từng tiêu chí
    def build_matrix(values, inverse=False):
        n = len(values)
        matrix = []
        for i in range(n):
            row = []
            for j in range(n):
                a = values[i]
                b = values[j]
                if inverse:
                    row.append(b / a if a != 0 else 0)
                else:
                    row.append(a / b if b != 0 else 0)
            matrix.append(row)
        return matrix

    # Lấy điểm
    diem_clgd = [t.clgd for t in truongs]
    diem_csvc = [t.csvc for t in truongs]
    diem_hd = [t.hdnk for t in truongs]
    diem_hp = [t.hocphi for t in truongs]

    # Tính trọng số tiêu chí
    weights_criteria = calculate_weights(criteria_matrix)
    lambda_max, ci, cr = calculate_consistency_ratio(criteria_matrix, weights_criteria)

    # Tính trọng số phương án cho từng tiêu chí
    weights_clgd = calculate_weights(build_matrix(diem_clgd))
    weights_csvc = calculate_weights(build_matrix(diem_csvc))
    weights_hd = calculate_weights(build_matrix(diem_hd))
    weights_hp = calculate_weights(build_matrix(diem_hp, inverse=True))  # học phí càng thấp càng tốt

    # Tính điểm tổng hợp cuối cùng
    final_scores = []
    for i in range(len(truongs)):
        score = (
            weights_criteria[0] * float(weights_clgd[i]) +
            weights_criteria[1] * float(weights_csvc[i]) +
            weights_criteria[2] * float(weights_hp[i]) +
            weights_criteria[3] * float(weights_hd[i])
        )
        final_scores.append(score)

    results = []
    for i, t in enumerate(truongs):
        results.append({
            "truong_id": t.truong_id,
            "ten_truong": t.ten_truong,
            "diem": round(final_scores[i], 4)
        })

    return jsonify({
        "weights_criteria": [float(w) for w in weights_criteria],
        "lambda_max": float(lambda_max),
        "CI": float(ci),
        "CR": float(cr),
        "results": results
    })
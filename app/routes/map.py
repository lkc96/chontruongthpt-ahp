from flask import Blueprint, render_template, jsonify, request
from app.models import Truong, ChatLuongGiaoDuc, CoSoVatChat, HoatDongNgoaiKhoa, HocPhi
from app import db
from fractions import Fraction
from flask import Blueprint, jsonify


bp = Blueprint('map', __name__)

@bp.route('/api/truong')
def get_truong():
    conn = db.engine.raw_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(vi_tri_dia_ly)::jsonb,
                    'properties', to_jsonb(row) - 'vi_tri_dia_ly'
                )
            )
        )
        FROM (SELECT truong_id, ten_truong, dia_chi, vi_tri_dia_ly FROM truong) AS row;
    """)
    data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify(data)


@bp.route('/api/ranhphuong')
def get_ranhphuong():
    conn = db.engine.raw_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(
                jsonb_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', to_jsonb(row) - 'geom'
                )
            )
        )
        FROM (SELECT gid, name_2, geom FROM quan_huyen) AS row;
    """)
    data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify(data)

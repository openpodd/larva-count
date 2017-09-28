# -*- coding: utf-8 -*-
import json
import os

import psycopg2 as psycopg2


def envVar(name, defaultValue):
    if name in os.environ:
        return os.environ[name]
    else:
        return defaultValue

DB_HOST = envVar('DB_HOST', 'localhost')
DB_NAME = envVar('DB_NAME', 'podd')
DB_USER = envVar('DB_USER', 'podd')
DB_PASSWORD = envVar('DB_PASSWORD', '')
DOMAIN_ID = envVar('DOMAIN_ID', 1)


def connect():
    print "connect to %s" % (DB_HOST,)
    conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (DB_NAME, DB_USER, DB_HOST, DB_PASSWORD))
    return conn


def fetch_report_type_id(conn, code, domain_id=1):
    cur = conn.cursor()
    cur.execute("select id from reports_reporttype where code = %s and domain_id = %s", (code, domain_id,))
    (report_type_id,) = cur.fetchone()
    print "report type id = %s" % (report_type_id)
    cur.close()
    return report_type_id


def fetch_reports(conn, report_type_id, date_begin, date_end, domain_id=1):
    FIND_REPORT_QUERY = """
    select id, 
           form_data, 
           date,
           ST_X(report_location::geometry) as longitude,
           ST_Y(report_location::geometry) as latitude 
          from reports_report
          where type_id = %s
          and date between %s and %s
          and (test_flag is null or test_flag = FALSE)
          and negative = TRUE 
          and domain_id = %s

    """
    cur = conn.cursor()
    cur.execute(FIND_REPORT_QUERY, (report_type_id, date_begin, date_end, domain_id))
    rows = cur.fetchall()
    cur.close()

    datas = []
    for row in rows:
        (report_id, form_data_str, date, longitude, latitude) = row
        form_data = json.loads(form_data_str)
        datas.append({
            'report_id': report_id,
            'date': date,
            'form_data': form_data,
            'longitude': longitude,
            'latitude': latitude,
        })

    return datas
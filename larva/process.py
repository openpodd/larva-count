# -*- coding: utf-8 -*-
import db
import pandas
import re


def parse_address(address_str):
    if address_str:
        def parse_item(item_str):
            im = re.match("\[[^:]+:(.*)\]", item_str)
            if im is not None:
                return im.group(1)
            return None

        m = re.match("(\[[^\]]*\])(\[[^\]]*\])(\[[^\]]*\])", address_str)
        if m is not None:
            p, d, s = m.group(1, 2, 3)
            province = parse_item(p).replace(u'จ. ', '')
            district = parse_item(d).replace(u'อ. ', '')
            subdistrict = parse_item(s).replace(u'ต. ', '')
            return province, district, subdistrict

    return '', '', ''


def run(params, conn, outputfile):
    """
    create spreadsheet fill with larva survey result, calculate HI, CI
    :param dict that contain
        date_begin: string format 'yyyy-mm-dd'
        date_end: string format 'yyyy-mm-dd'
        domain_id: int
    :param conn database connection
    :param outputfile string filename with fullpath
    :return:
    """
    date_begin = params['date_begin']
    date_end = params['date_end']
    domain_id = params['domain_id']

    report_type_id = db.fetch_report_type_id(conn, 'larva-count', domain_id)
    data = db.fetch_reports(conn, report_type_id, date_begin, date_end, domain_id)

    results = []
    for row in data:
        form_data = row['form_data']
        province, district, subdistrict = parse_address(form_data.get('address', ''))
        if 'total_containers' in form_data and 'found_containers' in form_data:
            results.append({
                'report_id': row['report_id'],
                'date': row['date'],
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'province': province,
                'district': district,
                'subdistrict': subdistrict,
                'village_no': str(form_data.get('village_no', '')),
                'place': form_data.get('place', ''),
                'house_no_name': form_data.get('house_no_name', ''),
                'total_containers': form_data['total_containers'],
                'found_containers': form_data['found_containers'],
            })

    if len(results) == 0:
        return False
    data = pandas.DataFrame(results)
    data['date'] = data['date'].astype('datetime64[ns]')
    data['village_no'] = data['village_no'].astype('str')

    valid_data = data[data.total_containers > 0]
    valid_data = valid_data.copy()
    valid_data['ci'] = valid_data['found_containers'] / valid_data['total_containers'] * 100
    valid_data['ci'] = valid_data.apply(lambda row: float("{0:.2f}".format(row['ci'])), axis=1)
    valid_data['ci_found'] = valid_data.apply(lambda row: 1 if row['ci'] > 0 else 0, axis=1)

    house_df = valid_data.loc[valid_data['place'] == u'บ้าน']
    non_house_df = valid_data.loc[valid_data['place'] != u'บ้าน']
    house_summary_df = house_df.groupby(['province', 'district', 'subdistrict', 'village_no'])

    values = []
    values.append([
        'province',
        'district',
        'subdistrict',
        'village',
        'found_houses',
        'total_houses',
        'HI'
    ])
    for name, group in house_summary_df:
        found = group.loc[group['ci_found'] > 0]
        cnt_found = len(found)
        cnt_all = len(group)
        values.append([
            name[0],
            name[1],
            name[2],
            name[3],
            cnt_found,
            cnt_all,
            float("{0:.2f}".format((float(cnt_found) / cnt_all) * 100.00))
        ])

    hi_df = pandas.DataFrame(values)

    writer = pandas.ExcelWriter(outputfile)
    df = valid_data[['province', 'district', 'subdistrict', 'village_no', 'place', 'found_containers', 'total_containers', 'ci']]
    df.to_excel(writer, 'ci')
    hi_df.to_excel(writer, 'hi')
    writer.save()
    return True
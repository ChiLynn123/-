import csv
from typing import List
import json
from collections import defaultdict
import os
import time

import requests


# from utils.helper import get_chunk_data

csv.field_size_limit(50 * 1024 * 1024)


def get_data(file, n=500):
    tmplist = []
    with open(file, "r", newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        cnt = 0
        fieldnames = ["uid", "html_origin_content", "url", "ip", "ip_loc"]
        for row in csvreader:
            if cnt == 0:
                cnt += 1
                continue
            tmpdict = {fieldnames[idx]: row[idx] for idx in range(len(fieldnames))}
            tmplist.append(tmpdict)
            cnt += 1
            if cnt == n + 1:
                break
    return tmplist


def count_class(judge_result):
    """Countes the different class number.
    Args:
        judge_result: list of dicts container 'cls_id' key.
    Returns:
        dict of every class count. eg:
        {'018000': 300, '9990000': 200}

    """
    res = defaultdict(int)
    for item in judge_result:
        res[item["cls_id"]] += 1
    return res


def smoke_test(data: List, port=10011, debug=False):
    if debug:
        api_url = "http://10.1.203.15:{}/v1/combine_predict?debug=on".format(port)
    else:
        api_url = "http://10.1.203.15:{}/v1/combine_predict".format(port)
    print(f"requests: {api_url}")
    payload = {"query_html_origin": []}
    payload["debug"] = True
    for item in data:
        payload["query_html_origin"].append(item)
    timeout = True
    success = False
    while timeout and not success:
        TIMEOUT = 40
        try:
            response = requests.post(api_url, data=json.dumps(payload), timeout=TIMEOUT)
            success = True
        except requests.exceptions.Timeout as exc:
            timeout = True
            TIMEOUT += 10
        except Exception as exc:
            timeout = True
    result = json.loads(response.text)
    cls_cnt = count_class(result["judge_result"])
    print('api classify completed')
    # print("{0:=^80}".format("="))
    # print(
    #     "time_consume:{0:>20}\nvalidate_count:{1:>20}\ncls_cnt:{2}\ndebug_info:{3}".format(
    #         result["time_consume"],
    #         result["validate_count"],
    #         str(sorted(cls_cnt.items())),
    #         result["debug_infos"],
    #     )
    # )
    # print("{0:=^80}".format("="))
    info = json.loads(response.text)
    
    return response


# 每500个进行处理
def chunk_test(file, port=10011, chunk_size=500, debug=False):
    chunk = []
    filename = os.path.basename(file)
    f = open(f"{filename}_chunk.txt", "w")
    with open(file, "r", newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        cnt = 0
        fieldnames = ["uid", "html_origin_content", "url", "ip", "ip_loc"]
        for row in csvreader:
            if row[0] == "html_content_id":
                continue
            try:
                tmpdict = {fieldnames[idx]: row[idx] for idx in range(len(fieldnames))}
            except:
                continue
            chunk.append(tmpdict)
            cnt += 1
            if cnt == chunk_size:
                cnt = 0
                response = smoke_test(chunk, port, debug)
                info = json.loads(response.text)
                cls_cnt = count_class(info["judge_result"])
                f.write(
                    f"{info['time_consume']}\t{sorted(cls_cnt.items())}\t{info['validate_count']}\t{info['debug_infos']}\n"
                )
                f.flush()
                chunk = []
        cls_cnt = count_class(info["judge_result"])
        if chunk:
            response = smoke_test(chunk, port)
            info = json.loads(response.text)
            f.write(
                f"{info['time_consume']}\t{sorted(cls_cnt.items())}\t{info['validate_count']}\t{info['debug_infos']}\n"
            )
        f.close()


def write_to_table(df, table_name, if_exists='fail'):
    import io
    import pandas as pd
    from sqlalchemy import create_engine
    db_engine = create_engine('postgresql://***:***@***:***/***')  # 初始化引擎
    string_data_io = io.StringIO()
    df.to_csv(string_data_io, sep='|', index=False)
    pd_sql_engine = pd.io.sql.pandasSQL_builder(db_engine)
    table = pd.io.sql.SQLTable(table_name, pd_sql_engine, frame=df,
                               index=False, if_exists=if_exists, schema = 'public')
    table.create()
    string_data_io.seek(0)
    with db_engine.connect() as connection:
        with connection.connection.cursor() as cursor:
            copy_cmd = "COPY public.%s FROM STDIN HEADER DELIMITER '|' CSV" %table_name
            cursor.copy_expert(copy_cmd, string_data_io)
        connection.connection.commit()


def read_csv(file, chunk_size=233):
    chunk = []
    id_list = []
    data_col = []
    filename = os.path.basename(file)
    with open(file, "r", newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        cnt = 0
        fieldnames = ["uid", "html_origin_content"]
        for row in csvreader:
            if row[0] == "html_content_id":
                continue
            try:
                tmpdict = {fieldnames[idx]: row[idx] for idx in range(len(fieldnames))}
                id_ = row[0]
            except:
                continue
            chunk.append(tmpdict)
            id_list.append(id_)
            cnt += 1
            if cnt == chunk_size:
                cnt = 0
                other_items = read_data2(id_list)
                for idx, item in enumerate(chunk):
                    all_items = dict(chunk[idx], **other_items[idx])
                    data_col.append(all_items)
                print(len(data_col))
                # response = smoke_test(chunk, port, debug)
                id_list = []
                chunk = []
                data_col = []
        if chunk and id_list and data_col:
            print('**************')
            print(len(data_col))


if __name__ == "__main__":
    # tmplist = get_data("webmail_test_1.7w_202111221604.csv", 500)
    # smoke_test(tmplist)
    import argparse

    parser = argparse.ArgumentParser(description="Fastapi test.")
    parser.add_argument("-p", help="api port", dest="port", type=int, default=10018)
    parser.add_argument(
        "-n", help="chunk size", dest="chunk_size", type=int, default=500
    )
    parser.add_argument("-d", help="debug type", dest="debug", type=bool, default=False)
    args = parser.parse_args()

    chunk_test(
        "E:/需求统计分析/外星人数据库表合并/600.csv",
        args.port,
        args.chunk_size,
        args.debug,
    )

    # tmplist = get_data("./time_consume_500_345.csv")
    # smoke_test(tmplist, 10013, True)

    # print(len(tmplist))
    # print(f"html_origin_content:{tmplist[1]['html_origin_content']}")
    # print(f"html_content_id:{tmplist[1]['html_content_id']}")
    # print(f"ip:{tmplist[1]['ip']}")
    # print(f"ip_loc:{tmplist[1]['ip_loc']}")

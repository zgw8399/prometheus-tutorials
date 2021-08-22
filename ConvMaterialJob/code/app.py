#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import os
import time
import logging
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler

from modules.Database import MySQL
from modules.Config import config

logging.basicConfig(level=logging.INFO)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")


class HealthcheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Service is healthy")


def make_app():
    return tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/healthz", HealthcheckHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )


def get_convmaterial():
    # Mongo数据库初始化
    client = pymongo.MongoClient(**config['mongo'])
    db = client[config['db']['mes_db_name']]
    coll = db[config['coll']['convmaterial_coll_name']]
    # 获取当天的料号列表
    sql = """SELECT RawMaterialID
             FROM ReMaterial
             WHERE TO_DAYS(CreateTime) = TO_DAYS(NOW())
             GROUP BY RawMaterialID"""
    mysqldb = MySQL()
    rawmaterial_ids = mysqldb.fetch_all(sql)
    # 如果有入料记录，则遍历料号列表，统计每个料号的所有转产记录
    if rawmaterial_ids:
        rawmaterial_subtotals = []
        for rawmaterial_id in rawmaterial_ids:
            # 获取当天所有的入料记录
            weight_subtotal = 0
            counter = 0
            sql = """SELECT RawMaterialID,CreateTime,Weight
                     FROM ReMaterial
                     WHERE TO_DAYS(CreateTime) = TO_DAYS(NOW())"""
            mysqldb = MySQL()
            result = mysqldb.fetch_all(sql)
            # 遍历当天所有入料记录，并将转产记录存入数据库
            for idx, val in enumerate(result):
                # 如果入料记录的料号与当前料号匹配，则统计重量
                if val['RawMaterialID'] == rawmaterial_id['RawMaterialID']:
                    weight_subtotal += val['Weight']
                    counter += 1
                # 如果统计的重量和数量不为0，则将转产记录存入数据库
                elif weight_subtotal != 0 and counter != 0:
                    begin_pos = idx - counter
                    end_pos = idx - 1
                    rawmaterial_subtotal = {
                        "rawmaterialID": rawmaterial_id['RawMaterialID'],
                        "beginTime": result[begin_pos]['CreateTime'],
                        "endTime": result[end_pos]['CreateTime'],
                        "weightSubtotal": weight_subtotal
                    }
                    rawmaterial_subtotals.append(rawmaterial_subtotal)
                    weight_subtotal = 0
                    counter = 0
                    continue
                # 如果以上都不匹配，则继续统计下一条入料记录
                else:
                    continue
                # 如果入料记录为最后一条，则将当前统计的最新转产记录写入数据库
                if idx == len(result) - 1 and weight_subtotal != 0 and counter != 0:
                    begin_pos = len(result) - counter
                    end_pos = idx
                    rawmaterial_subtotal = {
                        "rawmaterialID": rawmaterial_id['RawMaterialID'],
                        "beginTime": result[begin_pos]['CreateTime'],
                        "endTime": result[end_pos]['CreateTime'],
                        "weightSubtotal": weight_subtotal
                    }
                    rawmaterial_subtotals.append(rawmaterial_subtotal)
        today = time.strftime("%Y%m%d", time.localtime(time.time()))
        today2 = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        rawmaterial_total = {
            "_id": today,
            "date": today2,
            "conversionTotal": rawmaterial_subtotals
        }
        logging.info(rawmaterial_total)
        coll.save(rawmaterial_total)
    else:
        logging.info("当前没有任何入料记录！")
    # 关闭Mongo数据库连接
    client.close()


if __name__ == '__main__':
    # 后台执行的程序
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_convmaterial, 'interval', seconds=300, id='job1')
    scheduler.start()
    get_convmaterial()

    # 主程序
    app = make_app()
    app.listen(80)
    tornado.ioloop.IOLoop.current().start()

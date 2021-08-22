#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json
import os
import shutil

from base import BaseHandler, config 


class CertificateDownloadHandler(BaseHandler):
    # 数据库连接初始化
    def initialize(self):
        self.client = pymongo.MongoClient(**config.mongodb_options)
        self.db = self.client[config.db['tlink_db_name']]
        self.coll = self.db[config.coll['certificate_coll_name']]

    # 下载证书信息
    def get(self):
        #try:
           certificate_name = self.get_argument('CertificateName','')
           if certificate_name:
               query = {
                   "CertificateName": certificate_name
               }
               if self.coll.find_one(query):
                   self.set_header ('Content-Type', 'application/octet-stream')
                   self.set_header ('Content-Disposition', 'attachment; filename=' + certificate_name + '.ovpn')
                   certificate_path = os.path.join(config.certificate_dir, certificate_name + '.ovpn')
                   if (os.path.exists(certificate_path)):
                       with open(certificate_path, 'rb') as f:
                           while True:
                               data = f.read(16*1024)
                               if not data:
                                   break
                               self.write(data)
                       self.finish()
                   else:
                       self.write("证书文件不存在！")
               else:
                   self.write("证书信息不存在！")
           else:
               self.write("证书名不能为空！")
        #except:
        #    self.write("下载失败！")

    # 数据库连接关闭
    def on_finish(self):
        self.client.close()


if __name__ == "__main__":
    pass


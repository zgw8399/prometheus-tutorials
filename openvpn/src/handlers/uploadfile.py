#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json
import os
import shutil

from base import BaseHandler, config


class UploadFileHandler(BaseHandler):
    # 数据库连接初始化
    def initialize(self):
        self.client = pymongo.MongoClient(**config.mongodb_options)
        self.db = self.client[config.db['tlink_db_name']]
        self.coll = self.db[config.coll['certificate_coll_name']]

    # 上传文件
    def post(self):
        #try:
           # 文件的存储路径
           upload_path=os.path.join(os.path.dirname(__file__),'files')
           # 提取表单中‘name’为‘file’的文件元数据
           file_metas=self.request.files['file']
           for meta in file_metas:
               filename=meta['filename']
               filepath=os.path.join(upload_path,filename)
               # 有些文件需要以二进制的形式存储，实际中可以更改
               with open(filepath,'wb') as f:
                   f.write(meta['body'])
               self.write('上传成功！')
        #except:
        #    self.write('上传失败！')

    # 数据库连接关闭
    def on_finish(self):
        self.client.close()


if __name__ == "__main__":
    pass


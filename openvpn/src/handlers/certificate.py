#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json
import os
import shutil

from base import BaseHandler, config, RunCMD


class CertificateHandler(BaseHandler):
    # 数据库连接初始化
    def initialize(self):
        self.client = pymongo.MongoClient(**config.mongodb_options)
        self.db = self.client[config.db['tlink_db_name']]
        self.coll = self.db[config.coll['certificate_coll_name']]

    # 查询证书信息
    def get(self):
        #try:
           if self.get_argument('CertificateName',''):
               query = {
                   "CertificateName": self.get_argument('CertificateName')
               }
               data = {
                   "state": "success",
                   "message": "查询成功！",
                   "payload": self.coll.find_one(query, {"_id": 0})
               }
               self.write(json.dumps(data))
           else:
               data = {
                   "state": "success",
                   "message": "查询成功！",
                   "payload":  [x for x in self.coll.find({}, {"_id": 0})]
               }
               self.write(json.dumps(data))
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "查询失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 添加证书信息
    def post(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           certificate_name = request_data.get('CertificateName')
           query = {
               "CertificateName": certificate_name
           }
           if self.coll.find_one(query):
               data = {
                   "state": "failure",
                   "message": "信息已存在，请勿重复添加！",
                   "payload": ""
               }
               self.write(json.dumps(data))
           else:
               # 生成客户端证书
               cwd = os.getcwd()
               os.chdir(config.easyrsa_dir)
               cmd = 'echo ' + certificate_name + ' | ./easyrsa gen-req ' + certificate_name + ' nopass'
               rc = RunCMD(cmd)
               result = rc.run()
               if result.returncode == 0:
                   cmd = 'echo yes | ./easyrsa sign-req client ' + certificate_name
                   rc = RunCMD(cmd)
                   result = rc.run()
                   os.chdir(cwd)
                   if result.returncode == 0:
                       certificate_path = os.path.join(config.certificate_dir, certificate_name + '.ovpn')
                       client_base_conf_path = os.path.join(config.openvpn_conf_dir, config.client_base_conf_file)
                       ca_path = os.path.join(config.easyrsa_dir + '/pki', 'ca.crt')
                       cert_path = os.path.join(config.easyrsa_dir + '/pki/issued', certificate_name + '.crt')
                       key_path = os.path.join(config.easyrsa_dir + '/pki/private', certificate_name + '.key')
                       tls_auth_path = os.path.join(config.easyrsa_dir, 'ta.key')
                       # 写入证书到客户端配置文件
                       with open(certificate_path, 'a') as f:
                           with open(client_base_conf_path, 'r') as fo:
                               f.write(fo.read())
                           f.write('<ca>\n')
                           with open(ca_path, 'r') as fo:
                               f.write(fo.read())
                           f.write('</ca>\n<cert>\n')
                           with open(cert_path, 'r') as fo:
                               f.write(fo.read())
                           f.write('</cert>\n<key>\n')
                           with open(key_path, 'r') as fo:
                               f.write(fo.read())
                           f.write('</key>\n<tls-auth>\n')
                           with open(tls_auth_path, 'r') as fo:
                               f.write(fo.read())
                           f.write('</tls-auth>')
                       # 添加证书信息到数据库
                       self.coll.insert_one(request_data)
                       data = {
                           "state": "success",
                           "message": "添加成功！",
                           "payload": ""
                       }
                       self.write(json.dumps(data))
                   else:
                       data = {
                           "state": "failure",
                           "message": "证书签名失败！",
                           "payload": ""
                       }
                       self.write(json.dumps(data))
               else:
                   data = {
                       "state": "failure",
                       "message": "证书请求失败！",
                       "payload": ""
                   }
                   self.write(json.dumps(data))
        #except:
        #   data = {
        #       "state": "failure",
        #       "message": "添加失败！",
        #       "payload": ""
        #   }
        #   self.write(json.dumps(data))

    # 修改证书信息
    def put(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           query = {
               "CertificateName": request_data.get('CertificateName')
           }
           values = {
               "$set": request_data
           }
           self.coll.update_one(query, values, upsert=True)
           data = {
               "state": "success",
               "message": "修改成功！",
               "payload": ""
           }
           self.write(json.dumps(data))
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "修改失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 删除证书信息
    def delete(self):
        #try:
           request_data = json.loads(self.request.body.decode('utf-8'))
           certificate_name = request_data.get('CertificateName')
           query = {
               "CertificateName": certificate_name
           }
           self.coll_user = self.db[config.coll['user_coll_name']]
           if self.coll_user.find_one(query):
               data = {
                   "state": "failure",
                   "message": "已有关联数据，不允许删除！",
                   "payload": ""
               }
               self.write(json.dumps(data))
           else:
               # 吊销证书
               cwd = os.getcwd()
               os.chdir(config.easyrsa_dir)
               cmd = 'echo yes | ./easyrsa revoke ' + certificate_name
               rc = RunCMD(cmd)
               result = rc.run()
               if result.returncode == 0:
                   cmd = './easyrsa gen-crl'
                   rc = RunCMD(cmd)
                   result = rc.run()
                   os.chdir(cwd)
                   if result.returncode == 0:
                       # 更新CRL文件
                       src_crl_path = os.path.join(config.easyrsa_dir + '/pki', 'crl.pem')
                       dest_crl_path = os.path.join(config.openvpn_conf_dir, 'crl.pem')
                       shutil.copy(src_crl_path, dest_crl_path)
                       # 删除证书文件
                       certificate_path = os.path.join(config.certificate_dir, certificate_name + '.ovpn')
                       if (os.path.exists(certificate_path)):
                           os.remove(certificate_path)
                       # 从数据库中删除证书信息
                       self.coll.delete_one(query)
                       data = {
                           "state": "success",
                           "message": "删除成功！",
                           "payload": ""
                       }
                       self.write(json.dumps(data))
                   else:
                       data = {
                           "state": "failure",
                           "message": "CRL生成失败！",
                           "payload": ""
                       }
                       self.write(json.dumps(data))
               else:
                   data = {
                       "state": "failure",
                       "message": "证书吊销失败！",
                       "payload": ""
                   }
                   self.write(json.dumps(data))
        #except:
        #    data = {
        #        "state": "failure",
        #        "message": "删除失败！",
        #        "payload": ""
        #    }
        #    self.write(json.dumps(data))

    # 数据库连接关闭
    def on_finish(self):
        self.client.close()


if __name__ == "__main__":
    pass


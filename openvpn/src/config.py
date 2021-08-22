# -*- coding: utf-8 -*-

import os

# Tornado App配置
settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "template"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "",
    "xsrf_cookie": False,
    "debug": True
}

# MongoDB配置
mongodb_options = {
    "host": "localhost",
    "port": 27017,
    "username": "admin",
    "password": "password",
    "authSource": "admin",
    "authMechanism": "SCRAM-SHA-256",
    "maxPoolSize": 1024
}

# 数据库配置
db = {
    "tlink_db_name": "TLink"
}

# 集合配置
coll = {
    "factory_coll_name": "Factory",
    "workshop_coll_name": "Workshop",
    "productionline_coll_name": "ProductionLine",
    "machiningcenter_coll_name": "MachiningCenter",
    "vpnserver_coll_name": "VPNServer",
    "user_coll_name": "User",
    "certificate_coll_name": "Certificate",
    "equipment_coll_name": "Equipment",
    "model_coll_name": "Model"
}

# VPN配置
easyrsa_dir = '/usr/share/easy-rsa'
client_base_conf_file = 'client_base.conf'
certificate_dir = '/etc/openvpn/client'
openvpn_conf_dir = '/etc/openvpn'

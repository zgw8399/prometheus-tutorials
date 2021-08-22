#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('handlers/')

from base import IndexHandler, HealthCheckHandler
import factory
import workshop
import productionline
import machiningcenter
import vpnserver
import user
import certificate
import certificatedownload
import equipment
import model

# 路由映射
handlers = [
    (r"/", IndexHandler),
    (r"/healthz", HealthCheckHandler),
    (r"/api/v1/Factory", factory.FactoryHandler),
    (r"/api/v1/Workshop", workshop.WorkshopHandler),
    (r"/api/v1/ProductionLine", productionline.ProductionLineHandler),
    (r"/api/v1/MachiningCenter", machiningcenter.MachiningCenterHandler),
    (r"/api/v1/VPNServer", vpnserver.VPNServerHandler),
    (r"/api/v1/User", user.UserHandler),
    (r"/api/v1/Certificate", certificate.CertificateHandler),
    (r"/api/v1/CertificateDownload", certificatedownload.CertificateDownloadHandler),
    (r"/api/v1/Equipment", equipment.EquipmentHandler),
    (r"/api/v1/Model", model.ModelHandler),
]


if __name__ == "__main__":
    pass


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 代码兼容, 即在python2中使用python3的print函数, 导入后使用python2的print则会报错
from __future__ import print_function

import os
import sys
import os.path


"""基础环境"""
# 当前路径
path = os.path.dirname(__file__)
# 部署路径
deploy_path = path

"""部署环境"""
# compose版本
compose_version = '3.8'
# 容器网络名称
network_name = 'mes'
# 部署栈名称
stack_name = 'mes'
# 容器仓库地址
registry_host = 'localhost:5000'
# 项目名称
project_name = 'mes'
# 应用名称
app_name = 'convmaterial-api'
# 应用版本
app_version = '0.0.1'
# 镜像名称, 依赖于以上变量
image_name = '{}/{}/{}:{}'.format(registry_host, project_name, app_name, app_version)
# 服务端口
service_port = '30082'
# 副本数
replicas = '1'
# 资源请求
limits_memory = '512m'
limits_cpus = '1'
reservations_memory = '128m'
reservations_cpus = '0.5'
# 健康检查
interval = '15s'
timeout = '10s'
retries = '3'
start_period = '40s'

"""部署所需文件"""
dp_files = {}
dp_files['docker-compose.yml'] = '''
version: '{compose_version}'

networks:
  app_net:
    external: true
    name: {network_name}

services:
  {app_name}:
    image: {image_name}
    ports:
      - {service_port}:80
    networks:
      - app_net
    deploy:
      mode: replicated
      replicas: {replicas}
      resources:
        limits:
          memory: {limits_memory}
          cpus: '{limits_cpus}'
        reservations:
          memory: {reservations_memory}
          cpus: '{reservations_cpus}'
    healthcheck:
      test: ["CMD-SHELL", "curl -f -s http://localhost/healthz || exit 1"]
      interval: {interval}
      timeout: {timeout}
      retries: {retries}
      start_period: {start_period}
'''.format(compose_version=compose_version, network_name=network_name, app_name=app_name, image_name=image_name,
           service_port=service_port, replicas=replicas, limits_memory=limits_memory, limits_cpus=limits_cpus,
           reservations_memory=reservations_memory, reservations_cpus=reservations_cpus, interval=interval,
           timeout=timeout, retries=retries, start_period=start_period)

'''构建镜像所需文件'''
build_files = {}
build_files['_configs.yaml'] = '''
'''
build_files['Dockerfile'] = '''
FROM python:3.6.13-alpine3.13

MAINTAINER varden

# 修改安装源
RUN echo "https://mirrors.aliyun.com/alpine/v3.13/main/" > /etc/apk/repositories
RUN echo "https://mirrors.aliyun.com/alpine/v3.13/community/" >> /etc/apk/repositories
ENV LANG C.UTF-8
RUN apk update

# 安装必需软件和修改时区
RUN apk add --no-cache ca-certificates tzdata curl bash && rm -rf /var/cache/apk/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone

# 设定容器工作目录
WORKDIR /app

# 安装程序依赖
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 添加程序代码
ADD code/ /app/

# 运行程序
CMD python app.py
'''


def create_network():
    """创建容器网络"""
    print('[ 创建容器网络：{} ]'.format(network_name))
    cmd = "docker network ls | grep -w -o {} &>/dev/null".format(network_name)
    return_code = os.system(cmd)
    if return_code != 0:
        cmd = 'docker network create --attachable -d overlay {}'.format(network_name)
        print(cmd)
        os.system(cmd)
        print('*** 完成容器网络创建 ***')
    else:
        print('*** 容器网络已存在 ***')
    print()


def gen_files(files):
    """生成文件"""
    def write_file(filename, content):
        """写入文件"""
        fullname = os.path.join(deploy_path, filename)
        print('创建文件：' + fullname)
        with open(fullname, 'w') as f:
            f.write(content)
        return fullname

    print('[ 生成文件：{} ]'.format(','.join(files.keys())))
    names = [
        write_file(filename, content)
        for (filename, content) in files.items()
    ]
    print()
    return names


def build():
    """构建容器"""
    print("<--- 构建容器部分 --->")
    print()
    filenames = gen_files(build_files)
    print("*** 开始镜像构建 ***")
    cmd = 'docker build -t {} .'.format(image_name)
    print(cmd)
    os.system(cmd)
    print("*** 完成镜像构建 ***")
    print("*** 开始镜像上传 ***")
    cmd = 'docker push {}'.format(image_name)
    print(cmd)
    os.system(cmd)
    print("*** 完成镜像上传 ***")
    print()
    clean(filenames)


def deploy():
    """部署服务"""
    print('<--- 部署服务部分 --->')
    print()
    create_network()
    filenames = gen_files(dp_files)
    print("*** 开始服务部署 ***")
    cmd = 'docker stack deploy -c docker-compose.yml {}'.format(stack_name)
    print(cmd)
    os.system(cmd)
    print("*** 完成服务部署 ***")
    print()
    clean(filenames)


def clean(filenames):
    """清理文件"""
    print('[ 清理文件：{} ]'.format(",".join(filenames)))
    for filename in filenames:
        os.system('rm -f ' + filename)
        print('删除文件：' + filename)
    print()


def main(stage):
    if stage == 'build':
        build()
    elif stage == 'deploy':
        deploy()
    else:
        print('`{}` option is not found, please input `build` or `deploy` option.'.format(stage))


if __name__ == "__main__":
    arg_list = sys.argv
    if len(arg_list) == 2:
        main(arg_list[1])
    else:
        print('option error, please input `build` or `deploy` option.')

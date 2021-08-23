#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rediscluster import RedisCluster

startup_nodes = [
    {"host": "127.0.0.1", "port": "7001"},
    {"host": "127.0.0.1", "port": "7002"},
    {"host": "127.0.0.1", "port": "7003"},
    {"host": "127.0.0.1", "port": "7004"},
    {"host": "127.0.0.1", "port": "7005"},
    {"host": "127.0.0.1", "port": "7006"}
]

rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

rc.set("foo_python3", "bar_python3")

print(rc.get("foo_python3"))

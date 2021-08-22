#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml


def get_config():
    with open("./configs/config.yaml", encoding='utf-8') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


config = get_config()

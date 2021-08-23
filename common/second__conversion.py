#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import math


def second_conversion(seconds):
    one_day = 24*60*60
    one_hour = 60*60
    one_minute = 60
    if seconds < 60:
        return "%d秒" % math.ceil(seconds)
    elif seconds > one_day:
        days = divmod(seconds, one_day)
        return "%d天%s" % (int(days[0]), second_conversion(days[1]))
    elif seconds > one_hour:
        hours = divmod(seconds, one_hour)
        return '%d小时%s' % (int(hours[0]), second_conversion(hours[1]))
    else:
        minutes = divmod(seconds, one_minute)
        return "%d分%d秒" % (int(minutes[0]), math.ceil(minutes[1]))


if __name__ == "__main__":
    seconds = 0
    print(seconds, second_conversion(seconds))
    seconds = 6
    print(seconds, second_conversion(seconds))
    seconds = 60
    print(seconds, second_conversion(seconds))
    seconds = 66
    print(seconds, second_conversion(seconds))
    seconds = 3600
    print(seconds, second_conversion(seconds))
    seconds = 3660
    print(seconds, second_conversion(seconds))
    seconds = 3666
    print(seconds, second_conversion(seconds))
    seconds = 86400
    print(seconds, second_conversion(seconds))
    seconds = 86460
    print(seconds, second_conversion(seconds))
    seconds = 86466
    print(seconds, second_conversion(seconds))
    seconds = 90066
    print(seconds, second_conversion(seconds))

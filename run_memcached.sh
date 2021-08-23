#!/bin/bash
#
nohup /usr/share/memcached/scripts/systemd-memcached-wrapper /etc/memcached-11212.conf &
nohup /usr/share/memcached/scripts/systemd-memcached-wrapper /etc/memcached-11213.conf &

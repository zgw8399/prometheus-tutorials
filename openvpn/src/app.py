#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options, define

import config
import route

define("port", default=8888, type=int, help="run server on the given port.")


class App(tornado.web.Application):
    def __init__(self):
        self.__handlers = route.handlers
        self.__settings = config.settings
        tornado.web.Application.__init__(self, self.__handlers, **self.__settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.httpserver.HTTPServer(App())
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


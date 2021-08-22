#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options, define

import route


define("port", default=80, type=int, help="run server on the given port.")


class App(tornado.web.Application):
    def __init__(self):
        self.__handlers = route.handlers
        self.__settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret="",
            xsrf_cookie=False,
            debug=True
        )
        tornado.web.Application.__init__(self, self.__handlers, **self.__settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.httpserver.HTTPServer(App())
    app.listen(options.port)
    print('Development server is running at http://IP:%s/' % options.port)
    print('Quit the server with Control-C')
    tornado.ioloop.IOLoop.current().start()

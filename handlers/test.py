#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Author: YouShumin
@Date: 2019-12-13 15:37:14
@LastEditTime: 2019-12-31 15:20:03
@LastEditors: YouShumin
@Description: 
@FilePath: /cute_ansible/handlers/test.py
'''

import json
import logging
from oslo.form.form import form_error
from oslo.web.requesthandler import MixinRequestHandler
from oslo.web.route import route
from tornado import gen
from tornado.options import options, define
# from configs.setting import MQ_CLIENT_EXCHANGE, MQ_CLIENT_ROUTING_KEY
LOG = logging.getLogger(__name__)


@route("/test/mq/")
class TestHandler(MixinRequestHandler):
    
    @gen.coroutine
    def get(self):
        if options.debug:
            msg = "It's must be run debug... This is only test"
            return self.send_fail(msg=msg)
        hostinfo = [
            dict(host="192.168.2.132",
                 port=22051,
                 user="root",
                 password="",
                 ansible_ssh_private_key_file="~/.ssh/youshumin"),
        ]
        mq_server = self.application.mq_server

        data = dict(msg_id="2019-12-15",
                    msg_task="setup",
                    msg_data=hostinfo,
                    msg_return=True)

        yield mq_server.send_msg(json.dumps(data), MQ_CLIENT_EXCHANGE,
                                 MQ_CLIENT_ROUTING_KEY)
        return self.send_ok(data="")

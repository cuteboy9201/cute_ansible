#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Author: YouShumin
@Date: 2019-12-31 14:59:55
@LastEditTime : 2020-01-09 01:55:49
@LastEditors  : YouShumin
@Description: 接受rabbitmq发送过来的任务
@FilePath: /cute_ansible/task/recevice.py
'''

import json
import logging
from tornado import gen
from handlers.ansible.modules import AnsibleRunApi
from oslo.task.rabbitmq import TornadoAdapter
from utils.tools import (create_password, create_ssh_rsa, make_auth_file,
                         sha512_password)

LOG = logging.getLogger(__name__)


class ReceiveHandler(object):
    def __init__(self, body):
        try:
            self.body = json.loads(body)
            self.msg_id = self.body.get("msg_id")
            self.msg_data = self.body.get("msg_data")
            self.msg_backable = self.body.get("msg_backable")
            self.msg_return = self.body.get("msg_return")
            self.hostinfo = self.body.get("hostinfo")
            LOG.info("recevie msg_data: %s", self.msg_data)
            self._handler_hostinfo()    
            LOG.info(self.body)
        except Exception as error:
            self.body = dict()
            LOG.error("init error: %s", error)
            LOG.warn("receive body: %s", body)

    def _handler_hostinfo(self):
        """处理self.msg_auth"""
        self.msg_auth = []
        for item in self.hostinfo:
            if item.get("ansible_ssh_private_key_file", None):
                code, keyfile = make_auth_file(
                    item.get("ansible_ssh_private_key_file", None))
                if code:
                    item["ansible_ssh_private_key_file"] = keyfile
                    item["password"] = ""
            self.msg_auth.append(item)
        logging.info("auth_msg: %s", self.msg_auth)
   
    @property
    def get_result(self):
        return self.return_data

    @gen.coroutine
    def handler(self):
        task_type = self.msg_data.get("task_type")
        if task_type == "create_user":
            yield self.create_user()
        elif task_type == "setup":
            yield self.task_setup()
        raise gen.Return(self)

    @gen.coroutine
    def create_user(self):
        """
            name: 用户名
            password: 密码
            shell: 
            state: 创建或者删除
            home: 
        """
        try:
            password = create_password()
            crypt_password = sha512_password(password)
            args = dict(name=self.msg_data.get("user"),
                        password=crypt_password,
                        state=self.msg_data.get("state"),
                        shell=self.msg_data.get("shell", "/bin/bash"))
            api = AnsibleRunApi(self.msg_auth)
            api.module("user", args)
            if api.status:
                pub, pri = create_ssh_rsa()
                return_data = dict(password=password,
                                   sshPirKey=str(pri, encoding="utf-8"),
                                   sshPubKey=bytes.decode(pub),
                                   staus=True,
                                   user=self.msg_data.get("user"))
            else:
                return_data = api.reps
            self.return_data = dict(msg_id=self.msg_id,
                                    msg_data=return_data,
                                    msg_task="user")
        except Exception as e:
            self.return_data = {}
            LOG.warning("task_setup run fail: {}".format(e))
        else:
            LOG.info("return_data: %s", self.return_data)

    @gen.coroutine
    def task_setup(self):
        """
            获取服务器基本信息
        """
        try:
            api = AnsibleRunApi(self.msg_auth)
            api.module("setup","")
            self.return_data = dict(msg_id=self.msg_id,
                                    msg_task="setup",
                                    msg_data=api.reps)            
        except Exception as e:
            self.return_data = {}
            LOG.warning("task_setup run fail: {}".format(e))
        else:
            LOG.info("return_data: %s", self.return_data)
    
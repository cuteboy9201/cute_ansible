# -*- coding: utf-8 -*-
'''
@Author: your name
@Date: 2019-12-13 14:07:10
@LastEditTime : 2019-12-31 15:10:23
@LastEditors  : YouShumin
@Description: 接受来自rabbitmq的信息[作为消费者]
@FilePath: /cute_ansible/handlers/client_hanlder.py
'''
import logging
from utils.tools import make_auth_file
from handlers.ansible.modules import AnsibleRunApi
import json
from utils.tools import create_password, sha512_password, create_ssh_rsa

LOG = logging.getLogger(__name__)


class MQTaskHandler(object):
    """
        结构body参数 json格式
        返回return_data json格式
    """
    def __init__(self, body):
        self.return_data = {}
        self.run_status = False
        self.req_data = body
        self.__body_analysis()

    def __body_analysis(self):
        self.msg_id = ""  # 返回消息的时候对应的数据
        self.msg_task = ""  # 处理该消息应该使用什么方法函数等
        self.msg_auth = ""  # 主机认证信息
        self.msg_args = ""
        self.msg_return = False  # 是否需要返回数据
        try:
            req_data = json.loads(self.req_data)
            self.msg_id = req_data.get("msg_id", None)
            self.msg_task = req_data.get("msg_task", None)
            self.msg_auth = req_data.get("msg_auth", None)
            self.msg_return = req_data.get("msg_return", False)
            self.msg_args = req_data.get("msg_args", None)
            self.__handler_hostinfo()
            self.__handler_data()
        except Exception as e:
            LOG.warning("req_data: {}".format(self.req_data))
            LOG.warning("body analysis body fail: %s", str(e))
            self.run_status = False
            self.return_data = {}
        else:
            if not self.msg_id or not self.msg_task or not self.msg_auth:
                LOG.warning("req_data: {}".format(self.req_data))
                self.run_status = False
                self.return_data = {}

    def __handler_data(self):
        """
            添加或者修改这里任务 对应 AnsibleBaseModule中的方法
        """
        if self.msg_task == "setup":
            self.task_setup()
        elif self.msg_task == "user":
            self.api_user()

    @property
    def response(self):
        if self.run_status and self.return_data and self.msg_return:
            return self.return_data
        elif self.run_status and not self.msg_return:
            return "not_return"
        elif not self.run_status:
            return "run_fail"

    def __handler_hostinfo(self):
        """
            处理self.msg_auth
        """
        for item in self.msg_auth:
            if item.get("ansible_ssh_private_key_file", None):
                code, keyfile = make_auth_file(
                    item.get("ansible_ssh_private_key_file", None))
                if code:
                    item["ansible_ssh_private_key_file"] = keyfile
                    item["password"] = ""

    def task_setup(self):
        try:
            api = AnsibleRunApi(self.msg_auth)
            sysinfo = api.sys_info()
            self.return_data = dict(msg_id=self.msg_id,
                                    msg_task=self.msg_task,
                                    msg_data=sysinfo)
        except Exception as e:
            LOG.warning("task_setup run fail: {}".format(e))
            self.run_status = False
        else:
            self.run_status = True

    def api_user(self):
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
            args = dict(name=self.msg_args.get("user"),
                        password=crypt_password,
                        state=self.msg_args.get("state"),
                        shell=self.msg_args.get("shell", "/bash/shell"))
            api = AnsibleRunApi(self.msg_auth)
            api.module(self.msg_task, args)
            if api.status:
                pub, pri = create_ssh_rsa()
                return_data = dict(password=password,
                                   sshPirKey=str(pri, encoding="utf-8"),
                                   sshPubKey=bytes.decode(pub),
                                   staus=True,
                                   user=self.msg_args.get("user"))
            else:
                return_data = api.reps
            self.return_data = dict(msg_id=self.msg_id,
                                    msg_task=self.msg_task,
                                    msg_data=return_data)
        except Exception as e:
            LOG.warning("task_setup run fail: {}".format(e))
            self.run_status = False
        else:
            self.run_status = True
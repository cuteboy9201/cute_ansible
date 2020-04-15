'''
@Author: your name
@Date: 2019-12-13 10:55:08
@LastEditTime: 2019-12-19 17:00:02
@LastEditors: your name
@Description: In User Settings Edit
@FilePath: /cute_ansible/rpc/rabbit.py
'''
from oslo.task import mq_server
from oslo.task import mq_client
import pika
import logging
import uuid
import json
from configs.setting import MQ_SERVER_EXCHANGE, MQ_SERVER_ROUTING_KEY
from handlers import client_hanlder
LOG = logging.getLogger(__name__)


class RabbitClient(mq_client.PikaConsumer):
    def handler_body(self, body):

        taskHandler = client_hanlder.MQTaskHandler(body)
        return_data = taskHandler.response
        if return_data and return_data == "not_return":
            return True, {}
        elif return_data and return_data == "run_fail":
            return False, {}
        elif return_data:
            return True, return_data
        else:
            return False, {}


class RabbitServer(mq_server.PikaPublisher):
    """
        调用 send_msg()生成任务
            body=dict(msg_id="", msg_type="ansible", msg_return=True, data=data)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props = pika.BasicProperties(reply_to=self.ROUTING_KEY,
                                          message_id=self.EXCHANGE)

    def handler_body(self, msg):
        """
            处理回复信息 本项目不会主动发送请求,仅测试时候使用
        """
        LOG.info("接受回复信息:{}".format(msg))
        return True
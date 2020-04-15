#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author: Youshumin
@Date: 2019-11-12 16:05:49
@LastEditors  : YouShumin
@LastEditTime : 2019-12-31 15:22:41
@Description: 
'''
RBAC_NAME = "rbac"
RBAC_DB = "mysql+pymysql://rbac:123456@192.168.2.69:12502/cute_rbac"
RBAC_DB_ECHO = False
ADMIN_LIST = ["youshumin", "superuser"]

MQ_URL = "amqp://admin:admin@192.168.2.132:5672/my_vhost"

# RABBITMQ_SERVER
MQ_SERVER_QUEUE = "cute_ansible_queue"
MQ_SERVER_EXCHANGE = "cute_ansible_exchange"
MQ_SERVER_ROUTING_KEY = "cute_ansible_routing_key"
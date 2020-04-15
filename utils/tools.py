#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@Author: YouShumin
@Date: 2019-12-18 16:44:37
@LastEditTime : 2020-01-03 03:55:31
@LastEditors  : YouShumin
@Description: 
@FilePath: /cute_ansible/utils/tools.py
'''
import base64
import logging
import os

import rsa
from configs.setting import PATH_APP_ROOT
from oslo.util import create_id

LOG = logging.getLogger(__name__)


def make_auth_file(key):
    tmp_key_file = "%s/%s/.%s" % (PATH_APP_ROOT, "keys", create_id())
    status, msg = check_ssh_key(key)
    if status:
        with open(tmp_key_file, "wb+") as tkf:
            tkf.write(msg)
            os.system("chmod 600 %s" % tmp_key_file)
            return True, tmp_key_file
    else:
        return False, ""


def check_ssh_key(sshkey):
    try:
        pri_key = rsa.PrivateKey.load_pkcs1(sshkey)
        pri_file = pri_key.save_pkcs1()
        return True, pri_file
    except Exception as e:
        LOG.warning("check_ssh_key fail: %s", e)
        LOG.warning("check_ssh_key error: {}".format(str(sshkey)))
        return False, ""


def create_ssh_rsa():
    from cryptography.hazmat.primitives import serialization as crypto_serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend as crypto_default_backend

    key = rsa.generate_private_key(backend=crypto_default_backend(),
                                   public_exponent=65537,
                                   key_size=2048)
    private_key = key.private_bytes(crypto_serialization.Encoding.PEM,
                                    crypto_serialization.PrivateFormat.PKCS8,
                                    crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH)

    return public_key, private_key


def create_password():
    import re
    import random
    import string
    while True:
        password_list = random.sample(string.ascii_letters + string.digits, 18)
        password = "".join(password_list)
        if re.search('[0-9]', password) and re.search(
                '[A-Z]', password) and re.search('[a-z]', password):
            break
    return password


def sha512_password(password):
    from passlib.hash import sha512_crypt
    import getpass
    scypy_password = sha512_crypt.using(rounds=5000).hash(password)
    return scypy_password


if __name__ == "__main__":
    password = create_password()
    print(password)
    scpyt_pass = sha512_password(password)
    print(scpyt_pass)

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import json

from activateTools import  get_hardware_info


class ActivationSystem:
    def __init__(self):
        self.activation_file = "activation.key"
        self.salt = b"sk-ltd-00123"  # 建议存储在安全位置

    def generate_activation_key(self, fingerprint):
        # 使用密钥派生函数增强安全性
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(fingerprint.encode())

    def save_activation(self, key):
        # 添加随机混淆数据
        obfuscated = os.urandom(16) + key + os.urandom(16)
        with open(self.activation_file, 'wb') as f:
            f.write(obfuscated)

    def validate_activation(self):
        if not os.path.exists(self.activation_file):
            return False

        with open(self.activation_file, 'rb') as f:
            data = f.read()

        # 提取真实密钥
        try:
            stored_key = data[16:-16]
            current_fingerprint = get_hardware_info()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
                backend=default_backend()
            )
            kdf.verify(current_fingerprint.encode(), stored_key)
            return True
        except:
            return False

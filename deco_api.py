"""
TP-Link Deco API client for fetching WiFi client data.
Based on the Home Assistant integration by amosyuen.
"""
import base64
import hashlib
import json
import math
import re
import secrets
from urllib.parse import quote_plus

import requests
import urllib3
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

urllib3.disable_warnings()

AES_KEY_BYTES = 16
MIN_AES_KEY = 10 ** (AES_KEY_BYTES - 1)
MAX_AES_KEY = (10 ** AES_KEY_BYTES) - 1
PKCS1_v1_5_HEADER_BYTES = 11


def byte_len(n):
    return (int(math.log2(n)) + 8) >> 3


def rsa_encrypt(n, e, plaintext):
    public_key = RSA.construct((n, e)).publickey()
    encryptor = PKCS1_v1_5.new(public_key)
    block_size = byte_len(n)
    bytes_per_block = block_size - PKCS1_v1_5_HEADER_BYTES
    encrypted_text = ""
    index = 0
    while index < len(plaintext):
        chunk_size = min(bytes_per_block, len(plaintext) - index)
        content = plaintext[index:index + chunk_size]
        encrypted_text += encryptor.encrypt(content).hex()
        index += chunk_size
    return encrypted_text


def aes_encrypt(key, iv, plaintext):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def aes_decrypt(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


class DecoAPI:
    def __init__(self, host, username, password):
        self.host = f"https://{host}" if not host.startswith("http") else host
        self.username = username
        self.password = password
        self.aes_key = None
        self.aes_key_bytes = None
        self.aes_iv = None
        self.aes_iv_bytes = None
        self.password_rsa_n = None
        self.password_rsa_e = None
        self.sign_rsa_n = None
        self.sign_rsa_e = None
        self.seq = None
        self.stok = None
        self.cookie = None

    def _generate_aes(self):
        self.aes_key = secrets.randbelow(MAX_AES_KEY - MIN_AES_KEY) + MIN_AES_KEY
        self.aes_iv = secrets.randbelow(MAX_AES_KEY - MIN_AES_KEY) + MIN_AES_KEY
        self.aes_key_bytes = str(self.aes_key).encode("utf-8")
        self.aes_iv_bytes = str(self.aes_iv).encode("utf-8")

    def _fetch_keys(self):
        resp = self._post_raw(
            f"{self.host}/cgi-bin/luci/;stok=/login",
            params={"form": "keys"},
            data=json.dumps({"operation": "read"}),
        )
        keys = resp["result"]["password"]
        self.password_rsa_n = int(keys[0], 16)
        self.password_rsa_e = int(keys[1], 16)

    def _fetch_auth(self):
        resp = self._post_raw(
            f"{self.host}/cgi-bin/luci/;stok=/login",
            params={"form": "auth"},
            data=json.dumps({"operation": "read"}),
        )
        auth = resp["result"]
        self.sign_rsa_n = int(auth["key"][0], 16)
        self.sign_rsa_e = int(auth["key"][1], 16)
        self.seq = auth["seq"]

    def login(self):
        self._generate_aes()
        self._fetch_keys()
        self._fetch_auth()

        password_encrypted = rsa_encrypt(
            self.password_rsa_n, self.password_rsa_e, self.password.encode()
        )
        login_payload = {
            "params": {"password": password_encrypted},
            "operation": "login",
        }
        resp = self._post_raw(
            f"{self.host}/cgi-bin/luci/;stok=/login",
            params={"form": "login"},
            data=self._encode_payload(login_payload),
        )
        data = self._decrypt_data(resp["data"])
        error_code = data.get("error_code")
        if error_code != 0:
            raise Exception(f"Login failed: {data}")
        self.stok = data["result"]["stok"]
        return True

    def list_devices(self):
        payload = {"operation": "read"}
        resp = self._post_auth(
            f"{self.host}/cgi-bin/luci/;stok={self.stok}/admin/device",
            params={"form": "device_list"},
            data=self._encode_payload(payload),
        )
        data = self._decrypt_data(resp["data"])
        devices = data["result"]["device_list"]
        for d in devices:
            nick = d.get("custom_nickname")
            if nick:
                try:
                    d["custom_nickname"] = base64.b64decode(nick).decode()
                except Exception:
                    pass
        return devices

    def list_clients(self, deco_mac="default"):
        payload = {"operation": "read", "params": {"device_mac": deco_mac}}
        resp = self._post_auth(
            f"{self.host}/cgi-bin/luci/;stok={self.stok}/admin/client",
            params={"form": "client_list"},
            data=self._encode_payload(payload),
        )
        data = self._decrypt_data(resp["data"])
        clients = data["result"]["client_list"]
        for c in clients:
            try:
                c["name"] = base64.b64decode(c["name"]).decode()
            except Exception:
                pass
        return clients

    def _post_raw(self, url, params, data):
        """POST without auth cookie (for login flow)."""
        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.host}/webpages/index.html",
            "Origin": self.host,
        }
        if self.cookie:
            headers["Cookie"] = self.cookie
        resp = requests.post(url, params=params, data=data, headers=headers,
                             timeout=10, verify=False)
        resp.raise_for_status()
        # Capture cookie
        set_cookie = resp.headers.get("Set-Cookie", "")
        match = re.search(r"(sysauth=[a-f0-9]+)", set_cookie)
        if match:
            self.cookie = match.group(1)
        return resp.json()

    def _post_auth(self, url, params, data):
        """POST with auth cookie (for authenticated requests)."""
        if not self.cookie or not self.stok:
            raise Exception("Not logged in")
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "Cookie": self.cookie,
            "Origin": self.host,
            "Referer": f"{self.host}/webpages/index.html",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }
        resp = requests.post(url, params=params, data=data, headers=headers,
                             timeout=10, verify=False)
        if resp.status_code == 403:
            raise Exception(f"403 Forbidden - cookie={self.cookie}")
        resp.raise_for_status()
        return resp.json()

    def _encode_payload(self, payload):
        data = self._encode_data(payload)
        sign = self._encode_sign(len(data))
        return f"sign={sign}&data={quote_plus(data)}"

    def _encode_sign(self, data_len):
        seq_with_len = self.seq + data_len
        auth_hash = hashlib.md5(f"{self.username}{self.password}".encode()).digest().hex()
        sign_text = f"k={self.aes_key}&i={self.aes_iv}&h={auth_hash}&s={seq_with_len}"
        return rsa_encrypt(self.sign_rsa_n, self.sign_rsa_e, sign_text.encode())

    def _encode_data(self, payload):
        payload_json = json.dumps(payload, separators=(",", ":"))
        encrypted = aes_encrypt(self.aes_key_bytes, self.aes_iv_bytes, payload_json.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_data(self, data):
        decoded = base64.b64decode(data)
        decrypted = aes_decrypt(self.aes_key_bytes, self.aes_iv_bytes, decoded)
        num_padding = int(decrypted[-1])
        decrypted = decrypted[:-num_padding].decode()
        return json.loads(decrypted)

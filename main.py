import sys
from subprocess import run, PIPE
import email
import gnupg
import hashlib
import time
import json
import os

# retrieve config
config_raw = open(os.path.abspath(os.path.dirname(__file__)) + '/config.json', 'r')
config = json.loads(config_raw.read())

# init gnupg
gpg = gnupg.GPG(gnupghome=config["gnupghome"])
gpg.encoding = "UTF-8"
uids = list()
for key in gpg.list_keys():
    uids = uids + key["uids"]


def encrypt_message(message, to):
    if message.get_content_type() == 'multipart/encrypted':
        return message

    encrypted_message = email.message.Message()

    # generating boundary and content type header
    h = hashlib.new('sha256')
    h.update(time.time().__str__().encode('ascii'))
    boundary = '---------------------------' + h.hexdigest()
    encrypted_message.add_header('Content-Type', 'multipart/encrypted',
        protocol='application/pgp-encrypted', boundary=boundary
    )

    # force content in utf-8 before encrypting
    content = None
    if message.get_param('charset') != None:
        content = message.as_bytes().decode(message.get_param('charset'))
    else:
        content = message.as_string()
    encrypted_message.set_param('charset', 'UTF-8')

    # encrypting
    body = gpg.encrypt(content, to, always_trust=True).__str__()

    preamble = email.message.Message()
    preamble.add_header('Content-Type', 'application/pgp-encrypted')
    preamble.add_header('Version', '1')
    encrypted_message.attach(preamble)

    content = email.message.Message()
    content.add_header('Content-Type', 'application/octet-stream')
    content.set_payload(body)
    encrypted_message.attach(content)

    return encrypted_message

def restore_headers(original, encrypted):
    for t in original.items():
        if t[0] != 'Content-Type' and t[0] != 'Content-Transfer-Encoding':
            encrypted[t[0]] = t[1]

def send(to, mail):
    if config['debug'] == True:
        print(mail.as_string())
    else:
        p = run(['/usr/sbin/sendmail', '-G', '-i', to], stdout=PIPE, stderr=PIPE, encoding=mail.get_content_charset('utf8'), input=mail.as_string())

def handle(raw, to):
    original_mail = email.message_from_string(raw)
    try:
        uid = [x for x in uids if to in x]
        if len(uid) > 0:
            encrypted_mail = encrypt_message(original_mail, to)
            restore_headers(original_mail, encrypted_mail)
            send(to, encrypted_mail)
            return
    except Exception as err:
        print(err)
    send(to, original_mail)

    
for to in sys.argv[1:]:
    handle(sys.stdin.read(), to)

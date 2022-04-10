import sys
from subprocess import run, PIPE
import email
import gnupg
import hashlib
import time

gpg = gnupg.GPG(gnupghome='/home/gpg-filter/.gnupg')
uids = list()
for key in gpg.list_keys():
    uids = uids + key["uids"]

def encrypt_message(message, to):
    body = gpg.encrypt(message.as_string(), to, always_trust=True).__str__()

    h = hashlib.new('sha256')
    h.update(time.time().__str__().encode('ascii'))
    boundary = '---------------------------' + h.hexdigest()
    encrypted_message = email.message.Message()
    encrypted_message.add_header('Content-Type', 'multipart/encrypted',
        protocol='application/pgp-encrypted', boundary=boundary
    )

    preamble = email.message.Message()
    preamble.add_header('Content-Type', 'application/pgp-encrypted')
    preamble.add_header('Version', '1')
    encrypted_message.attach(preamble)

    content = email.message.Message()
    content.add_header('Content-Type', 'application/octet-stream')
    content.set_payload(body)
    encrypted_message.attach(content)

    return encrypted_message

def extract_main_body(message):
    main_body = email.message.Message()
    for param in message.get_params():
        if(param[1] == ''):
            main_body.set_type(param[0])
        else:
            main_body.set_param(param[0], param[1])

    payload = message.get_payload()

    if(type(payload) == str):
        main_body.set_payload(payload)
    else:
        for p in payload:
            main_body.attach(p)

    return main_body

def replace_main_body(message, body):
    for param in body.get_params():
        if(param[1] == ''):
            message.set_type(param[0])
        else:
            message.set_param(param[0], param[1])
    
    payload = body.get_payload()
    message.set_payload(None)
    if(type(payload) == str):
        message.set_payload(payload)
    else:
        for p in payload:
            message.attach(p)

def send(to, mail):
    p = run(['/usr/sbin/sendmail', '-G', '-i', to], stdout=PIPE, stderr=PIPE, encoding='ascii', input=mail.as_string())
    return

def handle(raw, to):
    original_mail = email.message_from_string(raw)
    uid = [x for x in uids if to in x]
    if len(uid) > 0:
        body = extract_main_body(original_mail)
        encrypted_body = encrypt_message(body, to)
        replace_main_body(original_mail, encrypted_body)
    send(to, original_mail)

    
for to in sys.argv[1:]:
    handle(sys.stdin.read(), to)
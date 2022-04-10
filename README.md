# GPG Filter

This script is a simple content filter for Postfix.
It encrypts incoming emails using public keys saved in the configured gnupg home.
if no matching public key is available, the incoming e-mail will not be encrypted.

It was created as a [RFC 3156](https://datatracker.ietf.org/doc/rfc3156/) compliant alternative to [GPG-mailgate](https://github.com/fkrone/gpg-mailgate), since emails encrypted with the latter are not readable for most of the email client with OpenPGP support.

## Requirements 

* gnupg
* Python 3.6
* python-gnupg

## How to use 

Please read the [official postfix documentation](https://www.postfix.org/FILTER_README.html#simple_filter).

1. Create a gpg-filter user with a home directory
2. Download the script and keep its path in mind, make the gpg-filter user owner of the script's directory
3. Edit /etc/postfix/master.cf and add the following at the end of the file

```
gpg-filter    unix  -       n       n       -       10      pipe
    flags=Rq user=gpg-filter null_sender=
    argv=/usr/bin/python3 path/to/gpg-filter/main.py ${recipient}
```

4. Edit /etc/postfix/master.cf and edit the smtp service so it will use gpg-filter as a content-filter

```
# =============================================================
# service type  private unpriv  chroot  wakeup  maxproc command
#               (yes)   (yes)   (yes)   (never) (100)
# =============================================================
smtp      inet  ...other stuff here, do not change...   smtpd
    -o content_filter=gpg-filter:dummy
```

5. Edit the gpg-filter config.json file and set `gnupghome` to folder .gnupg in the gpg-filter user's home directory 
6. You can now add public keys to the gpg-filter user keyring with
```
sudo -u gpg-filter /usr/bin/gpg --import /some/public.key
```
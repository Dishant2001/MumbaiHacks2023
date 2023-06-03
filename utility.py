import hashlib


def hashPassword(password,salt):
    hash_object = hashlib.md5()

    passwordComplete = password + salt
    hash_object.update(passwordComplete.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig
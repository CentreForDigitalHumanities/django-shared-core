from django.contrib.auth.hashers import (PBKDF2PasswordHasher,
                                         UnsaltedMD5PasswordHasher)


class PBKDF2WrappedMD5PasswordHasher(PBKDF2PasswordHasher):
    algorithm = 'pbkdf2_wrapped_md5'

    def encode_md5_hash(self, md5_hash, salt, iterations=None):
        return super().encode(md5_hash, salt, iterations)

    def encode(self, password, salt, iterations=None):
        md5_hash = UnsaltedMD5PasswordHasher().encode(password, '')
        return self.encode_md5_hash(md5_hash, salt, iterations)


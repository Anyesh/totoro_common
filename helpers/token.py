import jwt

from helpers.exceptions import ApiException


def generate_token(user_data, secret_key, algorithm):
    return jwt.encode(
        user_data,
        secret_key,
        algorithm=algorithm,
    )


def decode_token(token, secret_key, algorithm):
    try:
        return jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
        )
    except (
        jwt.exceptions.InvalidSignatureError,
        jwt.exceptions.DecodeError,
        jwt.exceptions.InvalidAlgorithmError,
        jwt.exceptions.InvalidKeyError,
    ):
        raise ApiException("Unauthorized: Invalid token", 401)

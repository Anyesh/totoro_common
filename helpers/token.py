import jwt


def generate_token(user_data, secret_key, algorithm):
    return jwt.encode(
        user_data,
        secret_key,
        algorithm=algorithm,
    )


def decode_token(token, secret_key, algorithm):
    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
    )

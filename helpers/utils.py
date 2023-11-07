import re


def regex_password_validator(password):
    if not re.search(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&].{7,}$",
        password,
    ):
        raise ValueError(
            "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number and one special character"
        )

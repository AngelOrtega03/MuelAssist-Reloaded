import re

def password_check(password):
    Flag = True
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length = len(password) < 8

    # searching for digits
    digit = re.search(r"\d", password)

    # searching for uppercase
    uppercase = re.search(r"[A-Z]", password)

    # searching for lowercase
    lowercase = re.search(r"[a-z]", password)

    # searching for symbols
    symbol = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password)

    # overall result
    if length and digit and uppercase and lowercase and symbol:
        return Flag
    else:
        Flag = False
        return Flag
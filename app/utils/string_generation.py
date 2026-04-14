import secrets

def generate_otp():
    return "".join((secrets.choice("1234567890")) for _ in range(0,4))

if __name__ == "__main__":
    otp = generate_otp()
    print(otp)
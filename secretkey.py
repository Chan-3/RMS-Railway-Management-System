import secrets

# Generate a random secret key (64-hex chars = 32 bytes)
secret_key = secrets.token_hex(32)

# File to store keys
filename = "secrets.txt"

# Append key to file
with open(filename, "a") as f:
    f.write(f"SECRET_KEY={secret_key}\n")

print("Generated SECRET_KEY and appended to secrets.txt:")
print(secret_key)

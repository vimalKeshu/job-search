import secrets
import string

def generate_client_secret(length):
    # Define the character set for the random string
    characters = string.ascii_letters + string.digits

    # Generate the random string
    client_secret = ''.join(secrets.choice(characters) for _ in range(length))

    return client_secret

# Generate a client secret with a length of 64 characters
client_secret = generate_client_secret(64)
print(client_secret)
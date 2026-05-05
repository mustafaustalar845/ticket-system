import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AES_SECRET_KEY must be a valid Fernet key (32-byte URL-safe base64-encoded string)
# You can generate one using Fernet.generate_key()
SECRET_KEY = os.getenv("AES_SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("AES_SECRET_KEY not found in environment variables or .env file")

# Initialize Fernet cipher
cipher_suite = Fernet(SECRET_KEY.encode())

def encrypt_data(plain_text: str) -> str:
    """
    Encrypts a string using AES-256 (Fernet) symmetric encryption.
    
    Args:
        plain_text (str): The raw text to be encrypted.
        
    Returns:
        str: The encrypted cipher text as a URL-safe base64 string.
        
    Raises:
        ValueError: If plain_text is not a string.
    """
    if not isinstance(plain_text, str):
        raise ValueError("Data to encrypt must be a string")
    
    encoded_text = plain_text.encode('utf-8')
    encrypted_text = cipher_suite.encrypt(encoded_text)
    return encrypted_text.decode('utf-8')

def decrypt_data(cipher_text: str) -> str:
    """
    Decrypts a Fernet-encrypted cipher text back to its original plain text.
    
    Args:
        cipher_text (str): The encrypted string (base64 encoded).
        
    Returns:
        str: The decrypted original plain text.
        
    Raises:
        ValueError: If decryption fails or input is invalid.
    """
    try:
        if not isinstance(cipher_text, str):
            raise ValueError("Cipher text must be a string")
            
        decoded_cipher = cipher_text.encode('utf-8')
        decrypted_text = cipher_suite.decrypt(decoded_cipher)
        return decrypted_text.decode('utf-8')
    except Exception as e:
        # Re-raise with a cleaner message for the team
        raise ValueError(f"Decryption failed. Ensure the key and cipher text are valid. Error: {str(e)}")

# Example usage for testing (uncomment if needed)
# if __name__ == "__main__":
#     test_msg = "Sensitive Data 123"
#     encrypted = encrypt_data(test_msg)
#     print(f"Encrypted: {encrypted}")
#     print(f"Decrypted: {decrypt_data(encrypted)}")

from cryptography.fernet import Fernet

def encrypt_file(input_file_path, output_file_path, key):
    print("enc", key)
    """
    Encrypts a file using Fernet encryption.
    
    Args:
    - input_file_path: Path to the input file to be encrypted.
    - output_file_path: Path to save the encrypted output file.
    - key: Fernet encryption key.
    """
    cipher_suite = Fernet(key)
    
    with open(input_file_path, 'rb') as file:
        file_data = file.read()
        
    encrypted_data = cipher_suite.encrypt(file_data)

    with open(output_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(input_file_path, output_file_path, key):
    print("dec", key)
    """
    Decrypts a file using Fernet encryption.
    
    Args:
    - input_file_path: Path to the input file to be decrypted.
    - output_file_path: Path to save the decrypted output file.
    - key: Fernet encryption key.
    """
    cipher_suite = Fernet(key)

    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = cipher_suite.decrypt(encrypted_data)

    with open(output_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)


# Generate a key
key = Fernet.generate_key()

# Encrypt a file
encrypt_file('drive\\asd.py', 'drive\des.py', key)

# Decrypt a file
decrypt_file('drive\des.py', 'drive\sss.py', key)

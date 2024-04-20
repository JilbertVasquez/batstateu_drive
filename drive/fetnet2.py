from cryptography.fernet import Fernet

def encrypt_file(input_file_path, output_file_path, key):
    cipher_suite = Fernet(key)
    
    with open(input_file_path, 'rb') as file:
        file_data = file.read()
        
    encrypted_data = cipher_suite.encrypt(file_data)

    with open(output_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def decrypt_file(input_file_path, output_file_path, key):
    cipher_suite = Fernet(key)

    with open(input_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = cipher_suite.decrypt(encrypted_data)

    with open(output_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

# Generate a key
key = Fernet.generate_key()

# Save the key to a text file
with open('key.txt', 'wb') as key_file:
    key_file.write(key)

# Read the key from the text file
with open('key.txt', 'rb') as key_file:
    key = key_file.read()

# Encrypt a file
# encrypt_file('D:\\batstateu_drive\uploadedfiles\\folder1\123\\a.txt', 'D:\\batstateu_drive\uploadedfiles\\folder1\123\\a2.txt', key)

# # Decrypt a file
# decrypt_file('D:\\batstateu_drive\uploadedfiles\\folder1\123\\a2.txt', 'D:\batstateu_drive\\temp_folder\sss.py', key)


# Encrypt a file
encrypt_file(r'\\DESKTOP-UUTKA7R\uploadedfiles\folder1\123\a.txt', r'\\DESKTOP-UUTKA7R\uploadedfiles\folder1\123\a2.txt', key)

# Decrypt a file
decrypt_file(r'\\DESKTOP-UUTKA7R\uploadedfiles\folder1\123\a2.txt', r'D:\batstateu_drive\temp_folder\aaa.txt', key)
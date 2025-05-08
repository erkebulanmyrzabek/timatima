import gnupg
import os
import subprocess
import smtplib
import logging
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger('mail_service')

# Настраиваем GnuPG
GPG_HOME = os.path.join(settings.BASE_DIR, 'gpg_home')
os.makedirs(GPG_HOME, exist_ok=True)
gpg = gnupg.GPG(gnupghome=GPG_HOME)


def generate_pgp_key_pair(user_email, passphrase):
    """
    Генерация PGP ключевой пары для пользователя
    
    Args:
        user_email: Email пользователя
        passphrase: Пароль для защиты ключа
        
    Returns:
        Tuple: (public_key, private_key_encrypted)
    """
    input_data = gpg.gen_key_input(
        name_real=user_email,
        name_email=user_email,
        passphrase=passphrase,
        key_type="RSA",
        key_length=4096,
        expire_date=0  # Ключ не истекает
    )
    
    key = gpg.gen_key(input_data)
    
    if not key:
        logger.error(f"Не удалось создать ключи для {user_email}")
        return None, None
    
    # Экспортируем публичный ключ
    public_key = gpg.export_keys(key.fingerprint)
    
    # Экспортируем приватный ключ (зашифрованный парольной фразой)
    private_key = gpg.export_keys(key.fingerprint, True, passphrase=passphrase)
    
    return public_key, private_key


def encrypt_with_aes(data, key):
    """
    Шифрует данные с использованием AES-256
    
    Args:
        data: Данные для шифрования (строка или байты)
        key: Ключ шифрования (пароль пользователя)
        
    Returns:
        str: Зашифрованные данные в base64
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Создаем 256-битный ключ из пароля пользователя с использованием SHA-256
    hashed_key = hashlib.sha256(key.encode('utf-8')).digest()
    
    # Генерируем IV (вектор инициализации)
    iv = os.urandom(16)
    
    # Создаем padder для данных, так как AES требует, чтобы данные были кратны размеру блока
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # Создаем шифратор
    cipher = Cipher(algorithms.AES(hashed_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Шифруем данные
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Объединяем IV и зашифрованные данные и кодируем в base64
    result = base64.b64encode(iv + encrypted_data).decode('utf-8')
    
    return result


def decrypt_with_aes(encrypted_data, key):
    """
    Расшифровывает данные, зашифрованные с использованием AES-256
    
    Args:
        encrypted_data: Зашифрованные данные в base64
        key: Ключ шифрования (пароль пользователя)
        
    Returns:
        str: Расшифрованные данные
    """
    # Декодируем base64
    encrypted_bytes = base64.b64decode(encrypted_data)
    
    # Получаем IV (первые 16 байт)
    iv = encrypted_bytes[:16]
    
    # Получаем зашифрованные данные (остаток)
    ciphertext = encrypted_bytes[16:]
    
    # Создаем 256-битный ключ из пароля пользователя с использованием SHA-256
    hashed_key = hashlib.sha256(key.encode('utf-8')).digest()
    
    # Создаем дешифратор
    cipher = Cipher(algorithms.AES(hashed_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Расшифровываем данные
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Удаляем padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    # Возвращаем расшифрованные данные в виде строки
    return data.decode('utf-8')


def save_private_key_encrypted(private_key, passphrase):
    """
    Шифрует приватный ключ паролем с использованием AES-256
    """
    return encrypt_with_aes(private_key, passphrase)


def decrypt_private_key(private_key_encrypted, passphrase):
    """
    Расшифровывает приватный ключ с помощью пароля
    """
    try:
        return decrypt_with_aes(private_key_encrypted, passphrase)
    except Exception as e:
        logger.error(f"Ошибка расшифровки приватного ключа: {e}")
        raise ValueError("Неверный пароль или поврежденный ключ")


def encrypt_message(content, recipient_public_key):
    """
    Шифрует сообщение с использованием публичного ключа получателя
    
    Args:
        content: Содержимое сообщения для шифрования
        recipient_public_key: Публичный ключ получателя
        
    Returns:
        str: Зашифрованное сообщение
    """
    # Импортируем публичный ключ получателя
    import_result = gpg.import_keys(recipient_public_key)
    
    if not import_result or not import_result.fingerprints:
        logger.error("Не удалось импортировать ключ получателя")
        return None
    
    # Шифруем сообщение
    encrypted_data = gpg.encrypt(content, import_result.fingerprints[0], always_trust=True)
    
    if not encrypted_data.ok:
        logger.error(f"Ошибка шифрования: {encrypted_data.status}")
        return None
    
    return str(encrypted_data)


def decrypt_message(encrypted_content, private_key, passphrase):
    """
    Расшифровывает сообщение с использованием приватного ключа
    
    Args:
        encrypted_content: Зашифрованное содержимое сообщения
        private_key: Приватный ключ пользователя (зашифрованный)
        passphrase: Пароль для расшифровки приватного ключа
        
    Returns:
        str: Расшифрованное сообщение
    """
    # Импортируем приватный ключ
    import_result = gpg.import_keys(private_key)
    
    if not import_result or not import_result.fingerprints:
        logger.error("Не удалось импортировать приватный ключ")
        return None
    
    # Расшифровываем сообщение
    decrypted_data = gpg.decrypt(encrypted_content, passphrase=passphrase)
    
    if not decrypted_data.ok:
        logger.error(f"Ошибка расшифровки: {decrypted_data.status}")
        return None
    
    return str(decrypted_data)


def send_email_via_postfix(from_email, to_email, subject, body, attachments=None):
    """
    Отправка письма через Postfix
    
    Args:
        from_email: Email отправителя
        to_email: Email получателя
        subject: Тема письма
        body: Тело письма
        attachments: Список путей к файлам вложений
        
    Returns:
        bool: Успешность отправки
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Добавляем тело письма
        msg.attach(MIMEText(body, 'html'))
        
        # Добавляем вложения, если есть
        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as file:
                        part = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                        msg.attach(part)
        
        # Отправляем через локальный Postfix
        smtp = smtplib.SMTP('localhost')
        smtp.send_message(msg)
        smtp.quit()
        
        logger.info(f"Письмо успешно отправлено от {from_email} к {to_email}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки письма: {str(e)}")
        return False


def check_email_delivery_status(message_id):
    """
    Проверка статуса доставки письма в логах Postfix
    
    Args:
        message_id: ID письма в Postfix
        
    Returns:
        str: Статус доставки (delivered, bounced, deferred, unknown)
    """
    try:
        # Ищем в логах Postfix информацию о письме
        result = subprocess.run(
            ["grep", message_id, "/var/log/mail.log"],
            capture_output=True, text=True
        )
        
        log_entries = result.stdout.strip().split('\n')
        
        if not log_entries or log_entries == ['']:
            return "unknown"
        
        # Анализируем логи для определения статуса
        for entry in log_entries:
            if "status=sent" in entry:
                return "delivered"
            elif "status=bounced" in entry:
                return "bounced"
            elif "status=deferred" in entry:
                return "deferred"
        
        return "unknown"
    except Exception as e:
        logger.error(f"Ошибка проверки статуса доставки: {str(e)}")
        return "unknown" 
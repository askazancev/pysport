import hid
import time

VENDOR_ID = 0x1a86  # Замените на VID вашего устройства
PRODUCT_ID = 0xe010 # Замените на PID вашего устройства

# Пример данных, которые отправим (должны соответствовать спецификации устройства)
# Например: [53 57 00 03 FF 10 44] — первый байт 0x00 — это Report ID
test_data = [0x07, 0x53, 0x57, 0x00, 0x03, 0xFF, 0x10, 0x44]

for d in hid.enumerate():
    if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
        print(d)

try:
    device = hid.device()
    device.open(VENDOR_ID, PRODUCT_ID)
    print(f"Connected to device: {device.get_product_string()}")

    # Установка времени ожидания чтения (в мс)
    device.set_nonblocking(True)

    # Отправка данных (через interrupt OUT transfer за кулисами)
    bytes_written = device.write(test_data)
    print(f"Sent {bytes_written} bytes")

    # Ждем и читаем ответ (через interrupt IN transfer за кулисами)
    for _ in range(10):
        response = device.read(64)  # Максимальная длина пакета
        if response:
            print(f"Received: {response}")
            break
        time.sleep(0.1)

    device.close()

except Exception as e:
    print(f"Error: {e}")


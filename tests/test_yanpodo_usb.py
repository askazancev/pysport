import usb.core
import usb.util

VENDOR_ID = 0x1A86  # Замените на VID вашего устройства
PRODUCT_ID = 0xE010 # Замените на PID вашего устройства


dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if dev is None:
    raise ValueError("Device not found")

dev.set_configuration()

# endpoint адрес для interrupt transfer — узнайте из дескриптора устройства
endpoint = dev[0][(0, 0)][0]  # Обычно первый endpoint

# Отправляем данные
dev.write(endpoint.bEndpointAddress, [0x00, 0xAA, 0xBB, 0xCC])

# Получаем данные
response = dev.read(endpoint.bEndpointAddress | 0x80, 64)
print(response)

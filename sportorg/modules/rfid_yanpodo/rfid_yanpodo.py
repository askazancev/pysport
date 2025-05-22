import ctypes
import os
import time
import logging
from queue import Queue, Empty
from threading import Event, Thread, main_thread
from ctypes import byref, c_int, c_byte
import platform
import os
import sys
import threading
from datetime import datetime
import asyncio

from random import randint
from time import sleep
import serial
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager

from PySide6.QtCore import QThread, Signal
from sportorg.common.otime import OTime
from sportorg.common.singleton import singleton
from sportorg.models import memory
from sportorg.models.memory import race


class YanpodoCommand:
    def __init__(self, command, data=None):
        self.command = command
        self.data = data


class YanpodoThread(QThread):
    def __init__(self, interface, port, queue, stop_event, logger, debug=False):
        super().__init__()
        self.setObjectName(self.__class__.__name__)
        self.interface = interface  # "USB" or "COM"
        self.port = port  # COM port for COM interface
        self._queue = queue
        self._stop_event = stop_event
        self._logger = logger
        self._debug = debug

        self.timeout_list = {}
        self.timeout = race().get_setting("readout_duplicate_timeout", 15000)

        # Определяем базовый путь к DLL
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if platform.system() == "Windows":
            # Загружаем соответствующую DLL
            dll_path_usb = os.path.join(
                base_dir,
                "..",
                "..",
                "..",
                "sportorg",
                "libs",
                "yanpodo",
                "X64",
                "USB",
                "SWHidApi.dll",
            )
            dll_path_com = os.path.join(
                base_dir,
                "..",
                "..",
                "..",
                "sportorg",
                "libs",
                "yanpodo",
                "X64",
                "Com",
                "SWComApi.dll",
            )

            if self.interface == "USB":
                self.reader_dll = ctypes.windll.LoadLibrary(dll_path_usb)
            elif self.interface == "COM":
                self.reader_dll = ctypes.windll.LoadLibrary(dll_path_com)
            else:
                raise ValueError(f"Unsupported interface type: {self.interface}")
        elif platform.system() == "Linux":
            # 1. Явно загружаем libusb в глобальном режиме (RTLD_GLOBAL)
            try:
                libusb = ctypes.CDLL(
                    "/usr/lib/libusb-1.0.so",
                    mode=ctypes.RTLD_GLOBAL,
                )
            except Exception as e:
                print(f"Ошибка загрузки libusb: {e}")
                exit(1)
            # Загружаем .so для Linux
            dll_path_usb = os.path.join(
                base_dir,
                "..",
                "..",
                "..",
                "sportorg",
                "libs",
                "yanpodo",
                "Linux_X64",
                "USB",
                "libSWHidApi.so",
            )
            dll_path_com = os.path.join(
                base_dir,
                "..",
                "..",
                "..",
                "sportorg",
                "libs",
                "yanpodo",
                "Linux_X64",
                "Com",
                "libSWComApi.so",
            )
            try:
                if self.interface == "USB":
                    self.reader_dll = ctypes.CDLL(dll_path_usb)
                elif self.interface == "COM":
                    self.reader_dll = ctypes.CDLL(dll_path_com)
            except Exception as e:
                print(f"Ошибка загрузки {self.interface} библиотеки: {e}")
                exit(1)
            else:
                raise ValueError(f"Unsupported interface type: {self.interface}")
        else:
            raise RuntimeError("Unsupported platform")

    def run(self):
        try:
            if self.interface == "USB":
                self._initialize_usb()
            elif self.interface == "COM":
                self._initialize_com()

            self._logger.info(
                f"Yanpodo reader initialized successfully on {self.interface} interface."
            )

            while not self._stop_event.is_set():
                self._read_tags()

        except Exception as e:
            self._logger.error(f"Error in YanpodoThread: {e}")
        finally:
            self._logger.debug("Stopping YanpodoThread")

    def _initialize_usb(self):
        if platform.system() == "Windows":
            if self.reader_dll.SWHid_GetUsbCount() == 0:
                raise RuntimeError("No USB devices found")
        if self.reader_dll.SWHid_OpenDevice(0) != 1:
            raise RuntimeError("Failed to open USB device")
        self.reader_dll.SWHid_ClearTagBuf()

    def _initialize_com(self):
        if self.reader_dll.SWCom_OpenDevice(self.port, 115200) != 1:
            raise RuntimeError(f"Failed to open COM device on port {self.port}")
        self.reader_dll.SWCom_ClearTagBuf()

    def _read_tags(self):
        arr_buffer = bytes(9182)
        tag_length = c_int(0)
        tag_number = c_int(0)

        if self.interface == "USB":
            ret = self.reader_dll.SWHid_GetTagBuf(
                arr_buffer, byref(tag_length), byref(tag_number)
            )
        elif self.interface == "COM":
            ret = self.reader_dll.SWCom_GetTagBuf(
                arr_buffer, byref(tag_length), byref(tag_number)
            )
        else:
            return

        if tag_number.value > 0:
            self._process_tags(arr_buffer, tag_number.value)

    # def _process_tags(self, arr_buffer, tag_count):
    #     i_length = 0
    #     for _ in range(tag_count):
    #         b_pack_length = arr_buffer[i_length]
    #         epc = ""
    #         for i in range(2, b_pack_length - 1):
    #             epc += hex(arr_buffer[1 + i_length + i]).replace("0x", "").zfill(2)

    #         card_data = {"epc": epc, "time": OTime.now()}
    #         self._logger.info(f"Tag read: {card_data}")  # Логируем данные метки

    #         # Обработка дубликатов
    #         card_id = card_data["epc"]
    #         card_time = card_data["time"]
    #         if card_id in self.timeout_list:
    #             old_time = self.timeout_list[card_id]
    #             if card_time - old_time < OTime(msec=self.timeout):
    #                 self._logger.debug(f"Duplicated result for tag {card_id}, ignoring")
    #                 continue

    #         self.timeout_list[card_id] = card_time
    #         self._queue.put(YanpodoCommand("card_data", card_data), timeout=1)
    #         i_length += b_pack_length + 1

    def _process_tags(self, arr_buffer, tag_count):
        # Для хранения последних card_data и таймеров по epc
        if not hasattr(self, "_epc_timers"):
            self._epc_timers = {}
            self._epc_data = {}

        i_length = 0
        for _ in range(tag_count):
            b_pack_length = arr_buffer[i_length]
            epc = ""
            for i in range(2, b_pack_length - 1):
                epc += hex(arr_buffer[1 + i_length + i]).replace("0x", "").zfill(2)

            card_data = {"epc": epc, "time": OTime.now()}
            self._logger.info(f"Tag read: {card_data}")

            card_id = card_data["epc"]
            card_time = card_data["time"]

            # Сохраняем только результат с максимальным временем
            prev_data = self._epc_data.get(card_id)
            if prev_data is None or card_time > prev_data["time"]:
                self._epc_data[card_id] = card_data

            # Если таймер уже есть, сбрасываем его
            if card_id in self._epc_timers:
                self._epc_timers[card_id].cancel()

            # Запускаем новый таймер на 3 секунды
            def send_result(epc=card_id):
                data = self._epc_data.pop(epc, None)
                self._epc_timers.pop(epc, None)
                if data:
                    try:
                        self._queue.put(YanpodoCommand("card_data", data), timeout=1)
                    except Exception as e:
                        self._logger.error(f"Failed to put card_data: {e}")

            timer = threading.Timer(3, send_result)
            self._epc_timers[card_id] = timer
            timer.start()

            i_length += b_pack_length + 1


class ResultThread(QThread):
    data_sender = Signal(object)

    def __init__(self, queue, stop_event, logger):
        super().__init__()
        self.setObjectName(self.__class__.__name__)
        self._queue = queue
        self._stop_event = stop_event
        self._logger = logger

    def run(self):
        while not self._stop_event.is_set():
            try:
                cmd = self._queue.get(timeout=5)
                if cmd.command == "card_data":
                    result = self._get_result(cmd.data)
                    self.data_sender.emit(result)
            except Empty:
                if not main_thread().is_alive() or self._stop_event.is_set():
                    break
            except Exception as e:
                self._logger.exception(e)
        self._logger.debug("Stopping ResultThread")

    @staticmethod
    def _get_result(card_data):
        result = memory.race().new_result(memory.ResultRfidYanpodo)

        limit = 10**8
        hex_offset = 5000000
        epc = str(card_data["epc"]).replace(" ", "")

        # Если EPC содержит только цифры, используем их напрямую
        # Иначе конвертируем hex -> dec и добавляем offset
        if epc.isdecimal():
            result.card_number = int(epc) % limit
        else:
            result.card_number = (int(epc, 16) + hex_offset) % limit

        result.finish_time = card_data["time"]
        return result


class CardData(BaseModel):
    card_number: str
    finish_time: str
    deviceId: str


@singleton
class YanpodoClient:
    def __init__(self):
        self._queue = Queue()
        self._stop_event = Event()
        self._yanpodo_thread = None
        self._result_thread = None
        self.port = None
        self._logger = logging.getLogger("YanpodoClient")
        self._call_back = None

    def set_call(self, value):
        if self._call_back is None:
            self._call_back = value
        return self

    def _start_yanpodo_thread(self, interface):
        if self._yanpodo_thread is None:
            self._yanpodo_thread = YanpodoThread(
                interface, self.port, self._queue, self._stop_event, self._logger
            )
            self._yanpodo_thread.start()
        elif self._yanpodo_thread.isFinished():
            self._yanpodo_thread = None
            self._start_yanpodo_thread(interface)

    def _start_result_thread(self):
        if self._result_thread is None:
            self._result_thread = ResultThread(
                self._queue,
                self._stop_event,
                self._logger,
            )
            if self._call_back is not None:
                self._result_thread.data_sender.connect(self._call_back)
            self._result_thread.start()
        elif self._result_thread.isFinished():
            self._result_thread = None
            self._start_result_thread()

    def is_alive(self):
        return (
            self._yanpodo_thread is not None
            and self._result_thread is not None
            and not self._yanpodo_thread.isFinished()
            and not self._result_thread.isFinished()
        )

    def start(self, interface="USB"):
        self.port = self.choose_port()
        self._stop_event.clear()
        self._start_yanpodo_thread(interface)
        self._start_result_thread()

        # Запуск сервера в отдельном потоке
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

    def _run_server(self):
        """Запускает сервер FastAPI в отдельном потоке."""
        asyncio.run(self._start_server())

    async def _start_server(self):
        app = FastAPI()

        @app.post("/submit")
        async def receive_data(data: CardData):
            card_data = {
                "epc": data.card_number,
                "time": data.finish_time, #OTime.now(),
            }
            # Обработка данных в отдельном потоке
            threading.Thread(
                target=self._process_remote_data, args=(card_data,)
            ).start()
            return {"status": "received"}

        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    def _process_remote_data(self, card_data):
        """Обрабатывает данные, полученные от удаленных считывателей."""
        arr_buffer = bytes(
            [len(card_data["epc"])] + list(card_data["epc"].encode())
        )
        self._yanpodo_thread._process_tags(arr_buffer, tag_count=1)

    def toggle(self, interface="USB"):
        if self.is_alive():
            self.stop()
        else:
            self.start(interface)

    def choose_port(self):
        return memory.race().get_setting("system_port", "COM4")

    def stop(self):
        self._stop_event.set()
        if self._yanpodo_thread:
            self._yanpodo_thread.wait()


if __name__ == "__main__":
    client = YanpodoClient()
    try:
        client.start(interface="USB")
    except KeyboardInterrupt:
        client.stop()

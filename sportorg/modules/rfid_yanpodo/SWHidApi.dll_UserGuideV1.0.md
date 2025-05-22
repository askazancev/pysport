# SWHidApi.dll  
## User’s Guide V1.0

SWHidApi.DLL is a dynamic link library designed to facilitate RFID application software development.

---

## 1. Function List

SWHidApi.DLL includes the following functions:

### 1.1 General Function

1. `int SWHid_GetUsbCount(void);`
2. `BOOL SWHid_GetUsbInfo(unsigned short iIndex, char *pucDeviceInfo);`
3. `BOOL SWHid_OpenDevice(unsigned short iIndex);`
4. `BOOL SWHid_CloseDevice(void);`
5. `BOOL SWHid_GetDeviceSystemInfo(unsigned char bDevAdr, unsigned char *pucSystemInfo);`
6. `BOOL SWHid_ReadDeviceOneParam(unsigned char bDevAdr, unsigned char pucDevParamAddr, unsigned char *pValue);`
7. `BOOL SWHid_SetDeviceOneParam(unsigned char bDevAdr, unsigned char pucDevParamAddr, unsigned char bValue);`
8. `BOOL SWHid_StopRead(unsigned char bDevAdr);`
9. `BOOL SWHid_StartRead(unsigned char bDevAdr);`
10. `void ( * FunPtrActiveCallback)(int msg, int param1, unsigned char *param2, int param3, unsigned char *param4);`
11. `int SWHid_SetCallback(FUNPTR_ACTIVE_CALLBACK pfAddr);`
12. `BOOL SWHid_InventoryG2(unsigned char bDevAdr, unsigned char *pBuffer, unsigned short *Totallen, unsigned short *CardNum);`
13. `BOOL SWHid_WriteEPCG2(unsigned char bDevAdr, unsigned char *Password, unsigned char *WriteEPC, unsigned char WriteEPClen);`
14. `BOOL SWHid_ReadCardG2(unsigned char bDevAdr, unsigned char *Password, unsigned char Mem, unsigned char WordPtr, unsigned char ReadEPClen, unsigned char *Data);`
15. `BOOL SWHid_WriteCardG2(unsigned char bDevAdr, unsigned char *Password, unsigned char Mem, unsigned char WordPtr, unsigned char Writelen, unsigned char *Writedata);`
16. `BOOL SWHid_RelayOn(unsigned char bDevAdr);`
17. `BOOL SWHid_RelayOff(unsigned char bDevAdr);`

---

## 2. Function Explanation

### 2.1 General Function

#### 2.1.1 `int SWHid_GetUsbCount(void)`

Get the count of connected USB devices.  
**Param:** None  
**Return:** Returns the number of connected USB devices. If no devices are found, returns 0.

---

#### 2.1.2 `BOOL SWHid_GetUsbInfo(unsigned short iIndex, char *pucDeviceInfo)`

Get USB HID value  
**Param:**  
- `iIndex`: HID Index 0,1,2....  
- `pucDeviceInfo`: Pointer to a buffer where the USB HID device information (e.g., device name or identifier) will be stored.  
**Return:** Success return TRUE (1), failed return FALSE (0)

---

#### 2.1.3 `BOOL SWHid_OpenDevice(unsigned short iIndex)`

Open Device.  
**Param:**  
- `iIndex`: HID Index 0,1,2....  
**Return:** Success return 1, failed return 0

---

#### 2.1.4 `BOOL SWHid_CloseDevice(void)`

Close Device  
**Param:** None  
**Return:** Success return 1, failed return 0

---

#### 2.1.5 `BOOL SWHid_GetDeviceSystemInfo(unsigned char bDevAdr, unsigned char *pucSystemInfo)`

GetDeviceInfo. 9Bytes  
**Param:**  
- `bDevAdr`: 0xFF  
- `pucSystemInfo`: SysInfo (9 bytes)  
      - Byte 1: Software Version  
      - Byte 2: Hardware Version  
      - Bytes 3-9: Device Serial Number (DeviceSN)  
**Return:** Success return 1, failed return 0

---

#### 2.1.6 `BOOL SWHid_ReadDeviceOneParam(unsigned char bDevAdr, unsigned char pucDevParamAddr, unsigned char *pValue)`

Get Device One Param  
**Param:**  
- `bDevAdr`: 0xFF  
- `pucDevParamAddr`: Param Addr  
- `pValue`: Return Param Value  
**Return:** Success return 1, failed return 0

---

#### 2.1.7 `BOOL SWHid_SetDeviceOneParam(unsigned char bDevAdr, unsigned char pucDevParamAddr, unsigned char bValue)`

Set Device One Param  
**Param:**  
- `bDevAdr`: 0xFF  
- `pucDevParamAddr`: Param Addr  
- `bValue`: Param  
**Return:** Success return 1, failed return 0

---

#### 2.1.8 `BOOL SWHid_StopRead(unsigned char bDevAdr)`

Stop all RF reading  
**Param:**  
- `bDevAdr`: 0xFF  
**Return:** Success return 1, failed return 0

---

#### 2.1.9 `BOOL SWHid_StartRead(unsigned char bDevAdr)`

Start all RF reading  
**Param:**  
- `bDevAdr`: 0xFF  
**Return:** Success return 1, failed return 0

---

#### 2.1.10 `typedef void ( * FUNPTR_ACTIVE_CALLBACK)(int msg, int param1, unsigned char *param2, int param3, unsigned char *param4)`

Callback function prototype  
- `msg == 0`: Device Insert  
- `msg == 1`: Device Out  
- `msg == 2`:  
      - `param1` represents the unique identifier (tag number) of the RFID tag detected  
      - `param2` contains the raw data read from the tag (tagdata)  
      - `param3` specifies the length of the tag data in bytes (tagdata length)  
      - `param4` holds the serial number of the device (DevSN) that detected the tag

---

#### 2.1.11 `int SWHid_SetCallback(FUNPTR_ACTIVE_CALLBACK pfAddr)`

- `pfAddr`: Callback function

---

#### 2.1.12 `BOOL SWHid_InventoryG2(unsigned char bDevAdr, unsigned char *pBuffer, unsigned short *Totallen, unsigned short *CardNum)`

Inventory EPC  
**Param:**  
- `bDevAdr`: 0xFF  
- `pBuffer`: Get Buffer  
- `Totallen`: Get Buffer Length  
- `CardNum`: Tag Number  
**Return:** Success return 1, failed return 0

---

#### 2.1.13 `BOOL SWHid_WriteEPCG2(unsigned char bDevAdr, unsigned char *Password, unsigned char *WriteEPC, unsigned char WriteEPClen)`

Write EPC  
**Param:**  
- `bDevAdr`: 0xFF  
- `Password`: Password (4 bytes)  
- `WriteEPC`: Write Data  
- `Writelen`: Write Length  
**Return:** Success return 1, failed return 0

---

#### 2.1.14 `BOOL SWHid_ReadCardG2(unsigned char bDevAdr, unsigned char *Password, unsigned char Mem, unsigned char WordPtr, unsigned char ReadEPClen, unsigned char *Data)`

- `Mem`:  
      - 0: Reserved (Reserved memory area, typically not used)  
      - 1: EPC (Electronic Product Code, used for identifying items)  
      - 2: TID (Tag Identifier, unique identifier for the tag)  
      - 3: USER (User memory, customizable data storage area)  
**Param:**  
- `bDevAdr`: 0xFF  
- `Password`: Password (4 bytes)  
- `Mem`: 0:Reserved 1:EPC 2:TID 3:USER  
- `WordPtr`: Start Address  
- `ReadEPClen`: Read Length  
- `Data`: Read Data  
**Return:** Success return 1, failed return 0

---

#### 2.1.15 `BOOL SWHid_WriteCardG2(unsigned char bDevAdr, unsigned char *Password, unsigned char Mem, unsigned char WordPtr, unsigned char Writelen, unsigned char *Writedata)`

- `Mem`:  
      - 0: Reserved memory area  
      - 1: EPC memory area  
      - 2: TID memory area  
      - 3: USER memory area  
- `WordPtr`: Start Address  
- `WriteEPC`: Write Data  
- `WriteEPClen`: Write Length  
**Return:** Success return 1, failed return 0

---

#### 2.1.16 `BOOL SWHid_RelayOn(unsigned char bDevAdr)`

RelayOn  
**Param:**  
- `bDevAdr`: 0xFF  
**Return:** Success return 1, failed return 0

---

#### 2.1.17 `BOOL SWHid_RelayOff(unsigned char bDevAdr)`

RelayOff  
**Param:**  
- `bDevAdr`: 0xFF  
**Return:** Success return 1, failed return 0

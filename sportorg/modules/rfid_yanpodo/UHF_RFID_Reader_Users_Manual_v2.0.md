# UHF RFID Reader User’s Manual V2.0

## 1. COMMUNICATION INTERFACE SPECIFICATION

The reader communicates with host (MCU, MPU, Controller) using serial communication interface RS232/RS485 or USB or TCPIP and completes corresponding operations according to the host command. The default serial communication parameter is **115200bps**, 1 start bit, 8 data bits, 1 stop bit, without parity check bit. During communication, the least significant bit of one byte is transmitted first, and the least significant byte of command data sequence is transmitted first.

## 2. PROTOCOL DESCRIPTION

A communication procedure is initiated by the host sending commands and data to the reader, and the reader returns the result status and data to the host after command execution. The reader executes a command after receiving it. Only after command execution is completed, the reader will be able to receive another command. During the execution of one command, the reader ignores all other command data received.

**Host to Reader Communication Process:**

| HOST                | DIRECTION | READER             |
|---------------------|-----------|--------------------|
| Command Data Block  | →         |                    |

The reader completes command execution after receiving the host command and returns the results. During this period, it does not process any host data.

**Reader to Host Feedback:**

| READER              | DIRECTION | HOST               |
|---------------------|-----------|--------------------|
| Response Data Block | →         |                    |

## 3. DATA BLOCK FORMAT

### 3.1 COMMAND DATA BLOCK

| Field   | Length (Byte) | Comment                                                                                 |
|---------|---------------|----------------------------------------------------------------------------------------|
| Head    | 2             | `0x53, 0x57`                                                                           |
| Length  | 2             | Command data block length (not including itself). Value range: 3~1024. Len = Data[] + 3|
| Addr    | 1             | Reader address, 1 byte. Range: 0~254. 255 is broadcast address. Default: 0             |
| Cmd     | 1             | Operation command symbol, 1 byte                                                        |
| Data[]  | Variable      | Operation command parameters                                                            |
| Check   | 1             | Checksum: sum from package type domain to parameters domain, then one's complement + 1  |

### 3.2 RESPONSE DATA BLOCK

| Field   | Length (Byte) | Comment                                                                                 |
|---------|---------------|----------------------------------------------------------------------------------------|
| Head    | 2             | `0x43, 0x54`                                                                           |
| Length  | 2             | Command data block length (not including itself). Value range: 3~1024. Len = Data[] + 3|
| Addr    | 1             | Reader address, 1 byte. Range: 0~254                                                   |
| Cmd     | 1             | Received command symbol, 1 byte                                                         |
| Status  | 1             | State domain. `0x01` means success, `0x00` means failed                                 |
| Data[]  | Variable      | Response data                                                                           |
| Check   | 1             | Checksum: sum from package type domain to parameters domain, then one's complement + 1  |

The default value of the reader address is `0x00`. The host may change it by using the reader-defined command “Write Adr”.

**CheckSum computation includes all data from Len. Example in C:**

```c
unsigned char CheckSum(unsigned char *uBuff, unsigned short iBuffLen)
{
    unsigned char uSum=0;
    unsigned short i = 0;
    for(i=0;i< iBuffLen;i++)
    {
        uSum = uSum + uBuff[i];
    }
    uSum = (~uSum) + 1;
    return uSum;
}
```

## 4. OPERATION COMMAND (CMD) SUMMARY

| NUM | COMMAND                  | CODE  | COMMENT              |
|-----|--------------------------|-------|----------------------|
| 1   | CMD_READ_SYSTEM_PARAM    | 0x10  | Read system param    |

**Example:**

- Send: `53 57 00 03 FF 10 44`
- Recv: `43 54 00 0D 00 10 01 14 11 C3 DD 93 8E 17 01 23 2A`
    - `14`: SoftVersion 1.4
    - `11`: HarVersion 1.1
    - `C3 DD 93 8E 17 01 23`: DevSN

| 2   | CMD_READ_DEVICE_PARAM    | 0x20  | Read device param    |

**Example:**

- Send: `53 57 00 03 FF 20 34`
- Recv: `43 54 00 21 00 20 01 C3 55 01 00 00 00 0A....`
    - `C3`: DevType (C3 Means 5300)
    - `55`: Default param switch. None 55 default param.
    - `01 00.....`: Params, see CMD_SET_DEVICE_PARAM Command

| 3   | CMD_SET_DEVICE_PARAM     | 0x21  | Set device param     |

**Example:**

- Send: `53 57 00 25 FF 21 C3 55 01 ......`
    - `C3`: DevType. If DevType is not same, device returns false.
    - `55`: Default param switch. None 55 default param.
    - `01 .....`: Params

**Define: (For 5300 Device)**

```c
typedef struct
{
    unsigned char bTransport;     // 0:USB 1:RS232(Default) 2:RJ45 3:WIFI 4:Weigand
    unsigned char bWorkMode;      // 0:Answer 1:Active(Default) 2:Trigger 
    unsigned char bDeviceAddr;    // 0x00-0xFE
    unsigned char bFilterTime;    // 0-255  0:Close
    unsigned char bRFPower;       // 0 - 26db
    unsigned char bBeepEnable;    // 0 Close  1 Open
    unsigned char bUartBaudRate;  // 0:9600 1:19200 2:38400 3:57600 4:115200 
    unsigned char bFreqH;         // FreqH     
    unsigned char bFreqL;         // FreqL
    // FreqH (Bit7) FreqH (Bit6) FreqL (Bit7) FreqL (Bit6) FreqBand
    // 0 0 1 0 US band
    // 0 1 0 0 EU band
    // FreqH  Bit5-Bit0: Max Freq
    // FreqL  Bit5-Bit0: Min Freq
    // US band: Fs = 902.75 + N * 0.5 (MHz) N∈[0,49]
    // EU band: Fs = 865.1 + N*0.2(MHz) N∈[0,14]
    unsigned char bScanArea;      // 0:EPC 1:TID 2:User 3:EPC+TID
    unsigned char bStartPos;      // StartAddress 
    unsigned char bScanLength;    // ByteLength
    unsigned char bTriggerTime;   // TriggerEffectiveTime
    unsigned char bWgProtocal;    // WiegandMode 0:WG26 1:WG34
    unsigned char bWgOutPutMode;  // 0:MSB first 1:LSB first
    unsigned char bWgOutTime;     // Wg OutInterval
    unsigned char bWgPulseWidth;  // Wg PulseWidth
    unsigned char bWgPulseInterTime; // Wg PulseIntervalTime
    unsigned char bAntH;
    unsigned char bAntL;          // Ant Set, Bit0:0 Ant0Close 1 Ant0 Open (Bit15 – Bit0 Only for multi-Ant reader)
    unsigned char bQValue;        // Q: 0-6
    unsigned char bSession;       // 0: S0  1:S1: 2:S2 3:S3
} Struct_Device_Parameters;
```

- Recv: `43 54 00 04 00 21 01 43`
    - `01`: Success
    - `00`: Failed
### 4. CMD_DEFAULT_DEVICE_PARAM (0x22) — Default device param

**Example:**

- Send: `53 57 00 03 FF 22 32`
- Recv: `43 54 00 04 00 22 01 42`

---

### 5. CMD_READ_DEVICE_ONEPARAM (0x23) — Read one param

**Param address:**

- `01`: Transport  
    Value: 0-4  
    - 0: USB  
    - 1: RS232 (Default)  
    - 2: RJ45  
    - 3: WIFI  
    - 4: Weigand

- `02`: WorkMode  
    Value: 0-2  
    - 0: Answer  
    - 1: Active (Default)  
    - 2: Trigger

- `03`: DeviceAddr  
    Value: 00-FE

- `04`: FilterTime  
    Value: 00-FF (00 Close)

- `05`: RFPower  
    Value: 00-1A (5300), 00-11 (5100), 00-1E (5500)

- `06`: BeepEnable  
    Value: 0 Close, 1 Open

- `07`: UartBaudRate  
    Value:  
    - 0: 9600  
    - 1: 19200  
    - 2: 38400  
    - 3: 57600  
    - 4: 115200

**Example (Read RF Power):**

- Send: `53 57 00 04 FF 23 05 2B`  
    `05`: RF Power (Param address)
- Recv: `43 54 00 06 00 23 01 05 1E 1C`  
    `05 1E`: RF Power is `0x1E` (30 dBm)

---

### 6. CMD_SET_DEVICE_ONEPARAM (0x24) — Set one param

**Param address / Value (One Byte):**

- `01`: Transport  
    Value: 0-4  
    - 0: USB  
    - 1: RS232 (Default)  
    - 2: RJ45  
    - 3: WIFI  
    - 4: Weigand

- `02`: WorkMode  
    Value: 0-2  
    - 0: Answer  
    - 1: Active (Default)  
    - 2: Trigger

- `03`: DeviceAddr  
    Value: 00-FE

- `04`: FilterTime  
    Value: 00-FF (00 Close)

- `05`: RFPower  
    Value: 00-1A (5300), 00-11 (5100), 00-1E (5500)

- `06`: BeepEnable  
    Value: 0 Close, 1 Open

- `07`: UartBaudRate  
    Value:  
    - 0: 9600  
    - 1: 19200  
    - 2: 38400  
    - 3: 57600  
    - 4: 115200

**Example (Set RF Power):**

- Send: `53 57 00 05 FF 24 05 1A 0F`  
    `05 1A`: Set RF Power 1A (26 dBm)
- Recv: `43 54 00 04 00 24 01 40`  
    `01`: Success, `00`: Failed

**Example (Set WorkMode):**

- Send: `53 57 00 05 FF 24 02 00 2C`  
    `02 00`: Set Answer WorkMode
- Recv: `43 54 00 04 00 24 01 40`  
    `01`: Success, `00`: Failed

---

### 7. CMD_READ_DEVICENET_PARAM (0x26) — Read device net param

**Example:**

- Send: `53 57 00 03 FF 26 2E`
- Recv: `43 54 00 85 00 26 01 C3 55 00 68...`  
    - `C3`: DevType  
    - `55`: Default param switch. None 55 default param.  
    - `00 68...`: Net Params

---

### 8. CMD_SET_DEVICENET_PARAM (0x27) — Set device net param

**Example:**

- Send: `53 57 00 A6 FF 27 C3 55 00 68 ......`  
    - `C3`: DevType. If DevType is not same, device returns false.  
    - `55`: Default param switch. None 55 default param.  
    - `00 68...`: Net params
- Recv: `43 54 00 04 00 27 01 3D`  
    `01`: Success, `00`: Failed

---

### 9. CMD_DEFAULT_DEVICENET_PARAM (0x28) — Default device param

**Example:**

- Send: `53 57 00 03 FF 28 2C`
- Recv: `43 54 00 04 00 28 01 3C`

---

### 10. CMD_READ_DEVICE_TIME (0x2B) — Read device time

**Example:**

- Send: `53 57 00 03 FF 2B 29`
- Recv: `43 54 00 0A 00 2B 01 11 01 02 03 04 05 13`  
    - `11 01 02 03 04 05`: Time  
        - `11`: year (2017)  
        - `01`: month  
        - `02`: day  
        - `03`: hour  
        - `04`: minute  
        - `05`: second

---

### 11. CMD_SET_DEVICE_TIME (0x2C) — Set device time

**Example:**

- Send: `53 57 00 09 FF 2C 11 01 02 03 04 05 02`  
    - `11 01 02 03 04 05`: Time  
        - `11`: year (2017)  
        - `01`: month  
        - `02`: day  
        - `03`: hour  
        - `04`: minute  
        - `05`: second
- Recv: `43 54 00 04 00 2C 01 38`

---

### 12. CMD_READ_DEVICE_SPECIAL_PARAM (0x2E) — Read device special param

**Example:**

- Send: `53 57 00 03 FF 2E 26`
- Recv: `43 54 00 85 00 2E 01 C3 55 00 00...`  
    - `C3`: DevType  
    - `55`: Default param switch. None 55 default param.  
    - `00 00...`: Special params

---

### 13. CMD_SET_DEVICE_SPECIAL_PARAM (0x2F) — Set device special param

**Example:**

- Send: `53 57 00 12 FF 2F C3 55 00 00 ......`  
    - `C3`: DevType. If DevType is not same, device returns false.  
    - `55`: Default param switch. None 55 default param.  
    - `00 00...`: Special params
- Recv: `43 54 00 04 00 2F 01 35`  
    `01`: Success, `00`: Failed

---

### 14. CMD_READ_FREQ (0x3E) — Read device frequency

**Example:**

- Send: `53 57 00 03 FF 3E 16`
- Recv: `43 54 00 06 00 3E 01 29 9D 5E`  
    - `01`: Success, `00`: Failed  
    - `29 9D`: 2 bytes Freq Value

**Frequency Table:**

| N1   | N2   | Region         |
|------|------|---------------|
| 0x31 | 0x80 | US Freq       |
| 0x4E | 0x00 | Europe        |
| 0x2C | 0xA3 | China         |
| 0x29 | 0x9D | Korea         |
| 0x2E | 0x9F | Australia     |
| 0x4E | 0x00 | New Zealand   |
| 0x4E | 0x00 | India         |
| 0x2C | 0x81 | Singapore     |
| 0x2C | 0xA3 | Hongkong      |
| 0x31 | 0xA7 | Taiwan        |
| 0x31 | 0x80 | Canada        |
| 0x31 | 0x80 | Mexico        |
| 0x31 | 0x99 | Brazil        |
| 0x1C | 0x99 | Israel        |
| 0x24 | 0x9D | South Africa  |
| 0x2C | 0xA3 | Thailand      |
| 0x28 | 0xA1 | Malaysia      |
| 0x29 | 0x9D | Japan         |

---

### 15. CMD_SET_FREQ (0x3F) — Set device frequency

**Example:**

- Send: `53 57 00 05 FF 3F N1 N2 CC`

    Where N1, N2 are from the frequency table above.

    - `CC`: CheckSum

- Example (Set US Freq):  
    `53 57 00 05 FF 3F 31 80 62`
- Recv: `43 54 00 04 00 3F 01 25`  
    `01`: Success, `00`: Failed

### 16. CMD_STOP_READ `0x40`  
**Stop reading (For active mode)**  
**Example:**  
- Send: `53 57 00 03 FF 40 14`  
- Recv: `43 54 00 04 00 40 01 24`

---

### 17. CMD_START_READ `0x41`  
**Start reading (For active mode)**  
**Example:**  
- Send: `53 57 00 03 FF 41 13`  
- Recv: `43 54 00 04 00 41 01 23`

---

### 18. CMD_ACTIVE_DATA `0x45`  
**Active mode device send data**  
**Example:**  
- Recv:  
    ```
    43 54 00 2C 00 45 01 C4 DD 93 8E 17 01 23 02 0F 01 02 E2 00 20 75 60 10 01 82 04 80 E0 64 33 0F 01 03 E3 00 20 75 60 10 01 82 04 80 E0 64 34 07
    ```
    - `C4 DD 93 8E 17 01 23`: DevSN  
    - `02`: Tag Number, 02 means 2 tagIDs  
    - `0F 01 02 E2 00 20 75 60 10 01 82 04 80 E0 64 33`:  
        - `0F`: First tag length (includes type, ant, id, rssi)  
        - `01`: tag type (UHF type, Reserved)  
        - `02`: ant2  
        - `E2 00 20 75 60 10 01 82 04 80 E0 64`: tag id  
        - `33`: Rssi  
    - `0F 01 03 E3 00 20 75 60 10 01 82 04 80 E0 64 34`:  
        - `0F`: Second tag length (includes type, ant, id, rssi)  
        - `01`: tag type (UHF type, Reserved)  
        - `03`: ant3  
        - `E3 00 20 75 60 10 01 82 04 80 E0 64`: tag id  
        - `34`: Rssi  
- Send (to confirm receipt, not necessary):  
    `53 57 00 03 FF 45 0F`

---

### 19. CMD_CHECK_MODULE `0xE0`  
**Check UHFModule status**  
**Example:**  
- Send: `53 57 00 03 FF E0 74`  
- Recv:  
    - `43 54 00 05 01 E0 01 82`  (ModuleOK)  
    - `43 54 00 05 01 E0 00 83`  (ModuleError)

---

### 20. CMD_CHECK_ANT `0xE1`  
**Check antenna status (For multi-channel ant reader)**  
**Example:**  
- Send: `53 57 00 03 FF E1 73`  
- Recv:  
    ```
    43 54 00 06 00 E1 01 FF F2 90
    ```
    - `FF F2`: Ant status  
        - `1111 1111 1111 0010` (binary)  
        - Ant16 --------------- Ant1  
        - Ant4: None, Ant3: None, Ant2: Exist, Ant1: None

---

### 21. CMD_CLOSE_RELAY `0x85`  
**Close relay**  
**Example:**  
- Send: `53 57 00 03 FF 85 CF`  
- Recv: `43 54 00 04 00 85 01 DF`

---

### 22. CMD_RELEASE_RELAY `0x86`  
**Release relay**  
**Example:**  
- Send: `53 57 00 03 FF 86 CE`  
- Recv: `43 54 00 04 00 86 01 DE`

---

### 23. CMD_HEARTBEAT_PACK `0xFF`  
**Heartbeat packet (For tcp client of reader in WIFI and RJ45)**  
**Example:**  
- Recv:  
    ```
    43 54 00 0B 01 FF 01 23 01 02 03 04 05 06 25
    ```
    - `01`: Status  
    - `23 01 02 03 04 05 06`: DevSN  
- No response needed

---

### 24. CMD_INVENTORY_TAG `0x01`  
**Inventory tag (For command mode)**  
**Example:**  
- Send: `53 57 00 03 FF 01 53`  
- Recv:  
    - `43 54 00 04 00 01 00 64` (No Tag)  
    - `43 54 00 36 00 01 01 00 03 0F 01 02 E2 00 20 67 55 16 02 70 12 70 92 0F 49 0F 01 02 E2 00 20 75 60 10 01 86 25 10 16 A3 48 0F 01 02 E2 00 20 75 60 10 01 85 01 01 01 01 4D E4`
        - `00 03`: Tag Number (3 Tags)
        - `0F 01 02 E2 00 20 67 55 16 02 70 12 70 92 0F 49`: First tag  
            - `0F`: First tag length (includes type, ant, id, rssi)  
            - `01`: tag type (UHF type)  
            - `02`: ant2  
            - `E2 00 20 67 55 16 02 70 12 70 92 0F`: tag id  
            - `49`: Rssi  
        - `0F 01 02 E2 00 20 75 60 10 01 86 25 10 16 A3 48`: Second tag  
            - `0F`: First tag length (includes type, ant, id, rssi)  
            - `01`: tag type (UHF type)  
            - `02`: ant2  
            - `E2 00 20 75 60 10 01 86 25 10 16 A3`: tag id  
            - `48`: Rssi  
        - `0F 01 02 E2 00 20 75 60 10 01 85 01 01 01 01 4D`: Third tag  
            - `0F`: First tag length (includes type, ant, id, rssi)  
            - `01`: tag type (UHF type)  
            - `02`: ant2  
            - `E2 00 20 75 60 10 01 85 01 01 01 01`: tag id  
            - `4D`: Rssi

---

### 25. COM_READ_TAG_DATA `0x02`  
**Read part or all of a Tag’s Password, EPC, TID, or User memory**  
**Example:**  
- Send:  
    ```
    53 57 00 0A FF 02 01 02 06 00 00 00 00 42
    ```
    - `01`: Region (0 reserved, 1 EPC, 2 TID, 3 User)  
    - `02`: StartAdd (Word)  
    - `06`: Length (Word)  
    - `00 00 00 00`: Password, 4 bytes  
- Recv:  
    - `43 54 00 04 00 02 00 63` (Failed)  
    - `43 54 00 10 00 02 01 E2 00 20 67 55 16 02 70 12 70 92 0F ED` (Success)  
        - `01`: Success  
        - `E2 00 20 67 55 16 02 70 12 70 92 0F`: Tag Data

---

### 26. COM_WRITE_TAG_DATA `0x03`  
**Write several words in a Tag’s Reserved, EPC, TID, or User memory**  
**Example:**  
- Send:  
    ```
    53 57 00 16 FF 03 01 02 06 00 00 00 00 00 11 22 33 44 55 66 77 88 99 AA BB D3
    ```
    - `01`: Region (0 reserved, 1 EPC, 2 TID, 3 User)  
    - `02`: StartAdd (Word)  
    - `06`: Length (Word)  
    - `00 00 00 00`: Password, 4 bytes  
    - `00 11 22 33 44 55 66 77 88 99 AA BB`: Write data  
- Recv:  
    - `43 54 00 04 00 03 01 61` (Success)  
    - `43 54 00 04 00 03 00 ??` (Failed)

---

### Custom Protocol

If the communication protocol is customized, the protocol format is:  
`0x02 + ASC ID + 0x0D + 0x0A + 0x03`

**Example:**  
- Recv:  
    ```
    02 30 30 31 31 32 32 33 33 34 34 35 35 36 36 37 37 38 38 39 39 41 41 42 42 0D 0A 03
    ```
    - The Tag ID is `00112233445566778899AABB`
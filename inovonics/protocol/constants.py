# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
from enum import IntEnum





class MARKET_IDS(IntEnum):
    SECURITY = 0xB2
    ENVIRONMENTAL = 0xC0
    SUBMETERING = 0xA0
    REPEATERS = 0x01
    COORDINATORS = 0x00

class REPEATER_PRODUCT_TYPE(IntEnum):
    EN5040_D = 0x01 # DIRECTED
    EN5040_B = 0x00 # BROADCAST

class SECURITY_PRODUCT_TYPE(IntEnum):
    EN1210 = 0x00
    EN1210 = 0x00
    EN1210SK = 0x04
    EN1210W = 0x03
    EN1210EOL = 0x05
    EN1212 = 0x01
    EE1215 = 0x08
    EE1215W = 0x0B
    EN1215EOL = 0x0D
    EN1215WEOL = 0x0E
    EN1216 = 0x09
    EN1223D = 0x19
    EN1223S = 0x18
    EN1223SK = 0x1E
    EN1224 = 0x16
    EN1224ON = 0x17
    EN1233D = 0x15
    EN1233S = 0x14
    EN1235D = 0x11
    EN1235DF = 0x13
    EN1235S = 0x10
    EN1235SF = 0x12
    EN1236D = 0x39
    EN1238D = 0x3A
    EN1243 = 0x2C
    EN1244 = 0x21
    EN1245 = 0x2E
    EN1247 = 0x32
    EN1249 = 0x30
    EN1252 = 0x07
    EN1260 = 0x28
    EE1261 = 0x2B
    EN1261HT = 0x2B
    EN1262 = 0x29
    EN1265 = 0x2A
    EN1224 = 0x50
    EN1224ON = 0x51





class PACKET_ENUM(IntEnum):
    RESERVED = 0x00
    RADIO = 0x01
    RADIO_ERP1 = 0x01
    RESPONSE = 0x02
    RADIO_SUB_TEL = 0x03
    EVENT = 0x04
    COMMON_COMMAND = 0x05
    SMART_ACK_COMMAND = 0x06
    REMOTE_MAN_COMMAND = 0x07
    RADIO_MESSAGE = 0x09
    # RADIO_ADVANCED == RADIO_ERP2
    # Kept for backwards compatibility reasons
    RADIO_ADVANCED = 0x0A
    RADIO_ERP2 = 0x0A
    RADIO_802_15_4 = 0x10
    COMMAND_2_4 = 0x11


class RETURN_CODE(IntEnum):
    OK = 0x00
    ERROR = 0x01
    NOT_SUPPORTED = 0x02
    WRONG_PARAM = 0x03
    OPERATION_DENIED = 0x04


class EVENT_CODE(IntEnum):
    SA_RECLAIM_NOT_SUCCESFUL = 0x01
    SA_CONFIRM_LEARN = 0x02
    SA_LEARN_ACK = 0x03
    CO_READY = 0x04
    CO_EVENT_SECUREDEVICES = 0x05


class RORG(IntEnum):
    UNDEFINED = 0x00
    RPS = 0xF6
    BS1 = 0xD5
    BS4 = 0xA5
    VLD = 0xD2
    MSC = 0xD1
    ADT = 0xA6
    SM_LRN_REQ = 0xC6
    SM_LRN_ANS = 0xC7
    SM_REC = 0xA7
    SYS_EX = 0xC5
    SEC = 0x30
    SEC_ENCAPS = 0x31
    UTE = 0xD4


class PARSE_RESULT(IntEnum):
    OK = 0x00
    INCOMPLETE = 0x01
    CRC_MISMATCH = 0x03


class DB0(object):
    BIT_0 = -1
    BIT_1 = -2
    BIT_2 = -3
    BIT_3 = -4
    BIT_4 = -5
    BIT_5 = -6
    BIT_6 = -7
    BIT_7 = -8


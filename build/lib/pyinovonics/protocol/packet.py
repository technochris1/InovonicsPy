# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
from collections import OrderedDict

from pyinovonics.utils import *
from pyinovonics.protocol.constants import PACKET, RORG, PARSE_RESULT, DB0, START_BYTES, PACKET_HEADERS, MESSAGE_CLASS


LOGGER = logging.getLogger(__name__)


class Packet(object):
    '''
    Base class for Packet.
    Mainly used for for packet generation and
    Packet.parse_msg(buf) for parsing message.
    parse_msg() returns subclass, if one is defined for the data type.
    '''
    

    def __init__(self, packet_type, data=None, optional=None):
        self.packet_type = packet_type
        self.rorg = RORG.UNDEFINED
        self.rorg_func = None
        self.rorg_type = None
        self.rorg_manufacturer = None

        self.received = None

        if not isinstance(data, list) or data is None:
            self.LOGGER.warning('Replacing Packet.data with default value.')
            self.data = []
        else:
            self.data = data

        if not isinstance(optional, list) or optional is None:
            self.LOGGER.warning('Replacing Packet.optional with default value.')
            self.optional = []
        else:
            self.optional = optional

        self.status = 0
        self.parsed = OrderedDict({})
        self.repeater_count = 0
        self._profile = None

        self.parse()

    def __str__(self):
        return '0x%02X %s %s %s' % (
            self.packet_type,
            [hex(o) for o in self.data],
            [hex(o) for o in self.optional],
            self.parsed)

    def __unicode__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.packet_type == other.packet_type and self.rorg == other.rorg \
            and self.data == other.data and self.optional == other.optional


    def checksumB(self, bytes):
        return b'%02X' % (sum(bytes) & 0xFF)
    
    def checksum(self, bytes):
        return (sum(bytes) & 0xFF)

    @property
    def _bit_data(self):
        # First and last 5 bits are always defined, so the data we're modifying is between them...
        # TODO: This is valid for the packets we're currently manipulating.
        # Needs the redefinition of Packet.data -> Packet.message.
        # Packet.data would then only have the actual, documented data-bytes.
        # Packet.message would contain the whole message.
        # See discussion in issue #14
        return inovonics.utils.to_bitarray(self.data[1:len(self.data) - 5], (len(self.data) - 6) * 8)

    @_bit_data.setter
    def _bit_data(self, value):
        # The same as getting the data, first and last 5 bits are ommitted, as they are defined...
        for byte in range(len(self.data) - 6):
            self.data[byte+1] = inovonics.utils.from_bitarray(value[byte*8:(byte+1)*8])

    # # COMMENTED OUT, AS NOTHING TOUCHES _bit_optional FOR NOW.
    # # Thus, this is also untested.
    # @property
    # def _bit_optional(self):
    #     return inovonics.utils.to_bitarray(self.optional, 8 * len(self.optional))

    # @_bit_optional.setter
    # def _bit_optional(self, value):
    #     if self.rorg in [RORG.RPS, RORG.BS1]:
    #         self.data[1] = inovonics.utils.from_bitarray(value)
    #     if self.rorg == RORG.BS4:
    #         for byte in range(4):
    #             self.data[byte+1] = inovonics.utils.from_bitarray(value[byte*8:(byte+1)*8])

    @property
    def _bit_status(self):
        return inovonics.utils.to_bitarray(self.status)

    @_bit_status.setter
    def _bit_status(self, value):
        self.status = inovonics.utils.from_bitarray(value)

    @staticmethod
    def parse_msg(buf):
        '''
        Parses message from buffer.
        returns:
            - PARSE_RESULT
            - remaining buffer
            - Packet -object (if message was valid, else None)
        '''
        # If the buffer doesn't contain 0x55 (start char)
        # the message isn't needed -> ignore
        if buf[0] not in START_BYTES:
        #if 0x55 not in buf:
            return PARSE_RESULT.INCOMPLETE, [], None

        
        # # Convert to list, as index -method isn't defined for bytearray
        # buf = [ord(x) if not isinstance(x, int) else x for x in buf[list(buf).index(0x55):]]
        # try:
        #     data_len = (buf[1] << 8) | buf[2]
        #     opt_len = buf[3]
        # except IndexError:
        #     # If the fields don't exist, message is incomplete
        #     return PARSE_RESULT.INCOMPLETE, buf, None

        # Header: 6 bytes, data, optional data and data checksum
        msg_len = buf[1]
        if len(buf) < msg_len:
            # If buffer isn't long enough, the message is incomplete
            return PARSE_RESULT.INCOMPLETE, buf, None

        msg = buf[:msg_len + 1]
        if msg[-1:][0] != Packet.checksum(msg[: -1]):
            # Fail if doesn't match message
            Packet.LOGGER.error('Header CHECKSUM error!')
            # Return CRC_MISMATCH
            return PARSE_RESULT.CHECKSUM_MISMATCH, buf, None





        buf = buf[msg_len +1:]

        #packet_type = msg[4]
        #data = msg[6:6 + data_len]
        #opt_data = msg[6 + data_len:6 + data_len + opt_len]

        # If we got this far, everything went ok (?)
        # if packet_type == PACKET.RADIO_ERP1:
        #     # Need to handle UTE Teach-in here, as it's a separate packet type...
        #     if data[0] == RORG.UTE:
        #         packet = UTETeachInPacket(packet_type, data, opt_data)
        #     else:
        #         packet = RadioPacket(packet_type, data, opt_data)
        # elif packet_type == PACKET.RESPONSE:
        #     packet = ResponsePacket(packet_type, data, opt_data)
        # elif packet_type == PACKET.EVENT:
        #     packet = EventPacket(packet_type, data, opt_data)
        # else:
        #     packet = Packet(packet_type, data, opt_data)



        match msg[0]:
            case PACKET_HEADERS.DATA_ACK: 
                LOGGER.info(" ACK")
                #0[0x06] - Header for data acknowledgement from application controller.
                #1[0x02] - Message length, excluding checksum.
                #2[0x08] - Checksum.    

            case PACKET_HEADERS.DATA_NACK: 
                #0[0x15] - Header for data non-acknowledgement from application controller.
                #1[0x03] - Message length, excluding checksum.
                #2[ERROR] - One byte error code
                #  [0x01] - Checksum incorrect
                #  [0x02] - Unrecognized header
                #  [0x03] - Serial buffer full
                #  [0x04] - Timeout(incomplete message)
                #  [0x05] - Write error
                #  [0x06] - Read error
                #  [0x07] - Invalid data
                #  [0x08] - Unrecognized command
                #  [0x09] - Outbound directed message fail
                #  [0x0A - 0xFF] - Reserved
                #3[CKSUM] - Checksum.                                
                LOGGER.info(f" NAK Error = {msg[2]} ")

            case PACKET_HEADERS.CONTROLLER_MESSAGE: #0x1C
                #0[0x1C] - Header for the check-in or status message.
                #1[0x05] - Message length, excluding checksum.
                #2[DATA] - The counter of unacknowledged messages sent to your application controller since the last check -in or status message.
                #3[STAT1] - Status byte 1 is reserved.
                #4[STAT0] - Status byte 0.
                #     Bit 7 - Receiver is jammed.All channels contain interfering signals above a predetermined level.
                #     Bit 6 - Reserved.
                #     Bit 5 - RF gateway case tamper.
                #     Bit 4 - Set when there has been no change in status since the last transmission.
                #     Bit 3 - Reset of the RF gateway microcontroller.
                #     Bit 2 - Reserved.
                #     Bit 1 - Reserved.
                #     Bit 0 - Link failure.
                #5[CKSUM] - Checksum.
                
                #stat0 = queue.peekAll()[4].toString(2).padStart(8, "0")
                #LOGGER.info("STAT0:", stat0);
                #LOGGER.info("STAT0:Jammed", stat0[0]);
                #LOGGER.info("STAT0:CaseTamper", stat0[2]);
                #LOGGER.info("STAT0:Idle", stat0[3]);
                #LOGGER.info("STAT0:Reset", stat0[4]);                                
                #s1 = BitArray(u=packet[4], length=8)
                #s1.reverse() # reverse bits to match documentation
                #LOGGER.info(f" Network Coordinator Message: [{packet[0]}][{packet[1]}][{packet[2]}][{packet[3]}][{packet[4]} (0.{s1[0]} 3.{s1[3]} 4.{s1[4]} 5.{s1[5]} 7.{s1[7]})][{packet[5]}] ")
                LOGGER.info(" Network Coordinator Message")

            case PACKET_HEADERS.PAYLOAD_MESSAGE: #0x72 
                #LOGGER.info(f" Device Payload Message Begin: [{packet[0]}][{packet[1]}]{packet[2:6]}{packet[6:10]}[{packet[10]}]")
                        
                #let uID = Convert.ToInt64(HEXuID, 16).ToString().PadLeft(8, "0");

                #traceCount = packet[10]
                #Debug.WriteLine("TRACE.COUNT: " + traceCount);
                LOGGER.info(f"TRACE.COUNT: {msg[10]}")
                _traceCountOffset = msg[10] * 4
                
                LOGGER.info(f"HOP.COUNT: {msg[11 + _traceCountOffset]}")
                LOGGER.info(f"MSG.CLASS: {msg[12 + _traceCountOffset]}")    

                match (msg[12 + _traceCountOffset]):
                    case MESSAGE_CLASS.REPEATER_RESET:                                             
                        LOGGER.info("Repeater Reset Message From Device")
                        pass

                    case MESSAGE_CLASS.AGGREGATED_ENDPOINT_MESSAGE: 
                        #region Security Device - Aggregated Message        
                        LOGGER.info("Aggregated Security Endpoint Message From Device")                                    
                        pass

                    case MESSAGE_CLASS.TEMPERATURE_SENSOR_MESSAGE: 
                        #region Temperature Device
                        LOGGER.info("Temperature SensorMessage From Device")
                        pass
                
                    case MESSAGE_CLASS.ENDPOINT_MESSAGE:
                        #region Security Device              
                        LOGGER.info("Security Endpoint Message")
                        #LOGGER.info(f"Security Endpoint Message From Device={msg[2:6]} productType={msg[13 + (msg[10] * 4)]} level={msg[16 + (msg[10] * 4)]} margin={msg[17 + (msg[10] * 4)]}")                              
                        pass
                
                    
                    case MESSAGE_CLASS.NETWORK_DEVICE_STATUS: 
                        LOGGER.info(f"Network Device Status Message")
                        #region Network Device Status Message
                        #LOGGER.info(f"Network Device Status Message From Device={packet[2:6]} mode={packet[13 + (packet[10] * 4)]} level={packet[16 + (packet[10] * 4)]} margin={packet[17 + (packet[10] * 4)]}")
                        #s1 = BitArray(u=packet[15 + (packet[10] * 4)], length=8)
                        #s1.reverse() # reverse bits to match documentation
                        #LOGGER.info(f"STAT0 = 1.{s1[1]} 3.{s1[3]} 4.{s1[4]} 5.{s1[5]} 6.{s1[6]} 7.{s1[7]}) ")
                        pass

                    case _: # DEFAULT
                        pass
                        
            case _:  #DEFAULT
                pass








        return PARSE_RESULT.OK, buf, packet

































    @staticmethod
    def create(packet_type, rorg, rorg_func, rorg_type, direction=None, command=None,
               destination=None,
               sender=None,
               learn=False, **kwargs):
        '''
        Creates an packet ready for sending.
        Uses rorg, rorg_func and rorg_type to determine the values set based on EEP.
        Additional arguments (**kwargs) are used for setting the values.

        Currently only supports:
            - PACKET.RADIO_ERP1
            - RORGs RPS, BS1, BS4, VLD.

        TODO:
            - Require sender to be set? Would force the "correct" sender to be set.
            - Do we need to set telegram control bits?
              Might be useful for acting as a repeater?
        '''

        if packet_type != PACKET.RADIO_ERP1:
            # At least for now, only support PACKET.RADIO_ERP1.
            raise ValueError('Packet type not supported by this function.')

        if rorg not in [RORG.RPS, RORG.BS1, RORG.BS4, RORG.VLD]:
            # At least for now, only support these RORGS.
            raise ValueError('RORG not supported by this function.')

        if destination is None:
            Packet.LOGGER.warning('Replacing destination with broadcast address.')
            destination = [0xFF, 0xFF, 0xFF, 0xFF]

        # TODO: Should use the correct Base ID as default.
        #       Might want to change the sender to be an offset from the actual address?
        if sender is None:
            Packet.LOGGER.warning('Replacing sender with default address.')
            sender = [0xDE, 0xAD, 0xBE, 0xEF]

        if not isinstance(destination, list) or len(destination) != 4:
            raise ValueError('Destination must a list containing 4 (numeric) values.')

        if not isinstance(sender, list) or len(sender) != 4:
            raise ValueError('Sender must a list containing 4 (numeric) values.')

        packet = Packet(packet_type, data=[], optional=[])
        packet.rorg = rorg
        packet.data = [packet.rorg]
        # Select EEP at this point, so we know how many bits we're dealing with (for VLD).
        packet.select_eep(rorg_func, rorg_type, direction, command)

        # Initialize data depending on the profile.
        if rorg in [RORG.RPS, RORG.BS1]:
            packet.data.extend([0])
        elif rorg == RORG.BS4:
            packet.data.extend([0, 0, 0, 0])
        else:
            packet.data.extend([0] * int(packet._profile.get('bits', '1')))
        packet.data.extend(sender)
        packet.data.extend([0])
        # Always use sub-telegram 3, maximum dbm (as per spec, when sending),
        # and no security (security not supported as per inovonics Serial Protocol).
        packet.optional = [3] + destination + [0xFF] + [0]

        if command:
            # Set CMD to command, if applicable.. Helps with VLD.
            kwargs['CMD'] = command

        packet.set_eep(kwargs)
        if rorg in [RORG.BS1, RORG.BS4] and not learn:
            if rorg == RORG.BS1:
                packet.data[1] |= (1 << 3)
            if rorg == RORG.BS4:
                packet.data[4] |= (1 << 3)
        packet.data[-1] = packet.status

        # Parse the built packet, so it corresponds to the received packages
        # For example, stuff like RadioPacket.learn should be set.
        packet = Packet.parse_msg(packet.build())[2]
        packet.rorg = rorg
        packet.parse_eep(rorg_func, rorg_type, direction, command)
        return packet

    def parse(self):
        ''' Parse data from Packet '''
        # Parse status from messages
        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            self.status = self.data[-1]
        if self.rorg == RORG.VLD:
            self.status = self.optional[-1]

        if self.rorg in [RORG.RPS, RORG.BS1, RORG.BS4]:
            # These message types should have repeater count in the last for bits of status.
            self.repeater_count = inovonics.utils.from_bitarray(self._bit_status[4:])
        return self.parsed

    def select_eep(self, rorg_func, rorg_type, direction=None, command=None):
        ''' Set EEP based on FUNC and TYPE '''
        # set EEP profile
        self.rorg_func = rorg_func
        self.rorg_type = rorg_type
        self._profile = self.eep.find_profile(self._bit_data, self.rorg, rorg_func, rorg_type, direction, command)
        return self._profile is not None

    def parse_eep(self, rorg_func=None, rorg_type=None, direction=None, command=None):
        ''' Parse EEP based on FUNC and TYPE '''
        # set EEP profile, if demanded
        if rorg_func is not None and rorg_type is not None:
            self.select_eep(rorg_func, rorg_type, direction, command)
        # parse data
        provides, values = self.eep.get_values(self._profile, self._bit_data, self._bit_status)
        self.parsed.update(values)
        return list(provides)

    def set_eep(self, data):
        ''' Update packet data based on EEP. Input data is a dictionary with keys corresponding to the EEP. '''
        self._bit_data, self._bit_status = self.eep.set_values(self._profile, self._bit_data, self._bit_status, data)

    def build(self):
        ''' Build Packet for sending to inovonics controller '''
        data_length = len(self.data)
        ords = [0x55, (data_length >> 8) & 0xFF, data_length & 0xFF, len(self.optional), int(self.packet_type)]
        ords.append(crc8.calc(ords[1:5]))
        ords.extend(self.data)
        ords.extend(self.optional)
        ords.append(crc8.calc(ords[6:]))
        return ords


class RadioPacket(Packet):
    destination = [0xFF, 0xFF, 0xFF, 0xFF]
    dBm = 0
    sender = [0xFF, 0xFF, 0xFF, 0xFF]
    learn = True
    contains_eep = False

    def __str__(self):
        packet_str = super(RadioPacket, self).__str__()
        return '%s->%s (%d dBm): %s' % (self.sender_hex, self.destination_hex, self.dBm, packet_str)

    @staticmethod
    def create(rorg, rorg_func, rorg_type, direction=None, command=None,
               destination=None, sender=None, learn=False, **kwargs):
        return Packet.create(PACKET.RADIO_ERP1, rorg, rorg_func, rorg_type,
                             direction, command, destination, sender, learn, **kwargs)

    @property
    def sender_int(self):
        return inovonics.utils.combine_hex(self.sender)

    @property
    def sender_hex(self):
        return inovonics.utils.to_hex_string(self.sender)

    @property
    def destination_int(self):
        return inovonics.utils.combine_hex(self.destination)

    @property
    def destination_hex(self):
        return inovonics.utils.to_hex_string(self.destination)

    def parse(self):
        self.destination = self.optional[1:5]
        self.dBm = -self.optional[5]
        self.sender = self.data[-5:-1]
        # Default to learn == True, as some devices don't have a learn button
        self.learn = True

        self.rorg = self.data[0]

        # parse learn bit and FUNC/TYPE, if applicable
        if self.rorg == RORG.BS1:
            self.learn = not self._bit_data[DB0.BIT_3]
        if self.rorg == RORG.BS4:
            self.learn = not self._bit_data[DB0.BIT_3]
            if self.learn:
                self.contains_eep = self._bit_data[DB0.BIT_7]
                if self.contains_eep:
                    # Get rorg_func and rorg_type from an unidirectional learn packet
                    self.rorg_func = inovonics.utils.from_bitarray(self._bit_data[DB3.BIT_7:DB3.BIT_1])
                    self.rorg_type = inovonics.utils.from_bitarray(self._bit_data[DB3.BIT_1:DB2.BIT_2])
                    self.rorg_manufacturer = inovonics.utils.from_bitarray(self._bit_data[DB2.BIT_2:DB0.BIT_7])
                    self.LOGGER.debug('learn received, EEP detected, RORG: 0x%02X, FUNC: 0x%02X, TYPE: 0x%02X, Manufacturer: 0x%02X' % (self.rorg, self.rorg_func, self.rorg_type, self.rorg_manufacturer))  # noqa: E501

        return super(RadioPacket, self).parse()


class UTETeachInPacket(RadioPacket):
    # Request types
    TEACH_IN = 0b00
    DELETE = 0b01
    NOT_SPECIFIC = 0b10

    # Response types
    NOT_ACCEPTED = [False, False]
    TEACHIN_ACCEPTED = [False, True]
    DELETE_ACCEPTED = [True, False]
    EEP_NOT_SUPPORTED = [True, True]

    unidirectional = False
    response_expected = False
    number_of_channels = 0xFF
    rorg_of_eep = RORG.UNDEFINED
    request_type = NOT_SPECIFIC
    channel = None

    contains_eep = True

    @property
    def bidirectional(self):
        return not self.unidirectional

    @property
    def teach_in(self):
        return self.request_type != self.DELETE

    @property
    def delete(self):
        return self.request_type == self.DELETE

    def parse(self):
        super(UTETeachInPacket, self).parse()
        self.unidirectional = not self._bit_data[DB6.BIT_7]
        self.response_expected = not self._bit_data[DB6.BIT_6]
        self.request_type = inovonics.utils.from_bitarray(self._bit_data[DB6.BIT_5:DB6.BIT_3])
        self.rorg_manufacturer = inovonics.utils.from_bitarray(self._bit_data[DB3.BIT_2:DB2.BIT_7] + self._bit_data[DB4.BIT_7:DB3.BIT_7])  # noqa: E501
        self.channel = self.data[2]
        self.rorg_type = self.data[5]
        self.rorg_func = self.data[6]
        self.rorg_of_eep = self.data[7]
        if self.teach_in:
            self.learn = True
        return self.parsed

    def create_response_packet(self, sender_id, response=TEACHIN_ACCEPTED):
        # Create data:
        # - Respond with same RORG (UTE Teach-in)
        # - Always use bidirectional communication, set response code, set command identifier.
        # - Databytes 5 to 0 are copied from the original message
        # - Set sender id and status
        data = [self.rorg] + \
               [inovonics.utils.from_bitarray([True, False] + response + [False, False, False, True])] + \
               self.data[2:8] + \
               sender_id + [0]

        # Always use 0x03 to indicate sending, attach sender ID, dBm, and security level
        optional = [0x03] + self.sender + [0xFF, 0x00]

        return RadioPacket(PACKET.RADIO_ERP1, data=data, optional=optional)


class ResponsePacket(Packet):
    response = 0
    response_data = []

    def parse(self):
        self.response = self.data[0]
        self.response_data = self.data[1:]
        return super(ResponsePacket, self).parse()


class EventPacket(Packet):
    event = 0
    event_data = []

    def parse(self):
        self.event = self.data[0]
        self.event_data = self.data[1:]
        return super(EventPacket, self).parse()

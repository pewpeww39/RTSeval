import pyvisa
import logging
from typing import (
    IO,
    Optional,
    Any,
    Dict,
    Union,
    List,
    Tuple,
    Set,
    Sequence,
    Iterable,
    Iterator,
)
import copy
import math
import sys
import warnings

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

_ch = logging.StreamHandler()
_ch.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(_ch)

# These are constant values used for checking and establishing 
# power supply limits.
# These values are obtained from the factory manufactor. See 
# http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=186&zoom=100,177,108
_FACTORY_MIN_P6V_VOLTAGE = 0.0
_FACTORY_MAX_P6V_VOLTAGE = 6.0
_FACTORY_MIN_P25V_VOLTAGE = 0.0
_FACTORY_MAX_P25V_VOLTAGE = 25.0
_FACTORY_MIN_N25V_VOLTAGE = -25.0
_FACTORY_MAX_N25V_VOLTAGE = 0.0

_FACTORY_MIN_P6V_CURRENT = 0.0
_FACTORY_MAX_P6V_CURRENT = 5.0
_FACTORY_MIN_P25V_CURRENT = 0.0
_FACTORY_MAX_P25V_CURRENT = 1.0
_FACTORY_MIN_N25V_CURRENT = 0.0
_FACTORY_MAX_N25V_CURRENT = 1.0
# These values are user created limitations to the output of the
# power supply. Default to the factory limitations.
USER_MIN_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P6V_VOLTAGE)
USER_MAX_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P6V_VOLTAGE)
USER_MIN_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P25V_VOLTAGE)
USER_MAX_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P25V_VOLTAGE)
USER_MIN_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_N25V_VOLTAGE)
USER_MAX_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_N25V_VOLTAGE)

USER_MIN_P6V_CURRENT = copy.deepcopy(_FACTORY_MIN_P6V_CURRENT)
USER_MAX_P6V_CURRENT = copy.deepcopy(_FACTORY_MAX_P6V_CURRENT)
USER_MIN_P25V_CURRENT = copy.deepcopy(_FACTORY_MIN_P25V_CURRENT)
USER_MAX_P25V_CURRENT = copy.deepcopy(_FACTORY_MAX_P25V_CURRENT)
USER_MIN_N25V_CURRENT = copy.deepcopy(_FACTORY_MIN_N25V_CURRENT)
USER_MAX_N25V_CURRENT = copy.deepcopy(_FACTORY_MAX_N25V_CURRENT)

# Default timeout value.
DEFAULT_TIMEOUT = 15
# The number of resolved digits kept by internal rounding
# by the power supply.
_SUPPLY_RESOLVED_DIGITS = 4

class KeysightPS: 

    # Internal implimentation values.
    _P6V_voltage = float()
    _P25V_voltage = float()
    _N25V_voltage = float()
    _P6V_current = float()
    _P25V_current = float()
    _N25V_current = float()

    # Serial connection information.
    _serial_port = str()
    _serial_baudrate = int()
    _serial_parity = str()
    _serial_data = int()
    _serial_start = int()
    _serial_end = int()
    _serial_timeout = int()

    # These values are user created limitations to the output of the
    # power supply for each individual power supply instance. 
    # Default to the factory limitations.
    MIN_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P6V_VOLTAGE)
    MAX_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P6V_VOLTAGE)
    MIN_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P25V_VOLTAGE)
    MAX_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P25V_VOLTAGE)
    MIN_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_N25V_VOLTAGE)
    MAX_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_N25V_VOLTAGE)

    MIN_P6V_CURRENT = copy.deepcopy(_FACTORY_MIN_P6V_CURRENT)
    MAX_P6V_CURRENT = copy.deepcopy(_FACTORY_MAX_P6V_CURRENT)
    MIN_P25V_CURRENT = copy.deepcopy(_FACTORY_MIN_P25V_CURRENT)
    MAX_P25V_CURRENT = copy.deepcopy(_FACTORY_MAX_P25V_CURRENT)
    MIN_N25V_CURRENT = copy.deepcopy(_FACTORY_MIN_N25V_CURRENT)
    MAX_N25V_CURRENT = copy.deepcopy(_FACTORY_MAX_N25V_CURRENT)

    def __init__(self, 
                 visa_address: str,
                 visa_library: str = "@py",
                 timeout=DEFAULT_TIMEOUT):
        # Ensure that the timeout value is at least one second.
        if (timeout < 1.0):
            # We will force it to be the default.
            warnings.warn("The timeout must be at least 1 second. Choosing "
                          "default of 15 seconds.",
                          RuntimeWarning, stacklevel=2)
            timeout = DEFAULT_TIMEOUT

        self.visa_address = visa_address
        self.visa_library = visa_library

        self.rm = pyvisa.ResourceManager(visa_library)
        # if ((len(self.visa_address.query('*IDN?')) == 0)):
        #     # There was no responce to the system version command.
        #     # There does not seem to be a Keysight E3631A 
        #     # attached to this interface.
        #     warnings.warn("There is no responce from the port `{port}`. "
        #                   "The instrument may not be communicating back "
        #                   "with this class. Some functions may fail."
        #                   .format(port=self._serial_port),
        #                   RuntimeWarning, stacklevel=2)
        # else:
        #     # Set the system into remote mode.
        #     __ = self.remote_mode()
        # self.rm = rm.open_resource(self.visa_address)

    # def connect(self, **kwargs) -> bool:
    #     """
    #     Connects to Keithley.
    #     :param kwargs: Keyword arguments for Visa connection.
    #     :returns: Whether the connection succeeded.
    #     """
    #     kwargs = kwargs or self._connection_kwargs  # use specified or remembered kwargs
    #     # try:
    #     self.connection = self.rm.open_resource(self.visa_address, **kwargs)
    #     self.connection.read_termination = "\n"
    #     self.connected = True
    def connect(self) -> bool:
        """
        Connects to Keithley.
        :param kwargs: Keyword arguments for Visa connection.
        :returns: Whether the connection succeeded.
        """
        # kwargs = kwargs or self._connection_kwargs  # use specified or remembered kwargs
        try:
            self.connection = self.rm.open_resource(self.visa_address)
            self.connection.read_termination = "\n"
            self.connected = True
            self._dict.clear()  # reset Keithley dict
            # logger.debug
            print("Connected to Keithley at %s.", self.visa_address)
        except ValueError:
            self.connection = None
            self.connected = False
            raise
        except ConnectionError:
            logger.info(
                "Connection error. Please check that no other program is connected."
            )
            self.connection = None
            self.connected = False
        except AttributeError:
            logger.info("Invalid VISA address %s.", self.visa_address)
            self.connection = None
            self.connected = False
        except Exception:
            logger.info("Could not connect to Keithley at %s.", self.visa_address)
            self.connection = None
            self.connected = False

        return self.connected
    

from keithley2600 import Keithley2600
import sys
import logging
import re
import threading
import numpy as np
import time
from contextlib import contextmanager
from threading import RLock
from xdrlib import Error as XDRError
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

# external imports
import pyvisa

# local import
from keithley2600.result_table import FETResultTable


LuaReturnTypes = Union[float, str, bool, None, "_LuaFunction", "_LuaTable"]
LuaBridgeType = Union["KeithleyFunction", "KeithleyClass", "KeithleyProperty"]


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

_ch = logging.StreamHandler()
_ch.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(_ch)


def log_to_screen(level: int = logging.DEBUG) -> None:
    log_to_stream(sys.stderr, level)


def log_to_stream(stream_output: Optional[IO], level: int = logging.DEBUG) -> None:
    logger.setLevel(level)
    _ch.setStream(stream_output)
    _ch.setLevel(level)


def removeprefix(self: str, prefix: str) -> str:
    """
    Removes the given prefix from a string. Only the first instance of the prefix is
    removed. The original string is returned if it does not start with the given prefix.
    This follows the Python 3.9 implementation of ``str.removeprefix``.
    :param self: Original string.
    :param prefix: Prefix to remove.
    :returns: String without prefix.
    """
    if self.startswith(prefix):
        return self[len(prefix) :]
    else:
        return self[:]


class KeithleyIOError(Exception):
    """Raised when no Keithley instrument is connected."""


class KeithleyError(Exception):
    """Raised for error messages from the Keithley itself."""


class _Nil:
    def __repr__(self) -> str:
        return "nil"


class _LuaTable:
    def __init__(self, str_repr: str) -> None:
        self._repr = str_repr

    def __repr__(self) -> str:
        return self._repr


class _LuaFunction:
    def __init__(self, str_repr) -> None:
        self._repr = str_repr

    def __repr__(self) -> str:
        return self._repr


class KeithleyProperty:
    """Mimics a Keithley TSP Lua property (bool, number or string).
    Getters and setters forward their calls to :func:`_query` and :func:`_write` methods
    of the parent command. Booleans, numbers and strings are accepted natively, anything
    else will be converted to a string.
    """

    def __init__(
        self, name: str, parent: "KeithleyClass", readonly: bool = False
    ) -> None:
        self._name = name
        self._name_display = removeprefix(name, "_G.")
        self._parent = parent
        self._readonly = readonly

    def get(self) -> Any:
        return self._parent._query(self._name)

    def set(self, value: Any) -> None:
        if self._readonly:
            raise AttributeError(f"'{self._name_display}' is read-only")
        value = self._parent._convert_input(value)
        self._parent._write(f"{self._name} = {value}")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}({self._name_display}, "
            f"readonly={self._readonly})>"
        )


class KeithleyFunction:
    """Mimics a Keithley TSP (Lua) function
    Class which mimics a function and can be dynamically created. It forwards all calls
    to the :func:`_query` method of the parent command and returns the result from
    :func:`_query`. Calls accept arbitrary arguments, as long as :func:`_query` can
    handle them.
    This class is designed to look like a Keithley TSP function, forward function calls
    to the Keithley, and return the results.
    """

    def __init__(self, name: str, parent: "KeithleyClass") -> None:
        self._name = name
        self._name_display = removeprefix(name, "_G.")
        self._parent = parent

    def __call__(self, *args) -> Any:

        # convert all arguments
        args = [self._parent._convert_input(a) for a in args]
        args_string = ", ".join(args)

        # pass on a string representation of the function call to self._parent._query
        return self._parent._query(f"{self._name}({args_string})")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self._name_display})>"

class KeithleyClass:
    """Mimics a Keithley TSP (Lua) table
    Class which represents a Keithley TSP / Lua table. Tables act as the equivalent of
    objects in the Lua scripting language and table indices can be both numbers or
    strings. Their values are accessible by index notation or as "attributes" in case of
    string indices. For example, ``table["name"]`` and ``table.name`` access the same
    field. If tables have numeric indices only, they practically serve as a list.
    """

    _protected_attrs = [
        "_name",
        "_name_display",
        "_parent",
        "_dict",
        "_lua_type",
    ]

    def __init__(self, name: str, parent: Optional["KeithleyClass"] = None) -> None:
        self._name = name
        self._name_display = removeprefix(name, "_G.")
        self._parent = parent
        self._dict: Dict[Union[str, int], LuaBridgeType] = {}
        self._lua_type: Optional[str] = None

    def create_lua_attr(self, name: Union[str, int], value: Any) -> LuaBridgeType:
        """
        Creates an attribute / index of this table with the given type. The initial
        value will be 0 for a KeithleyProperty and an empty table for a KeithleyClass.
        :param name: Variable name.
        :param value: Initial value, will be used to infer the type.
        :returns: The accessor for the created variable.
        """

        full_name = self._to_global_name(name)

        if isinstance(name, str) and "." in name:
            raise ValueError("Variable name may not contain periods")

        if self._query(full_name) is not None:
            raise ValueError("Variable already exists in namespace")

        # create variable on Keithley
        value_string = self._convert_input(value)
        self._write(f"{full_name} = {value_string}")

        # add to our own dict
        try:
            self._load_lua_attribute(name)
        except RuntimeError:
            raise RuntimeError("Variable creation failed")

        return self._dict[name]

    def delete_lua_attr(self, name: Union[str, int]) -> None:
        """
        Deletes an attribute / index of this table.
        .. warning:: If you delete a Keithley command group, for example ``smua``, it
            will no longer be available until you power-cycle the Keithley.
        :param name: Attribute name.
        """

        full_name = self._to_global_name(name)

        if isinstance(name, str) and "." in name:
            raise ValueError("Variable name may not contain periods")

        self._write(f"{full_name} = nil")

        # confirm deletion
        if self._query(full_name) is not None:
            raise RuntimeError("Variable deletion failed")

        del self._dict[name]

    def __getattr__(self, attr_name: str) -> Any:

        if not self._dict:
            # will raise KeithleyIOError if not connected
            self._load_lua_namespace()

        try:
            accessor = self._dict[attr_name]

            if isinstance(accessor, KeithleyProperty):
                return accessor.get()
            else:
                return accessor

        except KeyError:
            raise AttributeError(f"{self} has no attribute '{attr_name}'")

    def __setattr__(self, key: str, value: Any) -> None:

        if key in self._protected_attrs:
            super().__setattr__(key, value)
        else:

            if not self._dict:
                # will raise KeithleyIOError if not connected
                self._load_lua_namespace()

            if key in self._dict:
                accessor = self._dict[key]

                if isinstance(accessor, KeithleyProperty):
                    accessor.set(value)
                else:
                    value = self._convert_input(value)
                    self._write(f"{self._name}.{key} = {value}")
            else:
                super().__setattr__(key, value)

    def _to_global_name(self, index: Union[str, int]) -> str:
        if isinstance(index, int):
            global_name = f"{self._name}[{index}]"
        elif isinstance(index, str):
            global_name = f"{self._name}.{index}"
        else:
            raise ValueError(f"Invalid index {index}")

        return global_name

    def _load_lua_namespace(self) -> None:
        """
        Get all indices of the "namespace" defined by this table, including those
        defined through the metatable. This is the main method to get all support
        Keithley TSP commands.
        .. note:: The Lua table ``_G`` holds all global namespace variables, including a
            reference to itself.
        """

        self._dict.clear()

        var_name = _Nil()

        # get any immediate indices

        while True:

            # iterate over
            res = self._query(f"next({self._name}, {var_name!r})")

            if res:
                var_name, var_value = res
                full_name = self._to_global_name(var_name)

                if isinstance(var_value, _LuaFunction):
                    self._dict[var_name] = KeithleyFunction(full_name, self)
                elif isinstance(var_value, _LuaTable):
                    self._dict[var_name] = KeithleyClass(full_name, self)
                else:
                    self._dict[var_name] = KeithleyProperty(full_name, self)
            else:
                break

        # check for indices set by metatable
        # all commands defined by Keithley and not native to the Lua scripting language
        # will manage index access through Getters, Setter and Objects defined on the
        # metatable

        # get the metatable, if any
        self._write(f"mt = getmetatable({self._name})")

        if self._query("mt"):

            # get Getters, if any
            # those will define "immutable objects" (numbers, strings, booleans)
            if self._query("mt.Getters"):

                var_name = _Nil()

                while True:

                    res = self._query(f"next(mt.Getters, {var_name!r})")

                    if res:
                        var_name, var_value = res
                        full_name = self._to_global_name(var_name)

                        # check if we also have a setter
                        if self._query(f"mt.Setters[{var_name!r}]"):
                            readonly = False
                        else:
                            readonly = True
                        self._dict[var_name] = KeithleyProperty(
                            full_name, self, readonly
                        )
                    else:
                        break

            # get Objects, if any
            # those will define functions, tables or constants
            if self._query("mt.Objects"):
                var_name = _Nil()

                while True:

                    res = self._query(f"next(mt.Objects, {var_name!r})")

                    if res:
                        var_name, var_value = res
                        full_name = self._to_global_name(var_name)
                        if isinstance(var_value, _LuaFunction):
                            self._dict[var_name] = KeithleyFunction(full_name, self)
                        elif isinstance(var_value, _LuaTable):
                            self._dict[var_name] = KeithleyClass(full_name, self)
                        else:
                            self._dict[var_name] = KeithleyProperty(
                                full_name, self, readonly=True
                            )
                    else:
                        break

            self._lua_type = self._query("mt.luatype")

    def _load_lua_attribute(self, name: Union[str, int]) -> LuaBridgeType:

        full_name = self._to_global_name(name)

        # add to our own dict
        var_type = self._query(f"type({full_name})")

        if var_type is None:
            raise RuntimeError(f"Attribute {full_name} does not exist")

        if var_type == "table":
            self._dict[name] = KeithleyClass(full_name, self)
        elif var_type == "function":
            self._dict[name] = KeithleyFunction(full_name, self)
        else:
            self._dict[name] = KeithleyProperty(full_name, self)

        return self._dict[name]

    def _write(self, value: str) -> None:
        self._parent._write(value)

    def _query(self, value: str) -> Any:
        return self._parent._query(value)

    def _convert_input(self, value: Any) -> str:
        try:
            return self._parent._convert_input(value)
        except AttributeError:
            return value

    def __getitem__(self, key: Union[str, int]) -> Any:

        if not self._dict:
            # will raise KeithleyIOError if not connected
            self._load_lua_namespace()

        if self._lua_type in ("reading_buffer", "synchronous_table") and isinstance(
            key, int
        ):
            # bypass verification and support all integer indices for reading buffers
            return self._query(f"{self._name}[{key}]")

        # raises KeyError if the key does not exist
        accessor = self._dict[key]

        if isinstance(accessor, KeithleyProperty):
            return accessor.get()
        else:
            return accessor

    def __setitem__(self, key: Union[str, int], value: Any) -> None:

        if not self._dict:
            # will raise KeithleyIOError if not connected
            self._load_lua_namespace()

        try:
            accessor = self._dict[key]
        except KeyError:
            self.create_lua_attr(key, value)
        else:
            if isinstance(accessor, KeithleyProperty):
                accessor.set(value)
            else:
                value = self._convert_input(value)
                self._write(f"{self._name}[{key}] = {value}")
                self._load_lua_attribute(key)

    def __iter__(self) -> "KeithleyClass":

        if not self._dict:
            # will raise KeithleyIOError if not connected
            self._load_lua_namespace()

        return self

    def __dir__(self) -> List[str]:
        if not self._dict:
            try:
                self._load_lua_namespace()
            except KeithleyIOError:
                pass

        # remove all keys that are not strings (Lua allows integer keys as well)
        str_keys = [k for k in self._dict.keys() if isinstance(k, str)]

        return str_keys + list(super().__dir__())

    def __repr__(self) -> str:
        if self._lua_type:
            return (
                f"<{self.__class__.__name__}({self._name_display}, "
                f"lua_type={self._lua_type})>"
            )
        else:
            return f"<{self.__class__.__name__}({self._name_display})>"
class Keithley2600Base(KeithleyClass):
    """Keithley2600 driver
    Keithley driver for base functionality. It replicates the functionality and
    syntax from the Keithley TSP commands, as provided by the Lua scripting language.
    Attributes are created on-demand if they correspond to Keithley TSP commands.
    :param visa_address: Visa address of the instrument.
    :param visa_library: Path to visa library. Defaults to "@py" for pyvisa-py but
        another IVI library may be appropriate (NI-VISA, Keysight VISA, R&S VISA,
        tekVISA etc.). If an empty string is given, an IVI library will be used if
        installed and pyvisa-py otherwise.
    :param raise_keithley_errors: If ``True``, all Keithley errors will be raised as
        Python errors instead of being ignored. This causes significant communication
        overhead because the Keithley's error queue is read after each command. Defaults
        to ``False``.
    :param kwargs: Keyword arguments passed on to the visa connection, for instance
        baude-rate or timeout. If not given, reasonable defaults will be used.
    :cvar connection: Attribute holding a reference to the actual connection.
    :cvar connected: ``True`` if connected to an instrument, ``False`` otherwise.
    :cvar busy: ``True`` if a measurement is running, ``False`` otherwise.
    :cvar CHUNK_SIZE: Maximum length of lists which can be sent to the Keithley. Longer
        lists will be transferred in chunks.
    .. note::
        See the Keithley 2600 reference manual for all available commands and
        arguments. A dictionary of available commands will be loaded on access from the
        Keithley at runtime, if connected.
    :Examples:
        >>> keithley = Keithley2600Base('TCPIP0::192.168.2.121::INSTR')
        >>> keithley.smua.measure.v()  # measures voltage at smuA
        >>> keithley.smua.source.levelv = -40  # applies -40V to smuA
    """

    _protected_attrs = [
        "rm",
        "connection",
        "connected",
        "busy",
        "visa_address",
        "visa_library",
        "_connection_kwargs",
        "raise_keithley_errors",
        "CHUNK_SIZE",
        "_lock",
        "abort_event",
    ] + KeithleyClass._protected_attrs

    CHUNK_SIZE = 50

    def __init__(
        self,
        visa_address: str,
        visa_library: str = "@py",
        raise_keithley_errors: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(name="_G", parent=self)

        self.abort_event = threading.Event()
        self._lock = RLock()

        self.visa_address = visa_address
        self.visa_library = visa_library
        self._connection_kwargs = kwargs

        self.raise_keithley_errors = raise_keithley_errors

        # open visa resource manager and connect to keithley
        self.rm = pyvisa.ResourceManager(self.visa_library)
        self.connect(**kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.visa_address})>"

    # =============================================================================
    # Connect to keithley
    # =============================================================================

    def connect(self, **kwargs) -> bool:
        """
        Connects to Keithley.
        :param kwargs: Keyword arguments for Visa connection.
        :returns: Whether the connection succeeded.
        """
        kwargs = kwargs or self._connection_kwargs  # use specified or remembered kwargs
        try:
            self.connection = self.rm.open_resource(self.visa_address, **kwargs)
            self.connection.read_termination = "\n"
            self.connected = True
            self._dict.clear()  # reset Keithley dict
            logger.debug("Connected to Keithley at %s.", self.visa_address)
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

    def disconnect(self) -> None:
        """
        Disconnects from Keithley.
        """
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.connected = False
                del self.connection
                logger.debug("Disconnected from Keithley at %s.", self.visa_address)
            except AttributeError:
                self.connected = False
                pass

    def _get_smu_name(self, smu: KeithleyClass) -> str:
        if not re.match(r"^_G.smu([a-z])$", smu._name):
            raise ValueError(f"{smu} is not a valid SMU")
        return smu._name.split(".")[-1]
    
    def send_trigger(self) -> None:
        """
        Manually sends a trigger signal to the Keithley. This can be used for instance
        to start a pre-programmed sweep.
        """

        self._write("*trg")

    # =============================================================================
    # Define I/O
    # =============================================================================

    @contextmanager
    def _error_check(self) -> Iterator[None]:
        """
        A contextmanager to check if a command resulted in a Keithley error.
        """

        # clear any previous errors
        self.connection.write("errorqueue.clear()")

        try:
            yield
        finally:
            # check error queue and raise errors
            err = self.connection.query(f"print(errorqueue.next())")
            err = self._parse_response(err)
            if err[0] != 0:
                raise KeithleyError(err[1])

    def _write(self, value: str) -> None:
        """
        Writes text to Keithley. Input must be a string.
        """

        # only check for error when the query is not fetching the error queue
        check_for_errors = self.raise_keithley_errors and "errorqueue" not in value

        with self._lock:
            logger.debug("write: %s", value)

            if self.connection:

                if check_for_errors:
                    with self._error_check():
                        try:
                            self.connection.write(value)
                        except pyvisa.VisaIOError:
                            # ignore VisaIOError which can be caused by syntax errors
                            pass
                else:
                    self.connection.write(value)
            else:
                raise KeithleyIOError(
                    "No connection to keithley present. Try to call 'connect'."
                )

    def _query(self, value: str) -> Any:
        """
        Queries and expects response from Keithley. Input must be a string. Return value
        will be converted to Python type by :meth:`_parse_response`.
        """

        # only check for error when the query is not fetching the error queue
        check_for_errors = self.raise_keithley_errors and "errorqueue" not in value

        with self._lock:
            logger.debug("write: print(%s)", value)
            if self.connection:

                if check_for_errors:
                    with self._error_check():
                        try:
                            r = self.connection.query(f"print({value})")
                            logger.debug("read: %s", r)
                        except XDRError:
                            r = "nil"
                            logger.debug("read failed: unpack-error")
                        except pyvisa.VisaIOError:
                            # ignore VisaIOError which can be caused by syntax errors
                            pass

                else:
                    try:
                        r = self.connection.query(f"print({value})")
                        logger.debug("read: %s", r)
                    except XDRError:
                        r = "nil"
                        logger.debug("read failed: unpack-error")

                return self._parse_response(r)
            else:
                raise KeithleyIOError(
                    "No connection to keithley present. Try to call 'connect'."
                )

    def _parse_response(
        self, string: str
    ) -> Union[LuaReturnTypes, Tuple[LuaReturnTypes, ...]]:

        string_list = string.split("\t")

        converted_tuple = tuple(self._parse_single_response(s) for s in string_list)

        if len(converted_tuple) == 1:
            return converted_tuple[0]
        else:
            return converted_tuple

    @staticmethod
    def _parse_single_response(string: str) -> LuaReturnTypes:

        # Dictionary to convert from Keithley TSP to Python types.
        # Note that emtpy strings are converted to `None`. This is necessary
        # since `self.connection.query('print(func())')` returns an empty
        # string if the TSP function `func()` returns 'nil'.
        conversion_dict = {"true": True, "false": False, "nil": None, "": None}

        try:
            r = float(string)
            if r.is_integer():
                r = int(r)
        except ValueError:
            if string in conversion_dict.keys():
                r = conversion_dict[string]
            elif string.startswith("function: "):
                r = _LuaFunction(string)
            elif string.startswith("table: "):
                r = _LuaTable(string)
            else:
                r = string

        return r

    def _convert_input(self, value: Any) -> str:

        if isinstance(value, bool):
            # convert bool True to string 'true', False to string 'false'
            return str(value).lower()
        elif isinstance(value, KeithleyClass):
            # convert keithley object to string with its name
            return value._name
        elif isinstance(value, str):
            return repr(value)
        elif hasattr(value, "__iter__"):
            # convert some iterables to a TSP type list '{1,2,3,4}'
            return "{" + ", ".join([str(v) for v in value]) + "}"
        elif isinstance(value, (int, float, np.number)) and not isinstance(
            value, np.complex
        ):
            return str(value)
        else:
            raise ValueError(
                f"Unsupported value type '{type(value).__name__}' of input '{value!r}'"
            )


class Keithley2600(Keithley2600Base):
    def __init__(
        self,
        visa_address: str,
        visa_library: str = "@py",
        raise_keithley_errors: bool = False,
        **kwargs,
    ) -> None:
        Keithley2600Base.__init__(
            self,
            visa_address,
            visa_library,
            raise_keithley_errors=raise_keithley_errors,
            **kwargs,
        )

        self._measurement_lock = threading.RLock()

    @property
    def busy(self) -> bool:
        """True if a measurement is running, False otherwise."""

        gotten = self._measurement_lock.acquire(blocking=False)

        if gotten:
            self._measurement_lock.release()

        return not gotten

    # =============================================================================
    # Define lower level control functions
    # =============================================================================

    def read_error_queue(self) -> List[Tuple[LuaReturnTypes, ...]]:
        """
        Returns all entries from the Keithley error queue and clears the queue.
        :returns: List of errors from the Keithley error queue. Each entry is a tuple
            ``(error_code, message, severity, error_node)``. If the queue is empty, an
            empty list is returned.
        """

        error_list = []

        while self.errorqueue.count > 0:
            error_list.append(self.errorqueue.next())

        return error_list

    @staticmethod
    def read_buffer(buffer: KeithleyClass) -> List[float]:
        """
        Reads buffer values and returns them as a list. This can be done more quickly by
        calling :attr:`buffer.readings` but such a call may fail due to I/O limitations
        of the keithley if the returned list is too long.
        :param buffer: A keithley buffer instance.
        :returns: A list with buffer readings.
        """
        list_out = []
        for i in range(0, int(buffer.n)):
            list_out.append(buffer.readings.getreading(i + 1))

        return list_out

    def set_integration_time(self, smu: KeithleyClass, t_int: float) -> None:
        """
        Sets the integration time of SMU for measurements in sec.
        :param smu: A keithley smu instance.
        :param t_int: Integration time in sec. Value must be between 1/1000 and 25 power
            line cycles (50Hz or 60 Hz).
        :raises: :class:`ValueError` for too short or too long integration times.
        """

        # determine number of power-line-cycles used for integration
        freq = self.localnode.linefreq
        nplc = t_int * freq

        if nplc < 0.001 or nplc > 25:
            raise ValueError(
                "Integration time must be between 0.001 and 25 "
                f"power line cycles of 1/({freq} Hz)."
            )
        smu.measure.nplc = nplc

    def voltage_sweep_single_smu(
            self,
            smu: KeithleyClass,
            smu_sweeplist: Sequence[float],
            t_int: float,
            delay: float,
            pulsed: bool,
        ) -> Tuple[List[float], List[float]]:
            """
            Sweeps the voltage through the specified list of steps at the given
            SMU. Measures and returns the current and voltage during the sweep.
            :param smu: A keithley smu instance.
            :param smu_sweeplist: Voltages to sweep through (can be a numpy array, list,
                tuple or any other iterable of numbers).
            :param t_int: Integration time per data point. Must be between 0.001 to 25 times
                the power line frequency (50Hz or 60Hz).
            :param delay: Settling delay before each measurement. A value of -1
                automatically starts a measurement once the current is stable.
            :param pulsed: Select pulsed or continuous sweep. In a pulsed sweep, the voltage
                is always reset to zero between data points.
            :returns: Lists of voltages and currents measured during the sweep (in
                Volt and Ampere, respectively): ``(v_smu, i_smu)``.
            """

            with self._measurement_lock:

                # Define lists containing results.
                # If we abort early, we have something to return.
                v_smu, i_smu = [], []

                if self.abort_event.is_set():
                    return v_smu, i_smu

                # setup smu to sweep through list on trigger
                # send sweep_list over in chunks if too long
                if len(smu_sweeplist) > self.CHUNK_SIZE:
                    self.create_lua_attr("python_driver_list", [])
                    for num in smu_sweeplist:
                        self.table.insert(self.python_driver_list, num)
                    smu.trigger.source.listv(self.python_driver_list)
                    self.delete_lua_attr("python_driver_list")
                else:
                    smu.trigger.source.listv(smu_sweeplist)

                smu.trigger.source.action = smu.ENABLE

                # CONFIGURE INTEGRATION TIME FOR EACH MEASUREMENT
                self.set_integration_time(smu, t_int)

                # CONFIGURE SETTLING TIME FOR GATE VOLTAGE, I-LIMIT, ETC...
                smu.measure.delay = delay

                # enable autorange if not in high capacitance mode
                if smu.source.highc == smu.DISABLE:
                    smu.measure.autorangei = smu.AUTORANGE_ON

                # smu.trigger.source.limiti = 0.1

                smu.source.func = smu.OUTPUT_DCVOLTS

                # 2-wire measurement (use SENSE_REMOTE for 4-wire)
                # smu.sense = smu.SENSE_LOCAL

                # clears SMU buffers
                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()

                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

                # display current values during measurement
                smu_name = self._get_smu_name(smu)
                getattr(self.display, smu_name).measure.func = self.display.MEASURE_DCAMPS

                # SETUP TRIGGER ARM AND COUNTS
                # trigger count = number of data points in measurement
                # arm count = number of times the measurement is repeated (set to 1)

                npts = len(smu_sweeplist)
                smu.trigger.count = npts

                # SET THE MEASUREMENT TRIGGER ON BOTH SMU'S
                # Set measurement to trigger once a change in the gate value on
                # sweep smu is complete, i.e., a measurement will occur
                # after the voltage is stepped.
                # Both channels should be set to trigger on the sweep smu event
                # so the measurements occur at the same time.

                # enable smu
                smu.trigger.measure.action = smu.ENABLE

                # measure current and voltage on trigger, store in buffer of smu
                smu.trigger.measure.iv(smu.nvbuffer1, smu.nvbuffer2)

                # initiate measure trigger when source is complete
                smu.trigger.measure.stimulus = smu.trigger.SOURCE_COMPLETE_EVENT_ID

                # SET THE ENDPULSE ACTION TO HOLD
                # Options are SOURCE_HOLD AND SOURCE_IDLE, hold maintains same voltage
                # throughout step in sweep (typical IV sweep behavior). idle will allow
                # pulsed IV sweeps.

                if pulsed:
                    end_pulse_action = 0  # SOURCE_IDLE
                elif not pulsed:
                    end_pulse_action = 1  # SOURCE_HOLD
                else:
                    raise TypeError("'pulsed' must be of type 'bool'.")

                smu.trigger.endpulse.action = end_pulse_action

                # SET THE ENDSWEEP ACTION TO HOLD IF NOT PULSED
                # Output voltage will be held after sweep is done!

                smu.trigger.endsweep.action = end_pulse_action

                # SET THE EVENT TO TRIGGER THE SMU'S TO THE ARM LAYER
                # A typical measurement goes from idle -> arm -> trigger.
                # The 'trigger.event_id' option sets the transition arm -> trigger
                # to occur after sending *trg to the instrument.

                smu.trigger.arm.stimulus = self.trigger.EVENT_ID

                # Prepare an event blender (blender #1) that triggers when
                # the smua enters the trigger layer or reaches the end of a
                # single trigger layer cycle.

                # triggers when either of the stimuli are true ('or enable')
                self.trigger.blender[1].orenable = True
                self.trigger.blender[1].stimulus[1] = smu.trigger.ARMED_EVENT_ID
                self.trigger.blender[1].stimulus[2] = smu.trigger.PULSE_COMPLETE_EVENT_ID

                # SET THE smu SOURCE STIMULUS TO BE EVENT BLENDER #1
                # A source measure cycle within the trigger layer will occur when
                # either the trigger layer is entered (termed 'armed event') for the
                # first time or a single cycle of the trigger layer is complete (termed
                # 'pulse complete event').

                smu.trigger.source.stimulus = self.trigger.blender[1].EVENT_ID

                # PREPARE AN EVENT BLENDER (blender #2) THAT TRIGGERS WHEN BOTH SMU'S
                # HAVE COMPLETED A MEASUREMENT.
                # This is needed to prevent the next source measure cycle from occurring
                # before the measurement on both channels is complete.

                self.trigger.blender[2].orenable = True  # triggers when both stimuli are true
                self.trigger.blender[2].stimulus[1] = smu.trigger.MEASURE_COMPLETE_EVENT_ID

                # SET THE SMU ENDPULSE STIMULUS TO BE EVENT BLENDER #2
                smu.trigger.endpulse.stimulus = self.trigger.blender[2].EVENT_ID

                # TURN ON smu
                smu.source.output = smu.OUTPUT_ON

                # INITIATE MEASUREMENT
                # prepare SMUs to wait for trigger
                smu.trigger.initiate()

                # send trigger
                self.send_trigger()

                # CHECK STATUS BUFFER FOR MEASUREMENT TO FINISH
                # Possible return values:
                # 6 = smua and smub sweeping
                # 4 = only smub sweeping
                # 2 = only smua sweeping
                # 0 = neither smu sweeping

                # while loop that runs until the sweep begins
                while self.status.operation.sweeping.condition == 0:
                    time.sleep(0.1)

                # while loop that runs until the sweep ends
                while self.status.operation.sweeping.condition > 0:
                    time.sleep(0.1)

                # EXTRACT DATA FROM SMU BUFFERS
                i_smu = self.read_buffer(smu.nvbuffer1)
                v_smu = self.read_buffer(smu.nvbuffer2)

                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()

                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

                return v_smu, i_smu

### voltage log sweep for single smu
    def vLog_single(
            self,
            smu: KeithleyClass,
            log_parameters: Tuple[float],
            t_int: float,
            delay: float,
            pulsed: bool,
        ) -> Tuple[List[float], List[float]]:
            """
            Sweeps the voltage through the specified list of steps at the given
            SMU. Measures and returns the current and voltage during the sweep.
            :param smu: A keithley smu instance.
            :param smu_sweeplist: Voltages to sweep through (can be a numpy array, list,
                tuple or any other iterable of numbers).
            :param t_int: Integration time per data point. Must be between 0.001 to 25 times
                the power line frequency (50Hz or 60Hz).
            :param delay: Settling delay before each measurement. A value of -1
                automatically starts a measurement once the current is stable.
            :param pulsed: Select pulsed or continuous sweep. In a pulsed sweep, the voltage
                is always reset to zero between data points.
            :returns: Lists of voltages and currents measured during the sweep (in
                Volt and Ampere, respectively): ``(v_smu, i_smu)``.
            """

            with self._measurement_lock:

                # Define lists containing results.
                # If we abort early, we have something to return.
                v_smu, i_smu = [], []

                if self.abort_event.is_set():
                    return v_smu, i_smu

                # setup smu to sweep through list on trigger
                # send sweep_list over in chunks if too long
                # if len(smu_sweeplist) > self.CHUNK_SIZE:
                #     self.create_lua_attr("python_driver_list", [])
                #     for num in smu_sweeplist:
                #         self.table.insert(self.python_driver_list, num)
                #     smu.trigger.source.listv(self.python_driver_list)
                #     self.delete_lua_attr("python_driver_list")
                # else:
                # smu.trigger.source.listi(smu_sweeplist)

                smu.trigger.source.logi(log_parameters)

                smu.trigger.source.action = smu.ENABLE

                # CONFIGURE INTEGRATION TIME FOR EACH MEASUREMENT
                self.set_integration_time(smu, t_int)

                # CONFIGURE SETTLING TIME FOR GATE VOLTAGE, I-LIMIT, ETC...
                smu.measure.delay = delay

                # enable autorange if not in high capacitance mode
                if smu.source.highc == smu.DISABLE:
                    smu.measure.autorangei = smu.AUTORANGE_ON

                # smu.trigger.source.limiti = 0.1

                smu.source.func = smu.OUTPUT_DCAMPS

                # 2-wire measurement (use SENSE_REMOTE for 4-wire)
                # smu.sense = smu.SENSE_LOCAL

                # clears SMU buffers
                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()

                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

                # display current values during measurement
                smu_name = self._get_smu_name(smu)
                getattr(self.display, smu_name).measure.func = self.display.MEASURE_DCVOLTS

                # SETUP TRIGGER ARM AND COUNTS
                # trigger count = number of data points in measurement
                # arm count = number of times the measurement is repeated (set to 1)

                npts = len(log_parameters)
                smu.trigger.count = npts

                # SET THE MEASUREMENT TRIGGER ON BOTH SMU'S
                # Set measurement to trigger once a change in the gate value on
                # sweep smu is complete, i.e., a measurement will occur
                # after the voltage is stepped.
                # Both channels should be set to trigger on the sweep smu event
                # so the measurements occur at the same time.

                # enable smu
                smu.trigger.measure.action = smu.ENABLE

                # measure current and voltage on trigger, store in buffer of smu
                smu.trigger.measure.iv(smu.nvbuffer1, smu.nvbuffer2)

                # initiate measure trigger when source is complete
                smu.trigger.measure.stimulus = smu.trigger.SOURCE_COMPLETE_EVENT_ID

                # SET THE ENDPULSE ACTION TO HOLD
                # Options are SOURCE_HOLD AND SOURCE_IDLE, hold maintains same voltage
                # throughout step in sweep (typical IV sweep behavior). idle will allow
                # pulsed IV sweeps.

                if pulsed:
                    end_pulse_action = 0  # SOURCE_IDLE
                elif not pulsed:
                    end_pulse_action = 1  # SOURCE_HOLD
                else:
                    raise TypeError("'pulsed' must be of type 'bool'.")

                smu.trigger.endpulse.action = end_pulse_action

                # SET THE ENDSWEEP ACTION TO HOLD IF NOT PULSED
                # Output voltage will be held after sweep is done!

                smu.trigger.endsweep.action = end_pulse_action

                # SET THE EVENT TO TRIGGER THE SMU'S TO THE ARM LAYER
                # A typical measurement goes from idle -> arm -> trigger.
                # The 'trigger.event_id' option sets the transition arm -> trigger
                # to occur after sending *trg to the instrument.

                smu.trigger.arm.stimulus = self.trigger.EVENT_ID

                # Prepare an event blender (blender #1) that triggers when
                # the smua enters the trigger layer or reaches the end of a
                # single trigger layer cycle.

                # triggers when either of the stimuli are true ('or enable')
                self.trigger.blender[1].orenable = True
                self.trigger.blender[1].stimulus[1] = smu.trigger.ARMED_EVENT_ID
                self.trigger.blender[1].stimulus[2] = smu.trigger.PULSE_COMPLETE_EVENT_ID

                # SET THE smu SOURCE STIMULUS TO BE EVENT BLENDER #1
                # A source measure cycle within the trigger layer will occur when
                # either the trigger layer is entered (termed 'armed event') for the
                # first time or a single cycle of the trigger layer is complete (termed
                # 'pulse complete event').

                smu.trigger.source.stimulus = self.trigger.blender[1].EVENT_ID

                # PREPARE AN EVENT BLENDER (blender #2) THAT TRIGGERS WHEN BOTH SMU'S
                # HAVE COMPLETED A MEASUREMENT.
                # This is needed to prevent the next source measure cycle from occurring
                # before the measurement on both channels is complete.

                self.trigger.blender[2].orenable = True  # triggers when both stimuli are true
                self.trigger.blender[2].stimulus[1] = smu.trigger.MEASURE_COMPLETE_EVENT_ID

                # SET THE SMU ENDPULSE STIMULUS TO BE EVENT BLENDER #2
                smu.trigger.endpulse.stimulus = self.trigger.blender[2].EVENT_ID

                # TURN ON smu
                smu.source.output = smu.OUTPUT_ON

                # INITIATE MEASUREMENT
                # prepare SMUs to wait for trigger
                smu.trigger.initiate()

                # send trigger
                self.send_trigger()

                # CHECK STATUS BUFFER FOR MEASUREMENT TO FINISH
                # Possible return values:
                # 6 = smua and smub sweeping
                # 4 = only smub sweeping
                # 2 = only smua sweeping
                # 0 = neither smu sweeping

                # while loop that runs until the sweep begins
                while self.status.operation.sweeping.condition == 0:
                    time.sleep(0.1)

                # while loop that runs until the sweep ends
                while self.status.operation.sweeping.condition > 0:
                    time.sleep(0.1)

                # EXTRACT DATA FROM SMU BUFFERS
                i_smu = self.read_buffer(smu.nvbuffer1)
                v_smu = self.read_buffer(smu.nvbuffer2)

                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()

                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

                return v_smu, i_smu
    
    def setA_dMeasIV(
        self,
        smu1: KeithleyClass,
        smu2: KeithleyClass,
        smu1_sweeplist: Sequence[float],
        smu2_sweeplist: Sequence[float],
        current: float,
        time: float,
        t_int: float,
        delay: float,
    ) -> Tuple[List[float], List[float], List[float], List[float]]:

        smu2_sweeplist = [0]*len(smu1_sweeplist)
        """
        Sweeps voltages at two SMUs. Measures and returns current and voltage
        during sweep.

        :param smu1: 1st keithley smu instance to be swept.
        :param smu2: 2nd keithley smu instance to be swept.
        :param smu1_sweeplist: Voltages to sweep at ``smu1`` (can be a numpy array,
            list, tuple or any other iterable with numbers).
        :param smu2_sweeplist: Voltages to sweep at ``smu2`` (can be a numpy array,
            list, tuple or any other iterable with numbers).
        :param t_int: Integration time per data point. Must be between 0.001 to 25 times
            the power line frequency (50Hz or 60Hz).
        :param delay: Settling delay before each measurement. A value of -1
            automatically starts a measurement once the current is stable.
        :param pulsed: Select pulsed or continuous sweep. In a pulsed sweep, the voltage
            is always reset to zero between data points.
        :returns: Lists of voltages and currents measured during the sweep (in
            Volt and Ampere, respectively): ``(v_smu1, i_smu1, v_smu2,
            i_smu2)``.
        """

        with self._measurement_lock:

            if len(smu1_sweeplist) != len(smu2_sweeplist):
                raise ValueError("Sweep lists must have equal lengths")

            # Define lists containing results.
            # If we abort early, we have something to return.
            v_smu1, i_smu1, v_smu2, i_smu2 = [], [], [], []

            if self.abort_event.is_set():
                return v_smu1, i_smu1, v_smu2, i_smu2

            # Setup smu1/smu2 for time series measurement.

            self.trigger.timer[1].delay = 0.001
            self.trigger.timer[2].delay = 60
            self.trigger.timer[1].count = 1000
            self.trigger.timer[2].count = 1
            self.trigger.timer[1].passthrough = 0
            self.trigger.timer[2].passthrough = 0
            self.trigger.timer[1].stimulus = smu1.trigger.ARMED_EVENT_ID
            self.trigger.timer[2].stimulus = smu1.trigger.ARMED_EVENT_ID

            # CONFIGURE INTEGRATION TIME FOR EACH MEASUREMENT
            self.set_integration_time(smu1, t_int)
            self.set_integration_time(smu2, t_int)

            # CONFIGURE SETTLING TIME FOR GATE VOLTAGE, I-LIMIT, ETC...
            smu1.measure.delay = delay
            smu2.measure.delay = delay

            # enable autorange if not in high capacitance mode
            if smu1.source.highc == smu1.DISABLE:
                smu1.measure.autorangei = smu1.AUTORANGE_ON
            if smu2.source.highc == smu2.DISABLE:
                smu2.measure.autorangei = smu2.AUTORANGE_ON

            # smu1.trigger.source.limiti = 0.1
            # smu2.trigger.source.limiti = 0.1

            smu1.source.func = smu1.OUTPUT_DCAMPS
            smu2.source.func = smu2.OUTPUT_DCVOLTS

            # 2-wire measurement (use SENSE_REMOTE for 4-wire)
            # smu1.sense = smu1.SENSE_LOCAL
            # smu2.sense = smu2.SENSE_LOCAL

            # CLEAR BUFFERS
            for smu in [smu1, smu2]:
                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()
                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

            # display current values during measurement
            for smu in (smu1, smu2):
                smu_name = self._get_smu_name(smu)
                getattr(self.display, smu_name).measure.func = self.display.MEASURE_DCAMPS

            # SETUP TRIGGER ARM AND COUNTS
            # trigger count = number of data points in measurement
            # arm count = number of times the measurement is repeated (set to 1)
            # testTime = samples / sample per sec
            npts = time/t_int
            # npts = len(smu1_sweeplist)

            smu1.trigger.count = npts
            smu2.trigger.count = npts

            # SET THE MEASUREMENT TRIGGER ON BOTH SMU'S
            # Set measurement to trigger once a change in the gate value on
            # sweep smu is complete, i.e., a measurement will occur
            # after the voltage is stepped.
            # Both channels should be set to trigger on the sweep smu event
            # so the measurements occur at the same time.

            # enable smu
            smu1.trigger.measure.action = smu1.ENABLE
            smu2.trigger.measure.action = smu2.ENABLE

            # measure current and voltage on trigger, store in buffer of smu
            smu1.trigger.measure.iv(smu1.nvbuffer1, smu1.nvbuffer2)
            smu2.trigger.measure.iv(smu2.nvbuffer1, smu2.nvbuffer2)

            # initiate measure trigger when source is complete
            smu1.trigger.measure.stimulus = self.trigger.timer[1].EVENT_ID
            smu2.trigger.measure.stimulus = self.trigger.timer[1].EVENT_ID

            # SET THE ENDPULSE ACTION TO HOLD
            # Options are SOURCE_HOLD AND SOURCE_IDLE, hold maintains same voltage
            # throughout step in sweep (typical IV sweep behavior). idle will allow
            # pulsed IV sweeps.

            # if pulsed:
            #     end_pulse_action = 0  # SOURCE_IDLE
            # elif not pulsed:
            #     end_pulse_action = 1  # SOURCE_HOLD
            # else:
            #     raise TypeError("'pulsed' must be of type 'bool'.")

            # smu1.trigger.endpulse.action = end_pulse_action
            # smu2.trigger.endpulse.action = end_pulse_action

            # SET THE ENDSWEEP ACTION TO HOLD IF NOT PULSED
            # Output voltage will be held after sweep is done!

            # smu1.trigger.endsweep.action = end_pulse_action
            # smu2.trigger.endsweep.action = end_pulse_action

            # SET THE EVENT TO TRIGGER THE SMU'S TO THE ARM LAYER
            # A typical measurement goes from idle -> arm -> trigger.
            # The 'trigger.event_id' option sets the transition arm -> trigger
            # to occur after sending *trg to the instrument.

            smu1.trigger.arm.stimulus = self.trigger.timer[1].EVENT_ID

            # Prepare an event blender (blender #1) that triggers when
            # the smua enters the trigger layer or reaches the end of a
            # single trigger layer cycle.

            # triggers when either of the stimuli are true ('or enable')
            # self.trigger.blender[1].orenable = True
            # self.trigger.blender[1].stimulus[1] = smu1.trigger.ARMED_EVENT_ID
            # self.trigger.blender[1].stimulus[2] = smu1.trigger.PULSE_COMPLETE_EVENT_ID

            # SET THE smu1 SOURCE STIMULUS TO BE EVENT BLENDER #1
            # A source measure cycle within the trigger layer will occur when
            # either the trigger layer is entered (termed 'armed event') for the
            # first time or a single cycle of the trigger layer is complete (termed
            # 'pulse complete event').

            smu1.trigger.measure.stimulus = self.trigger.timer[1].EVENT_ID

            # PREPARE AN EVENT BLENDER (blender #2) THAT TRIGGERS WHEN BOTH SMU'S
            # HAVE COMPLETED A MEASUREMENT.
            # This is needed to prevent the next source measure cycle from occurring
            # before the measurement on both channels is complete.

            # self.trigger.blender[2].orenable = False  # triggers when both stimuli are true
            # self.trigger.blender[2].stimulus[1] = smu1.trigger.MEASURE_COMPLETE_EVENT_ID
            # self.trigger.blender[2].stimulus[2] = smu2.trigger.MEASURE_COMPLETE_EVENT_ID
            # Configure the endpulse action to achieve a pulse.
            smu1.trigger.endpulse.action = smu1.SOURCE_IDLE
            smu2.trigger.endpulse.action = smu2.SOURCE_IDLE
            # Trigger the SMU end pulse action with a pulse width timer event.
            smu1.trigger.endpulse.stimulus = self.trigger.timer[2].EVENT_ID
            smu2.trigger.endpulse.stimulus = self.trigger.timer[2].EVENT_ID

            # SET THE smu1 ENDPULSE STIMULUS TO BE EVENT BLENDER #2
            # smu1.trigger.endpulse.stimulus = self.trigger.blender[2].EVENT_ID
            smu1.trigger.arm.count = 0
            smu1.trigger.count = 1
            smu2.trigger.arm.count = 0
            smu2.trigger.count = 1

            self.apply_current(smu1, current)

            # TURN ON smu1 AND smu2
            smu1.source.output = smu1.OUTPUT_ON
            smu2.source.output = smu2.OUTPUT_ON

            # INITIATE MEASUREMENT
            # prepare SMUs to wait for trigger
            smu1.trigger.initiate()
            smu2.trigger.initiate()

            # send trigger
            # self.send_trigger()

            # CHECK STATUS BUFFER FOR MEASUREMENT TO FINISH
            # Possible return values:
            # 6 = smua and smub measuring
            # 4 = only smub measuring
            # 2 = only smua measuring
            # 0 = neither smu measuring

            # while loop that runs until the time series begins
            while self.status.operation.trigger.timer[1].enable == 0:
                time.sleep(0.1)

            # # while loop that runs until the time series ends
            while self.status.operation.trigger.timer[2].enable > 0:
                time.sleep(0.1)

            # EXTRACT DATA FROM SMU BUFFERS
            i_smu1 = self.read_buffer(smu1.nvbuffer1)
            v_smu1 = self.read_buffer(smu1.nvbuffer2)
            i_smu2 = self.read_buffer(smu2.nvbuffer1)
            v_smu2 = self.read_buffer(smu2.nvbuffer2)

            # CLEAR BUFFERS
            for smu in [smu1, smu2]:
                smu.nvbuffer1.clear()
                smu.nvbuffer2.clear()
                smu.nvbuffer1.clearcache()
                smu.nvbuffer2.clearcache()

            return v_smu1, i_smu1, v_smu2, i_smu2
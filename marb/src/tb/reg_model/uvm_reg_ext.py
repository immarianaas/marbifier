from pyuvm import *
from .uvm_reg_item import uvm_reg_item
from .uvm_reg_model import *

class uvm_reg_ext(uvm_reg):
    def __init__(self, name, n_bits):
        super().__init__(name)

        self._n_bits            = n_bits
        self._is_busy           = False
        self._write_in_progress = False
        self._read_in_progress  = False

    def get_n_bits(self):
        return self._n_bits

    def get_local_map(self):
        return self._parent.get_map()

    # 18.4.4.9 / 18.8.5.3
    async def write(self, value):
        """Write of ~value~ to register through register-model, return ~status~"""
        print("write func")
        # create an abstract transaction for this operation
        rw = uvm_reg_item.create("write_item")

        rw.set_element(self)
        rw.set_element_kind(uvm_elem_kind_e.REG)
        rw.set_kind(uvm_access_e.UVM_WRITE)
        rw.set_value(value)

        rw.set_local_map(self.get_local_map())

        # perform write-task
        await self.do_write(rw)

        return rw.get_status()

    # 18.4.4.10 / 18.8.5.4
    async def read(self):
        """Read value from register through register model, return ~status~ and ~value~"""

        #
        status, value = await self._read()
        return status, value

    async def _read(self):
        """Local read task"""

        # create an abstract transaction for this operation
        rw = uvm_reg_item.create("read_item")

        rw.set_element(self)
        rw.set_element_kind(uvm_elem_kind_e.REG)
        rw.set_kind(uvm_access_e.UVM_READ)
        rw.set_local_map(self.get_local_map())

        # perform read-task
        await self.do_read(rw)

        return rw.status, rw.value

    async def do_write(self, rw):
        """Invokes write function of the local map"""
        self._write_in_progress = True

        # truncate value to n_bits
        ...

        rw.set_status(uvm_status_e.UVM_IS_OK)

        # front door
        local_map = rw.get_local_map()
        system_map = local_map.get_root_map()

        self._is_busy = True

        # invokes write task of local map
        await local_map.do_write(rw)

        self._is_busy = False

        # auto prediction
        if system_map.get_auto_predict():
            ...

        self._write_in_progress = False

    async def do_read(self, rw):
        """Invokes read function of the local map"""
        self._read_in_progress = True

        rw.set_status(uvm_status_e.UVM_IS_OK)

        # front door
        local_map = rw.get_local_map()
        system_map = local_map.get_root_map()

        self._is_busy = True

        # invokes read task of the local map
        await local_map.do_read(rw)

        self._is_busy = False

        # auto prediction
        if system_map.get_auto_predict():
            ...

        self._read_in_progress = False

    def __str__(self) -> str:
        """Defines the string form of a register"""
        out = f"{self.get_name()}: fields = [ "
        for f in self.get_fields():
            out += f"{f.get_name()} "
        out += "]"
        return out

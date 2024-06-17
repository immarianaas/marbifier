from pyuvm import *
from .uvm_reg_model import *
from .uvm_reg_adapter import uvm_reg_adapter
from uvc.apb.src import *

class cl_reg_adapter(uvm_reg_adapter):
    def __init__(self, name = "cl_reg_adapter"):
        super().__init__(name)
        self.parent_sequence = uvm_sequence()

    def reg2bus(self, rw):
        apb = cl_apb_seq_item.create("apb_item")

        if rw.data == None:
            rw.data = 0

        if rw.kind == uvm_access_e.UVM_READ:
            with apb.randomize_with() as it:
                it.access == 0
                it.addr == rw.addr
                it.data == rw.data

        elif rw.kind == uvm_access_e.UVM_WRITE:
            with apb.randomize_with() as it:
                it.access == 1
                it.addr == rw.addr
                it.data == rw.data

        return apb

    def bus2reg(self, bus_item, rw):
        assert isinstance(bus_item, cl_apb_seq_item), {
            "Bus item is not of type APB item"}

        apb = bus_item

        if apb.access == apb_common.AccessType.RD:
            rw.kind = uvm_access_e.UVM_READ
        elif apb.access == apb_common.AccessType.WR:
            rw.kind = uvm_access_e.UVM_WRITE

        rw.addr   = apb.addr
        rw.data   = apb.data
        rw.status = uvm_status_e.UVM_IS_OK

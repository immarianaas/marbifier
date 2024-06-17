from pyuvm import *
from .cl_ctrl_reg import cl_ctrl_reg
from .cl_dprio_reg import cl_dprio_reg
from .uvm_reg_map_ext import uvm_reg_map_ext

class cl_reg_block(uvm_reg_block):
    def __init__(self, name = "cl_reg_block"):
        super().__init__(name)

        self.bus_map   = None
        self.ctrl_reg  = None
        self.dprio_reg = None

    def build(self):
        self.ctrl_reg = cl_ctrl_reg("ctrl_reg")
        self.ctrl_reg.configure(self)
        self.ctrl_reg.build()

        self.dprio_reg = cl_dprio_reg("dprio_reg")
        self.dprio_reg.configure(self)
        self.dprio_reg.build()

        self.bus_map = uvm_reg_map_ext("bus_map")
        self.bus_map.configure(parent = self, base_addr = 0)

        self.bus_map.add_reg(reg = self.ctrl_reg, offset  = 0)
        self.bus_map.add_reg(reg = self.dprio_reg, offset = 4)

    def get_map(self):
        return self.bus_map
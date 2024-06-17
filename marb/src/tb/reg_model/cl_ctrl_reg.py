from pyuvm import *
from .uvm_reg_ext import uvm_reg_ext

class cl_ctrl_reg(uvm_reg_ext):
    def __init__(self, name = "cl_ctrl_reg", n_bits = 32):
        super().__init__(name, n_bits)

    def build(self):
        # Define the register fields
        F_en = uvm_reg_field("en")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_en.configure(self, 1, 0, "RW", 0, 0)

        # Define the register fields
        F_mode = uvm_reg_field("mode")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_mode.configure(self, 2, 1, "RW", 0, 0)

        # Define the register fields
        F_unused = uvm_reg_field("unused")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_unused.configure(self, 29, 2, "RW", 0, 0)
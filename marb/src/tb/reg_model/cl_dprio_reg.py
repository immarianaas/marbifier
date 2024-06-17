from pyuvm import *
from .uvm_reg_ext import uvm_reg_ext

class cl_dprio_reg(uvm_reg_ext):
    def __init__(self, name = "cl_dprio_reg", n_bits = 32):
        super().__init__(name, n_bits)

    def build(self):
        # Define the register fields
        F_cif0 = uvm_reg_field("cif0")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_cif0.configure(self, 8, 0, "RW", 0, 0)

        # Define the register fields
        F_cif1 = uvm_reg_field("cif1")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_cif1.configure(self, 8, 8, "RW", 0, 0)

        # Define the register fields
        F_cif2 = uvm_reg_field("cif2")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_cif2.configure(self, 8, 16, "RW", 0, 0)

        # Define the register fields
        F_extra = uvm_reg_field("extra")
        # Configure (size, lsb_pos, access, is_volatile, reset)
        F_extra.configure(self, 8, 24, "RW", 0, 0)
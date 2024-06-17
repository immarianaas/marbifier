from enum import Enum

class uvm_access_e(Enum):
    """Type of access for operation:
    - UVM_READ
    - UVM_WRITE
    - UVM_BURST_READ
    - UVM_BURST_WRITE """

    UVM_READ        = 0
    UVM_WRITE       = 1
    UVM_BURST_READ  = 2
    UVM_BURST_WRITE = 3

class uvm_elem_kind_e(Enum):
    """Kind of element:
    - REG
    - MEM
    - FIELD """

    REG     = 0
    MEM     = 1
    FIELD   = 2

class uvm_status_e(Enum):
    """Status of register access:
    - UVM_IS_OK
    - UVM_NOT_OK
    - UVM_HAS_X """

    UVM_IS_OK   = 0
    UVM_NOT_OK  = 1
    UVM_HAS_X   = 2

class uvm_reg_bus_op():
    """Abstract register bus operation for performing access"""
    def __init__(self, kind = None, addr = None, data = None, n_bits = None, status:uvm_status_e = None):
        self.kind   = kind
        self.addr   = addr
        self.data   = data
        self.n_bits = n_bits
        self.status = status
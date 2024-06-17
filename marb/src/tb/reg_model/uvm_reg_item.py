from pyuvm import *

# 19.1.1.1 Class declaration
class uvm_reg_item(uvm_sequence_item):
    """Defines abstract register transaction item,
    no bus-specific information is present"""
    def __init__(self, name):
        super().__init__(name)

        # kind of element being accessed: REG, MEM, FIELD.
        # See <uvm_elem_kind_op>
        self.element_kind = None

        # handle to RegModel element for transaction of <element_kind>
        self.element = None

        # kind of access: READ or WRITE
        self.kind = None

        # the value to write or after completion the value read from DUT
        self.value = None

        # the offset
        self.offset = None

        # result of the transaction: IS_OK, HAS_X, or ERROR.
        self.status = None

        # local map of the element, used to obtain addresses
        self.local_map = None

        # original map specified for the operation
        self.map = None

        # path being used: <UVM_FRONTDOOR> or <UVM_BACKDOOR>.
        self.path = "UVM_FRONTDOOR"

        # sequence from which the operation originated
        self.parent = None

        # priority requested of this transfer
        self.prior = -1

        # handle to optional user data
        self.extension = None

        # file name from where this transaction originated,
        # if provided at the call site.
        self.fname = None

        # line number for the file where the transaction originated,
        # if provided at the call site.
        self.lineno = None

    def set_element_kind(self, element_kind):
        self.element_kind = element_kind

    def get_element_kind(self):
        return self.element_kind

    def set_element(self, element):
        self.element = element

    def get_element(self):
        return self.element

    def set_kind(self, kind):
        self.kind = kind

    def get_kind(self):
        return self.kind

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_offset(self, offset):
        self.offset = offset

    def get_offset(self):
        return self.offset

    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status

    def set_local_map(self, map):
        self.local_map = map

    def get_local_map(self):
        return self.local_map

    def set_map(self, map):
        self.map = map

    def get_map(self):
        return self.map

    def set_parent_sequence(self, parent):
        self.parent = parent

    def get_parent_sequence(self):
        return self.parent

    def set_priority(self, value):
        self.prior = value

    def get_priority(self):
        return self.prior

    def set_extension(self, extension):
        self.extension = extension

    def get_extension(self):
        return self.extension

    def set_fname(self, fname):
        self.fname = fname

    def get_fname(self):
        return self.fname

    def set_lineno(self, line):
        self.lineno = line

    def get_lineno(self):
        return self.lineno

    def __str__(self) -> str:
        return (
            f"uvm_reg_item {self.get_full_name()}: "
            f"kind={self.kind}, ele_kind={self.element_kind}, "
            f"ele_name={self.element.get_name()}, value={self.value}"
        )

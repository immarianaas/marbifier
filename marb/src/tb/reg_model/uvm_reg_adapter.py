from pyuvm import *

# 19.2.1.1 Class declaration
class uvm_reg_adapter(uvm_object):
    """This class defines an interface for converting between <uvm_reg_bus_op>
    and a specific bus transaction."""

    # 19.2.1.2.1
    def __init__(self, name=""):
        super().__init__(name)

        self._item           = None
        self.parent_sequence = None

    # 19.2.1.2.5
    def reg2bus(self, rw):
        """Convert <uvm_reg_bus_op> to new bus-specific <uvm_sequence_item>"""
        ...

    # 19.2.1.2.6
    def bus2reg(self, bus_item, rw):
        """Copy members of given bus-specific ~bus_item~ to the provided ~bus_rw~ item"""
        ...

    # 19.2.1.2.7
    def get_item(self):
        return self._item

    def set_item(self, item):
        self._item = item
from enum import Enum, IntEnum
import vsc
from .cl_apb_seq_item import cl_apb_seq_item

class DriverType(Enum):
    """ Type of driver: not set (NOT_SET), producer (PRODUCER) or consumer (CONSUMER)"""
    NOT_SET  = 0
    CONSUMER = 1
    PRODUCER = 2

class AccessType(IntEnum):
    """ Type of access: read (RD) or write (WR)"""
    RD = 0
    WR = 1

class SequenceItemOverride(Enum):
    """ DEFAULT - agent makes the correct override
        USER_DEFINED - user must call the override mechanism"""
    DEFAULT      = 0
    USER_DEFINED = 1

def apb_change_width(addr_width = 1, data_width = 1):
    """ Method that retuns a class definition which can be used by the UVM Factory to override the base sequence item class.
    The new class definition assures that the agent is using the correct WIDTH (from the configuration object)."""

    @vsc.randobj
    class cl_apb_seq_item_updated(cl_apb_seq_item):
        """Common base sequence item for the APB agent"""

        def __init__(self, name = "apb_item_updated"):
            super().__init__(name)

        @vsc.constraint
        def c_apb_width_parameter(self):
            """Setting the correct ADDR_WIDTH and DATA_WIDTH parameters"""
            self.addr < 2**addr_width
            self.data < 2**data_width

    return cl_apb_seq_item_updated
"""APB-UVC Configuration object"""

from pyuvm import uvm_object, uvm_active_passive_enum
from .apb_common import SequenceItemOverride

class cl_apb_config(uvm_object):
    """Configuration object for the APB agent (and its sub-components)"""

    def __init__(self, name = 'apb_config'):
        super().__init__(name)

        #############################
        # General configuration
        #############################

        # Configuration knob for controlling the interface widths, default: 1
        self.ADDR_WIDTH = 1
        self.DATA_WIDTH = 1

        # Setting agent as ACTIVE or PASSIVE
        self.is_active = uvm_active_passive_enum.UVM_ACTIVE

        # Virtual interface handle
        self.vif = None

        # Driver type
        self.driver = None

        # Number of consumer sequences, default: infinite sequences
        self.num_consumer_seq = None

        #############################
        # Coverage specific settings
        #############################

        # Control if transaction coverage is sampled, run time switch
        self.enable_transaction_coverage = True

        # Control if delay coverage is sampled, run time switch
        self.enable_delay_coverage = True

        # Control knob for monitor sequence item overriding
        self.seq_item_override = SequenceItemOverride.DEFAULT
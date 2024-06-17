"""APB Monitor
- UVM monitor is responsible for capturing signal activity from the design interface and translates it into transaction level data objects that can be sent to other components."""

from pyuvm import *
from uvc.sdt.src.cl_sdt_seq_item import *
from uvc.sdt.src.sdt_common import *

class cl_apb_monitor(uvm_monitor):
    """APB Monitor
    - Capture pin level signal activity
    - Translate it to transactions
    - Broadcasts transactions via analysis port"""

    def __init__(self, name, parent):
        super().__init__(name, parent)

        # Analysis port for broadcasting of collected transactions
        self.ap = None
        self.request_ap = None

        # Handle to the configuration object
        self.cfg = None

        # Monitor process
        self.monitor_loop_process = None

        # Clock cycle counter
        self.clk_cyc_cnt = 0

    def build_phase(self):
        self.logger.info("Start build_phase() -> APB monitor")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(self, "", "cfg")

        # Construct the analysis port
        self.ap = uvm_analysis_port("ap", self)
        self.request_ap = uvm_analysis_port("request_ap", self)

        self.logger.info("End build_phase() -> APB monitor")

    async def run_phase(self):
        self.logger.info("Start run_phase() -> APB monitor")
        await super().run_phase()

        self.logger.info("End run_phase() -> APB monitor")

        # Not implemented

from cocotb.types import Logic, LogicArray

class cl_apb_interface():
    """Python interface for APB configuration"""

    def __init__(self, clk_signal, rst_signal, name = "apb_interface"):
        self.name = name
        self.clk = clk_signal
        self.rst = rst_signal

        self.wr        = None   # 1 bit
        self.sel       = None   # 1 bit
        self.enable    = None   # 1 bit
        self.addr      = None   # 32 bit
        self.wdata     = None   # 32 bit
        self.strb      = None   # 4 bit
        self.rdata     = None   # 32 bit
        self.ready     = None   # 1 bit
        self.slverr    = None   # 1 bit


    def connect(self, wr_signal, sel_signal, enable_signal, addr_signal,
                wdata_signal, strb_signal, rdata_signal, ready_signal, slverr_signal):
        """Connecting the signals to the interface and set values to x"""
        self.wr        = wr_signal
        self.sel       = sel_signal
        self.enable    = enable_signal
        self.addr      = addr_signal
        self.wdata     = wdata_signal
        self.strb      = strb_signal
        self.rdata     = rdata_signal
        self.ready     = ready_signal
        self.slverr    = slverr_signal

        self._set_x_values()

    def _set_x_values(self):
        self.wr.value        = Logic('x')
        self.sel.value       = Logic('x')
        self.enable.value    = Logic('x')
        self.addr.value      = LogicArray('x' * 32)
        self.wdata.value     = LogicArray('x' * 32)
        self.strb.value      = LogicArray('x' * 4)
        self.rdata.value     = LogicArray('x' * 32)
        self.ready.value     = Logic('x')
        self.slverr.value    = Logic('x')

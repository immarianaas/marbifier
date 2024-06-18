from cocotb.types import Logic, LogicArray


class cl_sdt_interface():
    """Python interface for SDT UVC"""

    def __init__(self, clk_signal, rst_signal, name="sdt_if"):
        self.name = name
        self.clk = clk_signal
        self.rst = rst_signal

        self.rd = None
        self.wr = None
        self.addr = None
        self.wr_data = None
        self.rd_data = None
        self.ack = None

        self.ADDR_WIDTH = None
        self.DATA_WIDTH = None

    def connect(self, rd_signal, wr_signal, addr_signal, wr_data_signal, rd_data_signal, ack_signal):
        """Connecting the signals to the interface and set values to x"""
        self.rd = rd_signal
        self.wr = wr_signal
        self.addr = addr_signal
        self.wr_data = wr_data_signal
        self.rd_data = rd_data_signal
        self.ack = ack_signal

        # Set values to X
        self._set_x_values()

    def _set_width_values(self, ADDR_WIDTH=1, DATA_WIDTH=1):
        self.ADDR_WIDTH = ADDR_WIDTH
        self.DATA_WIDTH = DATA_WIDTH

    def _set_x_values(self):
        self.rd.value = Logic("X")
        self.wr.value = Logic("X")
        self.addr.value = LogicArray("X" * self.ADDR_WIDTH)
        self.wr_data.value = LogicArray("X" * self.DATA_WIDTH)
        self.rd_data.value = LogicArray("X" * self.DATA_WIDTH)
        self.ack.value = Logic("X")

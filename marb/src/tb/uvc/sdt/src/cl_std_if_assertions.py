
import cocotb
from cocotb.triggers import ReadOnly, RisingEdge


class cl_sdt_interface_assert_check():
    def __init__(self,
                 clk_signal=None,
                 rst_signal=None,
                 rd=None,
                 wr=None,
                 addr=None,
                 rd_data=None,
                 wr_data=None,
                 ack=None
                 ):

        self.clk = clk_signal
        self.rst = rst_signal
        self.rd = rd
        self.wr = wr
        self.addr = addr
        self.rd_data = rd_data
        self.wr_data = wr_data
        self.ack = ack

        self.DATA_WIDTH = None
        self.ADDR_WIDTH = None

        self.all_good = True

    def _set_width_values(self, DATA_WIDTH=1, ADDR_WIDTH=1):
        self.DATA_WIDTH = DATA_WIDTH
        self.ADDR_WIDTH = ADDR_WIDTH

    async def check_assertions(self):
        cocotb.start_soon(self.cannot_read_write())
        cocotb.start_soon(self.addr_not_zero())

    async def cannot_read_write(self):
        """Cannot read and write at the same time."""

        while True:
            await ReadOnly()

            try:
                assert self.rd != 1 or self.wr != 1, \
                    "Both rd and wd are 1."
            except AssertionError as msg:
                self.all_good = False
                print(msg)

            await RisingEdge(self.clk)

    async def addr_not_zero(self):
        """When rd or wr, addr != 0"""

        while True:
            await ReadOnly()

            try:
                if self.rd == 1 or self.wr == 1:
                    assert self.addr != 0, \
                        "Address is 0 when rd or wr were active."
            except AssertionError as msg:
                self.all_good = False
                print(msg)

            await RisingEdge(self.clk)

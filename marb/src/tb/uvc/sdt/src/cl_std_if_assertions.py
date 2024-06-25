
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
        cocotb.start_soon(self.addr_not_x())
        cocotb.start_soon(self.wr_data_not_x())

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

    async def addr_not_x(self):
        """When rd or wr, addr != 0"""

        while True:
            await ReadOnly()

            try:
                if self.rd == 1 or self.wr == 1:
                    assert self.addr.value.is_resolvable, \
                        "Address is either X,W,U when rd or wr were active or not an BinaryValue object."
            except AssertionError as msg:
                self.all_good = False
                print(msg)

            await RisingEdge(self.clk)

    async def wr_data_not_x(self):
        """When wr, wr_data != X"""

        while True:
            await ReadOnly()

            try:
                if self.wr == 1:
                    assert self.wr_data.value.is_resolvable, \
                        "Wr_data is X,U,Y or not a binaryValue object."
            except AssertionError as msg:
                self.all_good = False
                print(msg)

            await RisingEdge(self.clk)

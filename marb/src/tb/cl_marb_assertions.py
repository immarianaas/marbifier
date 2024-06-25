

import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

############################
# Worked on it:            #
# - Tobias                 #
############################


class cl_interface_assert_check():
    def __init__(self,
                 clk_signal=None,
                 rst_signal=None,
                 ack0_signal=None,
                 ack1_signal=None,
                 ack2_signal=None
                 ):

        self.clk = clk_signal
        self.rst = rst_signal
        self.ack0 = ack0_signal
        self.ack1 = ack1_signal
        self.ack2 = ack2_signal
        self.all_good = True

    async def check_assertions(self):
        cocotb.start_soon(self.only_one_ack())

    async def only_one_ack(self):
        """Only one ack should be high at a time."""
        while True:
            await ReadOnly()
            try:
                assert self.ack0.value + self.ack1.value + self.ack2.value <= 1, \
                    "More than one ack is high."
            except AssertionError as msg:
                self.all_good = False
                print(msg)

            await RisingEdge(self.clk)

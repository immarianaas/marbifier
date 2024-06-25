from uvc.sdt.src import *
from cl_marb_tb_base_seq import cl_marb_tb_base_seq

import cocotb
from cocotb.triggers import Combine


############################
# Worked on it:            #
# - Mariana                #
# - Tobias                 #
############################


class cl_marb_random_seq(cl_marb_tb_base_seq):
    """Setup and start Memory Arbiter with random sequence"""

    def __init__(self, name="cl_marb_dynamic_seq"):
        cl_marb_tb_base_seq.__init__(self, name)
        self.c0_seq = cl_sdt_count_seq.create("c0_seq")
        self.c1_seq = cl_sdt_count_seq.create("c1_seq")
        self.c2_seq = cl_sdt_count_seq.create("c2_seq")
        self.m_seq = cl_sdt_consumer_rsp_seq.create("m_seq")

    # our function, nothing to do with library
    def randomize(self):
        self.c0_seq.randomize()
        self.c1_seq.randomize()
        self.c2_seq.randomize()

    async def body(self):
        await super().body()

        cocotb.start_soon(
            self.m_seq.start(self.sequencer.sdt_m_sequencer))

        c0_seq_task = cocotb.start_soon(
            self.c0_seq.start(self.sequencer.sdt_c0_sequencer))
        c1_seq_task = cocotb.start_soon(
            self.c1_seq.start(self.sequencer.sdt_c1_sequencer))
        c2_seq_task = cocotb.start_soon(
            self.c2_seq.start(self.sequencer.sdt_c2_sequencer))

        await Combine(c0_seq_task, c1_seq_task, c2_seq_task)

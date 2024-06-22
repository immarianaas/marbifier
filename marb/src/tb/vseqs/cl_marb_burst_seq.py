import vsc

from uvc.sdt.src import *
from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from reg_model.seq_lib.cl_reg_setup_seq import cl_reg_setup_seq

import cocotb
from cocotb.triggers import Combine


# @vsc.randobj
class cl_marb_burst_seq(cl_marb_tb_base_seq):
    """Setup and start Memory Arbiter with static configuration"""

    def __init__(self, name="cl_marb_static_seq"):
        cl_marb_tb_base_seq.__init__(self, name)
        self.c0_seq = cl_sdt_burst_seq.create("c0_seq")
        self.c1_seq = cl_sdt_burst_seq.create("c1_seq")
        self.c2_seq = cl_sdt_burst_seq.create("c2_seq")
        self.m_seq = cl_sdt_consumer_rsp_seq.create("m_seq")

    # our function, nothing to do with library
    # is this the correct way?
    def randomize(self):
        self.c0_seq.randomize()
        self.c1_seq.randomize()
        self.c2_seq.randomize()

    async def body(self):
        await super().body()
        print("~ cl_marb_static_seq ~")

        cocotb.start_soon(
            self.m_seq.start(self.sequencer.sdt_m_sequencer))

        await self.c0_seq.start(self.sequencer.sdt_c0_sequencer)
        await self.c1_seq.start(self.sequencer.sdt_c1_sequencer)
        await self.c2_seq.start(self.sequencer.sdt_c2_sequencer)


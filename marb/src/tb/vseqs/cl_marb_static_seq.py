import vsc

from uvc.sdt.src import *
from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from reg_model.seq_lib.cl_reg_setup_seq import cl_reg_setup_seq

import cocotb
from cocotb.triggers import Combine


# @vsc.randobj
class cl_marb_static_seq(cl_marb_tb_base_seq):
    """Setup and start Memory Arbiter with static configuration"""

    def __init__(self, name="cl_reg_simple_seq"):
        cl_marb_tb_base_seq.__init__(self, name)
        self.c0_seq = cl_sdt_single_seq.create("c0_seq")
        self.c1_seq = cl_sdt_single_seq.create("c1_seq")
        self.c2_seq = cl_sdt_single_seq.create("c2_seq")
        self.m_seq = cl_sdt_consumer_rsp_seq.create("m_seq")

    async def body(self):
        await super().body()
        print("~ cl_marb_static_seq ~")

        cocotb.start_soon(
            self.m_seq.start(self.sequencer.sdt_m_sequencer))

        for _ in range(10):
            c0_seq_task = cocotb.start_soon(
                self.c0_seq.start(self.sequencer.sdt_c0_sequencer))
            c1_seq_task = cocotb.start_soon(
                self.c1_seq.start(self.sequencer.sdt_c1_sequencer))
            c2_seq_task = cocotb.start_soon(
                self.c2_seq.start(self.sequencer.sdt_c2_sequencer))

            await Combine(c0_seq_task, c1_seq_task, c2_seq_task)

        # Start sequences
        # self.sequencer.logger.debug("Starting setup seq")
        # await setup_seq.start(self.sequencer)

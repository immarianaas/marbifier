import vsc

from uvc.sdt.src import *
from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from reg_model.seq_lib.cl_reg_setup_seq import cl_reg_setup_seq

import cocotb
from cocotb.triggers import Combine
@vsc.randobj
class cl_marb_static_seq(cl_marb_tb_base_seq, object):
    """Setup and start Memory Arbiter with static configuration"""

    def __init__(self, name = "cl_reg_simple_seq"):
        cl_marb_tb_base_seq.__init__(self, name)
        object.__init__(self)
        self.c0_seq = cl_sdt_single_seq.create("c0_seq")
        self.c1_seq = cl_sdt_single_seq.create("c1_seq")
        self.c2_seq = cl_sdt_single_seq.create("c2_seq")
        self.m_seq = cl_sdt_single_seq.create("m_seq")



    async def body(self):
        await super().body()

        for _ in range(10):
            c0_seq_task = cocotb.start_soon(self.c0_seq.start(self.sequencer.sdt_c0))
            c1_seq_task = cocotb.start_soon(self.c1_seq.start(self.sequencer.sdt_c1))
            c2_seq_task = cocotb.start_soon(self.c2_seq.start(self.sequencer.sdt_c2))
            m_seq_task = cocotb.start_soon(self.m_seq.start(self.sequencer.sdt_m))
            await Combine(c0_seq_task, c1_seq_task, c2_seq_task, m_seq_task)
            
        # Setup seqs and set reg_model
        setup_seq  = cl_reg_setup_seq.create("setup_seq")

        # Start sequences
        self.sequencer.logger.debug("Starting setup seq")
        await setup_seq.start(self.sequencer)


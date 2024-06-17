from pyuvm import *

class cl_reg_base_seq(uvm_sequence):
    """Base sequence for register sequences"""

    def __init__(self, name = "cl_reg_base_seq"):
        super().__init__(name)

        self.start_mask         = 0x00000001
        self.dynamic_prio_mask  = 0x00000002

        self.cfg = None

    async def pre_body(self):
        if self.sequencer is not None:
            self.cfg = self.sequencer.cfg

    async def body(self):
        await self.pre_body()
from uvc.sdt.src import *
from cl_marb_tb_base_seq import cl_marb_tb_base_seq

class cl_marb_basic_seq(cl_marb_tb_base_seq):
    """Start 2 sequences in parallel twice for each producer sequencer"""

    def __init__(self, name = "cl_marb_basic_seq"):
        super().__init__(name)

    async def body(self):
        await super().body()


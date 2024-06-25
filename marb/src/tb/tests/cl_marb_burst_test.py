import pyuvm
from pyuvm import *

from cl_marb_tb_base_test import cl_marb_tb_base_test
from cl_marb_tb_base_seq import cl_marb_tb_base_seq
from vseqs.cl_reg_simple_seq import cl_reg_simple_seq
from vseqs.cl_marb_burst_seq import cl_marb_burst_seq
from uvc.sdt.src import *
import globalvars

############################
# Worked on it:            #
# - Mariana                #
############################

@pyuvm.test(timeout_time=100000, timeout_unit='ns')
class cl_marb_burst_test(cl_marb_tb_base_test):
    """burst test - running WR and RD bursts on each producer"""

    def __init__(self, name="cl_marb_static_test", parent=None):
        super().__init__(name, parent)

    def start_of_simulation_phase(self):
        globalvars.STATIC = True


        super().start_of_simulation_phase()
        uvm_factory().set_type_override_by_type(cl_marb_tb_base_seq, cl_marb_burst_seq)

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        # Register sequence for enabling and configuring the Memory Arbiter sequene
        conf_seq = cl_reg_simple_seq.create("conf_seq")
        conf_seq.randomize()

        # cocotb.start_soon(conf_seq.start(self.marb_tb_env.virtual_sequencer))
        await conf_seq.start(self.marb_tb_env.virtual_sequencer)

        self.top_seq = cl_marb_burst_seq.create("top_seq")
        self.top_seq.randomize()
        await self.top_seq.start(self.marb_tb_env.virtual_sequencer)

        self.drop_objection()

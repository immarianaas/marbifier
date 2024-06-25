from .cl_reg_base_seq import cl_reg_base_seq
from ..uvm_reg_model import *

############################
# Worked on it:            #
# - Mariana                #
# - Tobias                 #
############################

class cl_reg_setup_seq(cl_reg_base_seq):
    """Setup sequence for registers"""

    def __init__(self, name="cl_reg_seq_setup"):
        super().__init__(name)

    async def body(self):
        await super().body()

        ######################
        #  Setup up sequence
        ######################

        # Write the value 1 into the ctrl register
        status = await self.sequencer.reg_model.ctrl_reg.write(1)
        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {1} "
                f"to ctrl_reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

        # Read the value of the DPRIO register
        status, read_val = await self.sequencer.reg_model.dprio_reg.read()

        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: read {read_val} "
                f"from dprio, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

        # Write the value 0 into the DPRIO register
        status = await self.sequencer.reg_model.dprio_reg.write(0)
        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0} "
                f"to dprio_reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

from .cl_reg_base_seq import cl_reg_base_seq
from ..uvm_reg_model import *
import vsc

@vsc.randobj
class cl_reg_setup_dynamic_seq(cl_reg_base_seq):
    """Setup sequence for registers"""

    def __init__(self, name="cl_reg_dynamic_seq"):
        super().__init__(name)
        self.c0_priority = vsc.rand_uint8_t()
        self.c1_priority = vsc.rand_uint8_t()
        self.c2_priority = vsc.rand_uint8_t()
    @vsc.constraint
    def c_priority(self):
        self.c0_priority != 0
        self.c1_priority != 0
        self.c2_priority != 0


    async def body(self):
        await super().body()
        self.randomize()
        self.prettyCountPrint()

        ######################
        #  Setup up sequence
        ######################

        # Write the value 0 into the ctrl register
        status = await self.sequencer.reg_model.ctrl_reg.write(0x3)
        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0} "
                f"to dprio_reg, status = {status}")  # TODO change
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
        status = await self.sequencer.reg_model.dprio_reg.write(self.c2_priority << 16 | self.c1_priority << 8 | self.c0_priority)
        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0} "
                f"to dprio_reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")


    def prettyCountPrint(self):
        #split into 4 8 bit values
        print("Pretty print ENGAGE")
        string = str("C2: " + str(self.c2_priority)+"\n")
        string = string + str("C1: " + str(self.c1_priority)+"\n")
        string = string + str("C0: " + str(self.c0_priority)+"\n")

        print(string)
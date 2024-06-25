from .cl_reg_base_seq import cl_reg_base_seq
from ..uvm_reg_model import *
import globalvars
import vsc


############################
# Worked on it:            #
# - Tobias                 #
############################

@vsc.randobj
class cl_reg_setup_dynamic_seq(cl_reg_base_seq):
    """Setup sequence for registers"""

    def __init__(self, name="cl_reg_dynamic_seq"):
        super().__init__(name)
        self.c0_priority = vsc.rand_bit_t(2)
        self.c1_priority = vsc.rand_bit_t(2)
        self.c2_priority = vsc.rand_bit_t(2)
        # Configuration
        self.cfg = None

    @vsc.constraint
    def c_priority(self):

        self.c0_priority != 0
        self.c1_priority != 0
        self.c2_priority != 0
        vsc.unique(self.c0_priority, self.c1_priority, self.c2_priority)

    async def body(self):
        await super().body()
        self.randomize()
        self.prettyCountPrint()

        ######################
        #  Setup up sequence
        ######################

        # Write the value 0 into the ctrl register
        status = await self.sequencer.reg_model.ctrl_reg.write(0x00000002)
        # Set the STATIC variable from the file cl_marb_ref_model.py to False
        globalvars.STATIC = False

        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0} "
                f"to ctrl reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

        # Read the value of the DPRIO register
        status, read_val = await self.sequencer.reg_model.dprio_reg.read()

        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: read {read_val} "
                f"from dprio reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

        # Write the value 0 into the DPRIO register
        test = 00000000 << 24 | self.c2_priority << 16 | self.c1_priority << 8 | self.c0_priority
        status = await self.sequencer.reg_model.dprio_reg.write(test)
        globalvars.ORDER = (
            self.c0_priority, self.c1_priority, self.c2_priority)
        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0} "
                f"to dprio_reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

        # Write the value 0 into the ctrl register
        status = await self.sequencer.reg_model.ctrl_reg.write(0x00000003)
        # Set the STATIC variable from the file cl_marb_ref_model.py to False
        globalvars.STATIC = False

        # Check the status received
        if status == uvm_status_e.UVM_IS_OK:
            self.sequencer.logger.info(
                f"SETUP SEQ: written {0x3} "
                f"to ctrl_reg, status = {status}")
        else:
            self.sequencer.logger.error("STATUS is NOT_OK")

    def prettyCountPrint(self):
        # split into 4 8 bit values
        string = str("C2: " + str(self.c2_priority)+"\n")
        string = string + str("C1: " + str(self.c1_priority)+"\n")
        string = string + str("C0: " + str(self.c0_priority)+"\n")

        print(string)

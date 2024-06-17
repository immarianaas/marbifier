import pyuvm
from pyuvm import *

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer
from cocotb.queue import Queue

import warnings
from random import randint
import vsc

from uvc.sdt.src import *

from cl_marb_tb_config import cl_marb_tb_config
from uvc.apb.src.cl_apb_interface import cl_apb_interface
from cl_marb_tb_env import cl_marb_tb_env
from uvc.sdt.src.sdt_common import DriverType
from uvc.sdt.src.sdt_common import SequenceItemOverride

from reg_model.seq_lib.cl_reg_setup_seq import cl_reg_setup_seq

@pyuvm.test()
class cl_marb_tb_base_test(uvm_test):
    def __init__(self, name = "cl_marb_tb_base_test", parent = None):
        super().__init__(name, parent)

        # Access the DUT through the cocotb.top handler
        self.dut = cocotb.top


        # APB configuration interface
        self.apb_if = None

        # Configuration object handler
        self.cfg = None

        # TB environment handler
        self.marb_tb_env = None

        uvm_report_object.set_default_logging_level("INFO")

        # Quick fix because of warnings og PYVSC
        warnings.simplefilter("ignore")

    def build_phase(self):
        self.logger.info("Start build_phase() -> MARB base test")
        super().build_phase()

        # Create configuration object
        self.cfg = cl_marb_tb_config("cfg")


        # APB agent configuration
        self.cfg.apb_cfg.driver                      = DriverType.PRODUCER
        self.cfg.apb_cfg.create_default_coverage     = False
        self.cfg.apb_cfg.seq_item_override           = SequenceItemOverride.USER_DEFINED


        self.apb_if       = cl_apb_interface(self.dut.clk, self.dut.rst)

        # Set interfaces in cfg
        self.cfg.apb_cfg.vif           = self.apb_if

        # Instantiate environment
        ConfigDB().set(self, "marb_tb_env", "cfg", self.cfg)
        self.marb_tb_env = cl_marb_tb_env("marb_tb_env", self)


        self.logger.info("End build_phase() -> MARB base test")

    def connect_phase(self):
        self.logger.info("Start connect_phase() -> MARB base test")
        super().connect_phase()


        self.apb_if.connect(wr_signal      = self.dut.conf_wr,
                           sel_signal      = self.dut.conf_sel,
                           enable_signal   = self.dut.conf_enable,
                           addr_signal     = self.dut.conf_addr,
                           wdata_signal    = self.dut.conf_wdata,
                           strb_signal     = self.dut.conf_strb,
                           rdata_signal    = self.dut.conf_rdata,
                           ready_signal    = self.dut.conf_ready,
                           slverr_signal   = self.dut.conf_slverr)

        self.logger.info("End connect_phase() -> MARB base test")

    async def run_phase(self):
        self.logger.info("Start run_phase() -> MARB base test")
        await super().run_phase()

        await self.trigger_reset()

        # Instantiate register sequences for enabling and configuring the Memory Arbiter

        self.logger.info("End run_phase() -> MARB base test")


    async def trigger_reset(self):
        """Activation and deactivation of reset """

        # Start a clock of randomizd clock period [1, 5] ns
        self.clk_period = randint(1, 5)
        cocotb.start_soon(Clock(self.dut.clk, self.clk_period, 'ns').start())

        # Wait randomized number of clock cyles in [0, 5]
        await ClockCycles(self.dut.clk, randint(0, 5))

        # Activate reset
        self.logger.info("Waiting for reset")
        self.dut.rst.value = 1

        # Wait randomized number of clock cycles before deactivating reset
        await ClockCycles(self.dut.clk, randint(1, 20))
        self.dut.rst.value = 0

        self.logger.info("Reset Done")

    def end_of_elaboration_phase(self):
        super().end_of_elaboration_phase()

    def report_phase(self):
        self.logger.info("Start report_phase() -> MARB base test")
        super().report_phase()

        # Creating coverage report with PyVSC in txt format
        try:
            test_number = cocotb.plusargs["test_number"]
        except:
            test_number = 0

        # Writing coverage report in txt-format
        f = open(f'sim_build/{self.get_type_name()}_{test_number}_cov.txt', "w")
        f.write(f"Coverage report for {self.get_type_name()} #{test_number} \n")
        f.write("------------------------------------------------\n \n")
        vsc.report_coverage(fp=f, details=True)
        f.close()

        # Writing coverage report in xml-format
        vsc.write_coverage_db(
            f'sim_build/{self.get_type_name()}_{test_number}_cov.xml')

        self.logger.info("End report_phase() -> MARB base test")

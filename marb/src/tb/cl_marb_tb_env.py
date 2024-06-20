from pyuvm import *

from uvc.sdt.src import *

from cl_marb_tb_virtual_sequencer import cl_marb_tb_virtual_sequencer

from reg_model.cl_reg_block import cl_reg_block
from reg_model.cl_reg_adapter import cl_reg_adapter

from uvc.apb.src.cl_apb_driver import cl_apb_driver
from uvc.apb.src.cl_apb_agent import cl_apb_agent
from uvc.apb.src.cl_apb_monitor import cl_apb_monitor
from cl_marb_scb import cl_marb_scoreboard
from cl_marb_ref_model import marb_ref_model


class cl_marb_tb_env(uvm_env):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # Configuration object handle
        self.cfg = None

        # Virtual sequencer
        self.virtual_sequencer = None

        self.reg_model = None
        self.adapter = None

        self.sdt_agent_c0 = None
        self.sdt_agent_c1 = None
        self.sdt_agent_c2 = None
        self.sdt_agent_m = None
        self.apb_agent = None

        self.ref_model_handler = None
        self.scoreboard = None

    def build_phase(self):
        self.logger.info("Start build_phase() -> MARB env")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(self, "", "cfg")

        # Create virtual_sequencer and pass handler to cfg
        ConfigDB().set(self, "virtual_sequencer", "cfg", self.cfg)
        self.virtual_sequencer = cl_marb_tb_virtual_sequencer.create(
            "virtual_sequencer", self)

        # Instantiate the SDT UVC and pass handler to cfg
        # ConfigDB().set(self, "", "cfg", self.cfg.sdt_cfg_prod)
        # ConfigDB().set(self, "", "cfg", self.cfg.sdt_cfg_cons)

        self.sdt_agent_c0 = cl_sdt_agent.create("sdt_agent_c0", self)
        self.sdt_agent_c0.cdb_set("cfg", self.cfg.sdt_cfg_c0, "")
        

        self.sdt_agent_c1 = cl_sdt_agent.create("sdt_agent_c1", self)
        self.sdt_agent_c1.cdb_set("cfg", self.cfg.sdt_cfg_c1, "")

        self.sdt_agent_c2 = cl_sdt_agent.create("sdt_agent_c2", self)
        self.sdt_agent_c2.cdb_set("cfg", self.cfg.sdt_cfg_c2, "")

        self.sdt_agent_m = cl_sdt_agent.create("sdt_agent_m", self)
        self.sdt_agent_m.cdb_set("cfg", self.cfg.sdt_cfg_m, "")

        # Instantiate the APB UVC and pass handler to cfg
        ConfigDB().set(self, "apb_agent", "cfg", self.cfg.apb_cfg)
        self.apb_agent = cl_apb_agent("apb_agent", self)

        self.reg_model = cl_reg_block()
        self.adapter = cl_reg_adapter()

        # Build register model
        self.reg_model.build()

        # Set register model in virtual sequencer
        self.virtual_sequencer.reg_model = self.reg_model

        self.ref_model_handler = marb_ref_model.create(
            "cl_ref_model_handler", self)
        self.ref_model_handler.DATA_WIDTH = self.cfg.DATA_WIDTH
        self.ref_model_handler.DATA_WIDTH = self.cfg.DATA_WIDTH

        self.scoreboard = cl_marb_scoreboard.create(
            name="cl_marb_scoreboard", parent=self)
        self.scoreboard.cdb_set("cfg", self.cfg, "")

        self.logger.info("End build_phase() -> MARB env")

    def connect_phase(self):
        self.logger.info("Start connect_phase() -> MARB env")
        super().connect_phase()

        # Connect the virtual sequencer to the agents
        self.virtual_sequencer.sdt_c0_sequencer = self.sdt_agent_c0.sequencer
        self.virtual_sequencer.sdt_c1_sequencer = self.sdt_agent_c1.sequencer
        self.virtual_sequencer.sdt_c2_sequencer = self.sdt_agent_c2.sequencer
        self.virtual_sequencer.sdt_m_sequencer = self.sdt_agent_m.sequencer

        # Connect the agents analysis port to the scoreboard
        # TODO: the agents have `request_ap` and also `ap`
        #       I'm unsure which one I should usseeee
        self.sdt_agent_m.ap.connect(
            self.scoreboard.uvc_sdt_m_consumer_fifo.analysis_export)

        self.ref_model_handler.analysis_port.connect(
            self.scoreboard.ref_model_fifo.analysis_export)

        # TODO: the agents have `request_ap` and also `ap`
        #       I'm unsure which one I should usseeee

        # Connect agent's request analysis port to the reference model
        self.sdt_agent_c0.ap.connect(
            self.ref_model_handler.uvc_sdt_c0_fifo.analysis_export)
        self.sdt_agent_c1.ap.connect(
            self.ref_model_handler.uvc_sdt_c1_fifo.analysis_export)
        self.sdt_agent_c2.ap.connect(
            self.ref_model_handler.uvc_sdt_c2_fifo.analysis_export)

        # Connect reg_model and APB sequencer
        self.reg_model.bus_map.set_sequencer(
            self.apb_agent.sequencer, self.adapter)
        self.logger.info("End connect_phase() -> MARB env")

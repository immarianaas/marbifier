from pyuvm import *

from uvc.sdt.src.cl_sdt_config import *
from uvc.apb.src.cl_apb_config import *


class cl_marb_tb_config(uvm_object):
    def __init__(self, name="cl_marb_tb_config"):
        super().__init__(name)

        self.apb_cfg = cl_apb_config.create("apb_cfg")

        self.sdt_cfg_c0 = cl_sdt_config.create("sdt_cfg_c0")
        self.sdt_cfg_c1 = cl_sdt_config.create("sdt_cfg_c1")
        self.sdt_cfg_c2 = cl_sdt_config.create("sdt_cfg_c2")
        self.sdt_cfg_m = cl_sdt_config.create("sdt_cfg_m")

        self.ADDR_WDITH = None
        self.DATA_WIDTH = None

    def build_phase(self):
        self.sdt_cfg_c0.DATA_WIDTH = self.DATA_WIDTH
        self.sdt_cfg_c0.DATA_WIDTH = self.DATA_WIDTH

        self.sdt_cfg_c1.DATA_WIDTH = self.DATA_WIDTH
        self.sdt_cfg_c1.DATA_WIDTH = self.DATA_WIDTH

        self.sdt_cfg_c2.DATA_WIDTH = self.DATA_WIDTH
        self.sdt_cfg_c2.DATA_WIDTH = self.DATA_WIDTH

        self.sdt_cfg_m.DATA_WIDTH = self.DATA_WIDTH
        self.sdt_cfg_m.DATA_WIDTH = self.DATA_WIDTH

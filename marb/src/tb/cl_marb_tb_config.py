from pyuvm import *

from uvc.sdt.src.cl_sdt_config import *
from uvc.apb.src.cl_apb_config import *

class cl_marb_tb_config(uvm_object):
    def __init__(self, name = "cl_marb_tb_config"):
        super().__init__(name)

        self.apb_cfg           = cl_apb_config.create("apb_cfg")
        self.sdt_cfg_prod      = cl_sdt_config.create("sdt_cfg_prod")
        self.sdt_cfg_cons      = cl_sdt_config.create("sdt_cfg_cons")

        self.addr_width = None
        self.data_width = None
    def build_phase(self):
        self.sdt_cfg_prod.DATA_WIDTH = self.data_width
        self.sdt_cfg_prod.ADDR_WIDTH = self.addr_width
        self.sdt_cfg_cons.DATA_WIDTH = self.data_width
        self.sdt_cfg_cons.ADDR_WIDTH = self.addr_width
        

from pyuvm import uvm_driver
from cocotb.triggers import FallingEdge, RisingEdge, ReadOnly

from .sdt_common import DriverType, AccessType


class cl_std_driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # config obj
        self.cfg = None

        # virtual interface
        self.vif = None

        self.rsp = None

    def build_phase(self):
        super().build_phase()

        # create instance of config
        self.cfg = self.cdb_get("cfg", "")

        # virtual interface obtained from cfg
        self.vif = self.cfg.vif

    async def run_phase(self):
        await super().run_phase()

    async def drive_transaction(self):
        if self.cfg.driver_type is DriverType.PRODUCER:
            await self.producer_loop()
        elif self.cfg.driver_type is DriverType.CONSUMER:
            await self.consumer_loop()
        else:
            assert False, "Unknown type of handler"

    async def producer_loop(self):
        req = await self.seq_item_port.get_next_item()

        # handle response object
        self.rsp = req.clone()
        self.rsp.set_context(req)
        self.rsp.set_id_info(req)

        self.vif.addr.value = req.addr
        if req.access == AccessType.WR:
            self.vif.wr_data.value = self.req.data
            self.vif.wr.value = 1
        else:
            self.vif.rd = 1

        await FallingEdge(self.vif.ack)
        self.reset_bus_producer()
        self.seq_item_port.item_done(self.rsp)

    def reset_bus_producer(self):
        self.vif.addr.value = 0
        self.vif.rd.value = 0
        self.vif.wr.value = 0
        self.vif.wr_data.value = 0

    async def consumer_loop(self):
        while True:
            await RisingEdge(self.ack)
            await ReadOnly()

            if self.vid.rd.value == 1:
                self.rsp.data = self.vid.rd_data
                self.rsp.addr = self.vid.addr
                self.rsp.access = AccessType.RD

            elif self.vid.wr.value == 1:
                self.rsp.data = self.vid.wr_data
                self.rsp.addr = self.vid.addr
                self.rsp.access = AccessType.WR

            else:
                assert False, "Invalid consumer SDT transaction"

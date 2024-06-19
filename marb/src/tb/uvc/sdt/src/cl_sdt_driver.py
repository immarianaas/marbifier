from pyuvm import uvm_driver
from cocotb.triggers import FallingEdge, RisingEdge, ReadOnly, ReadWrite, ClockCycles

from .sdt_common import DriverType, AccessType


class cl_sdt_driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # config obj
        self.cfg = None

        # virtual interface
        self.vif = None

        self.rsp = None

        self.req = None

    def build_phase(self):
        super().build_phase()

        # create instance of config
        self.cfg = self.cdb_get("cfg", "")

        # virtual interface obtained from cfg
        self.vif = self.cfg.vif

    async def run_phase(self):
        await super().run_phase()

        while True:
            item = await self.seq_item_port.get_next_item()
            self.req = item.clone()
            self.rsp = self.req
            self.rsp.set_context(self.req)
            self.rsp.set_id_info(self.req)

            await self.drive_transaction()

            self.seq_item_port.item_done()
            self.seq_item_port.put_response(self.rsp)

    async def drive_transaction(self):
        if self.cfg.driver is DriverType.PRODUCER:
            await self.producer_loop()
        elif self.cfg.driver is DriverType.CONSUMER:
            await self.consumer_loop()
        else:
            assert False, "Unknown type of handler in sdt driver"

    async def producer_loop(self):
        # handle response object

        # but first, reset pins
        self.reset_bus_producer()
        print(f"[producer loop] begin; name = {self.get_name()}")
        await ReadWrite()
        await RisingEdge(self.vif.clk)
        self.vif.addr.value = self.req.addr

        if self.req.access == AccessType.WR:
            self.vif.wr_data.value = self.req.data
            self.vif.wr.value = 1
            self.vif.rd.value = 0
        else:
            self.vif.wr.value = 0
            self.vif.rd.value = 1

        await FallingEdge(self.vif.ack)
        print("[producer loop] after ack goes down")

        self.reset_bus_producer()
        # self.seq_item_port.item_done(self.rsp)
        # self.seq_item_port.put_response(self.rsp)

    def reset_bus_producer(self):
        self.vif.addr.value = 0
        self.vif.rd.value = 0
        self.vif.wr.value = 0
        self.vif.wr_data.value = 0

    async def consumer_loop(self):
        # handle response object
        self.reset_bus_consumer()

        await ReadOnly()
        while (self.vif.rd.value == 0 and self.vif.wr.value == 0):
            await ReadOnly()
            await RisingEdge(self.vif.clk)

        await ReadWrite()
        if self.vif.rd.value == 1:
            self.rsp.addr = self.vif.addr
            self.rsp.access = AccessType.RD

        elif self.vif.wr.value == 1:
            self.rsp.data = self.vif.wr_data
            self.rsp.addr = self.vif.addr
            self.rsp.access = AccessType.WR

        self.vif.rd_data.value = 42
        self.vif.ack.value = 1
        await ClockCycles(self.vif.clk, 1)

    def reset_bus_consumer(self):
        self.vif.ack.value = 0
        self.vif.rd_data.value = 0

from pyuvm import uvm_driver
from cocotb.triggers import FallingEdge, RisingEdge, ReadOnly, ReadWrite

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
        
        self.req = await self.seq_item_port.get_next_item()
        self.rsp = self.req.clone()
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
        #req = await self.seq_item_port.get_next_item()

        # handle response object

        self.vif.addr.value = self.req.addr

        print("\n11.\n")

        await RisingEdge(self.vif.clk)
        if self.req.access == AccessType.WR:
            self.vif.wr_data.value = self.req.data
            self.vif.wr.value = 1
            self.vif.rd.value = 0
        else:
            self.vif.wr.value = 0
            self.vif.rd.value = 1

        print("\n22.\n")

        await FallingEdge(self.vif.ack)
        print("\n33.\n")

        self.reset_bus_producer()
        # self.seq_item_port.item_done(self.rsp)
        # self.seq_item_port.put_response(self.rsp)

    def reset_bus_producer(self):
        self.vif.addr.value = 0
        self.vif.rd.value = 0
        self.vif.wr.value = 0
        self.vif.wr_data.value = 0

    async def consumer_loop(self):
        #req = await self.seq_item_port.get_next_item()

        # handle response object

        while True:
            self.vif.ack.value = 0
            await RisingEdge(self.vif.clk)
            await ReadWrite()

            if self.vif.rd.value == 1:
                self.rsp.addr = self.vif.addr
                self.rsp.access = AccessType.RD

            elif self.vif.wr.value == 1:
                self.rsp.data = self.vif.wr_data
                self.rsp.addr = self.vif.addr
                self.rsp.access = AccessType.WR
            else:
                continue

            await RisingEdge(self.vif.clk)
            await ReadWrite()

            self.vif.ack.value = 1
            self.vif.rd_data.value = 42
            break

            # self.seq_item_port.item_done(self.rsp)
            # self.seq_item_port.put_response(self.rsp)

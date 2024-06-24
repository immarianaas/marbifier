from pyuvm import uvm_driver
from cocotb.triggers import FallingEdge, RisingEdge, ReadOnly, ReadWrite, ClockCycles, Edge, Event, Timer

import cocotb
from .sdt_common import DriverType, AccessType
from pyuvm import UVMSequenceError, UVMFatalError
from cocotb.types import LogicArray


class cl_sdt_driver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # config obj
        self.cfg = None

        # virtual interface
        self.vif = None

        self.rsp = None

        self.req = None

        self.ev_last_clock = None
        self.get_and_drive_process = None

    def build_phase(self):
        super().build_phase()

        # create instance of config
        self.cfg = self.cdb_get("cfg", "")

        # virtual interface obtained from cfg
        self.vif = self.cfg.vif

    async def run_phase(self):
        await super().run_phase()

        # Starts coroutines in parallel
        cocotb.start_soon(self.clock_event())
        cocotb.start_soon(self.drive_transaction())
        cocotb.start_soon(self.handle_reset())

    async def clock_event(self):
        self.ev_last_clock = Event()
        while True:
            await RisingEdge(self.cfg.vif.clk)
            self.ev_last_clock.set()

            # Waits until next time step , default unit is step
            await Timer(1)
            self.ev_last_clock.clear()

    async def handle_reset(self):
        """ Kills driver process when reset is active"""
        while True:
            if self.cfg.vif.rst.value.binstr == '1':
                if self.get_and_drive_process is not None:
                    self.logger.debug("Process should be killed")
                    self.get_and_drive_process.kill()
                    self.get_and_drive_process = None
                    # Ends any active items
                    try:
                        self.seq_item_port.item_done()
                    except UVMSequenceError:
                        self.logger.info("No current active item")
            await RisingEdge(self.cfg.vif.clk)

    async def get_and_drive_transaction(self):
        # Start driver as master or slave
        if self.cfg.driver is DriverType.PRODUCER:
            await self.prod_loop()
        elif self.cfg.driver is DriverType.CONSUMER:
            await self.cons_loop()
        else:
            raise UVMFatalError(
                f"DRIVER, not handled driver {self.get_full_name()}")

    async def drive_reset(self):
        # Reset interface values according to type
        if self.cfg.driver is DriverType.PRODUCER:
            self.vif.wr.value = 0
            self.vif.rd.value = 0
            self.vif.wr_data.value = LogicArray("X" * 8)
            self.vif.addr.value = LogicArray("X" * 8)  # TODO: change

        if self.cfg.driver is DriverType.CONSUMER:
            self.vif.ack.value = 0
            self.vif.rd_data.value = LogicArray("X" * 8)

    async def drive_transaction(self):
        while True:
            await self.drive_reset()

            # This is a workaround to wait for the machine to be ready
            # This is only needed for the dynamic test
            #for _ in range(50):
            #    await RisingEdge(self.cfg.vif.clk)

            while self.cfg.vif.rst.value.binstr != '0':
                await RisingEdge(self.cfg.vif.clk)

            # Passes coroutine to process handle -> possible to kill() process
            self.get_and_drive_process = cocotb.start_soon(
                self.get_and_drive_transaction())
            # Waits for process to finish
            await self.get_and_drive_process

    async def prod_loop(self):
        while True:
            self.logger.debug("SDT-Producer driver waiting for next seq_item")

            # Waits for seq item
            self.req = await self.seq_item_port.get_next_item()
            self.logger.debug(f"SDT-Producer driver item: {self.req}")

            # Creates clone of seq item
            self.rsp = self.req.clone()
            self.rsp.set_id_info(self.req)
            self.rsp.set_context(self.req)

            self.logger.debug("Driving producer pins")
            await self.prod_drive_pins()
            self.seq_item_port.item_done(self.rsp)

    async def cons_loop(self):
        while True:
            self.logger.debug("SDT-Consumer driver waiting for next seq_item")

            # Waits for seq item
            self.req = await self.seq_item_port.get_next_item()
            self.logger.debug(f"SDT-Consumer driver item: {self.req}")

            # Creates clone of seq item
            self.rsp = self.req.clone()
            self.rsp.set_id_info(self.req)
            self.rsp.set_context(self.req)

            self.logger.debug("Driving producer pins")
            await self.cons_drive_pins()
            self.seq_item_port.item_done(self.rsp)

    async def prod_drive_pins(self):
        # If unaligned to clock wait for clocking event
        await RisingEdge(self.cfg.vif.clk)

        # common for both
        self.vif.addr.value = self.req.addr

        # Drive transactions through interface
        if self.req.access == AccessType.WR:
            self.vif.wr.value = 1
            self.vif.rd.value = 0
            self.vif.wr_data.value = self.req.data

        elif self.req.access == AccessType.RD:
            self.cfg.vif.wr.value = 0
            self.cfg.vif.rd.value = 1
        else:
            self.logger.critical(
                f"Access type not wr or rd: access = {self.req.access}")

        # wait for ACK to go up now
        await RisingEdge(self.cfg.vif.clk)

        while self.vif.ack.value != 1:
            await RisingEdge(self.cfg.vif.clk)

        # # Capture slave response
        # if self.req.access == AccessType.RD:
        #     self.req.data = self.cfg.vif.rdata.value.integer
        #     self.rsp.data = self.cfg.vif.rdata.value.integer

        # # Return to idle
        # await RisingEdge(self.cfg.vif.clk)
        # self.cfg.vif.enable.value = 0
        # self.cfg.vif.sel.value = 0

        self.vif.rd.value = 0
        self.vif.wr.value = 0

        self.logger.debug(f"prod: REQ object: {self.req}")
        self.logger.debug(f"prod: RSP object: {self.rsp}")

    async def cons_drive_pins(self):
        # If unaligned to clock wait for clocking event
        await RisingEdge(self.vif.clk)

        while (self.vif.rd.value == 0 and self.vif.wr.value == 0):
            await RisingEdge(self.vif.clk)

        # common case
        self.rsp.addr = self.vif.addr.value.integer

        if self.vif.rd.value == 1:
            self.rsp.access = AccessType.RD

        elif self.vif.wr.value == 1:
            self.rsp.access = AccessType.WR
            self.rsp.data = self.vif.wr_data.value.integer
        else:
            self.logger.critical(
                f"Access type not wr or rd: access = {self.req.access}")

        await RisingEdge(self.vif.clk)
        self.vif.rd_data.value = 42  # TODO: change?
        self.vif.ack.value = 1
        await RisingEdge(self.vif.clk)

        # Reset
        self.vif.addr.value = 0
        self.vif.rd.value = 0
        self.vif.wr.value = 0
        self.vif.wr_data.value = 0
        self.vif.ack.value = 0

        # self.logger.info(f"cons: REQ object: {self.req}")
        self.logger.debug(f"cons: RSP object: {self.rsp}")

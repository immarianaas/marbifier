"""APB Driver
- The UVM Driver is an active entity that converts abstract transaction to design pin toggles.
- Transaction level objects are obtained from the Sequencer and the UVM Driver drives them to the design via an interface handler."""

from cocotb.triggers import RisingEdge, Event, Timer
from cocotb.types import LogicArray
from pyuvm import *
from uvc.sdt.src.sdt_common import *

class cl_apb_driver(uvm_driver):
    """ Signal interface driver for APB
    - translates transactions to pin level activity
    - transactions pulled from sequencer by the seq_item_port"""

    def __init__(self, name, parent):
        super().__init__(name, parent)

        # Handle to the configuration object
        self.cfg = None

        # Process
        self.get_and_drive_process = None

        self.ev_last_clock = None

    def build_phase(self):
        self.logger.info("Start build_phase() -> APB driver")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(self, "", "cfg")

        self.logger.info("End build_phase() -> APB driver")

    async def run_phase(self):
        """Run phase:
        * Receives the sequence item.
        * For each sequence item it calls the clock_event, drive_transaction and
        handle_reset tasks in parallel in a fork join_none."""

        self.logger.info("Start run_phase() -> APB driver")
        await super().run_phase()

        # Starts coroutines in parallel
        cocotb.start_soon(self.clock_event())
        cocotb.start_soon(self.drive_transaction())
        cocotb.start_soon(self.handle_reset())

        self.logger.info("End run_phase() -> APB driver")

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

    async def drive_transaction(self):
        while True:
            await self.drive_reset()

            while self.cfg.vif.rst.value.binstr != '0':
                await RisingEdge(self.cfg.vif.clk)

            # Passes coroutine to process handle -> possible to kill() process
            self.get_and_drive_process = cocotb.start_soon(self.get_and_drive_transaction())
            # Waits for process to finish
            await self.get_and_drive_process

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
            self.cfg.vif.wr.value     = 0
            self.cfg.vif.sel.value    = 0
            self.cfg.vif.enable.value = 0
            self.cfg.vif.addr.value   = LogicArray("X" * 32)
            self.cfg.vif.wdata.value  = LogicArray("X" * 32)
            self.cfg.vif.strb.value   = 0

    async def prod_loop(self):
        while True:
            self.logger.debug("APB-Producer driver waiting for next seq_item")

            # Waits for seq item
            self.req = await self.seq_item_port.get_next_item()
            self.logger.debug(f"APB-Producer driver item: {self.req}")

            # Creates clone of seq item
            self.rsp = self.req.clone()
            self.rsp.set_id_info(self.req)
            self.rsp.set_context(self.req)

            self.logger.debug("Driving producer pins")
            await self.prod_drive_pins()
            self.seq_item_port.item_done(self.rsp)

    async def prod_drive_pins(self):
        # If unaligned to clock wait for clocking event
        await RisingEdge(self.cfg.vif.clk)

        # Drive transactions through interface
        if self.req.access == AccessType.WR:
            self.cfg.vif.wr.value = 1
            self.cfg.vif.sel.value = 1
            self.cfg.vif.enable.value = 0
            self.cfg.vif.addr.value = self.req.addr
            self.cfg.vif.wdata.value = self.req.data
            self.cfg.vif.strb.value = LogicArray('1' * 4)

        elif self.req.access == AccessType.RD:
            self.cfg.vif.wr.value = 0
            self.cfg.vif.sel.value = 1
            self.cfg.vif.enable.value = 0
            self.cfg.vif.addr.value = self.req.addr
            self.cfg.vif.strb.value = 0

            self.cfg.vif.wdata.value = LogicArray('X' * 32)
        else:
            self.logger.critical(
                f"Access type not wr or rd: access = {self.req.access}")

        await RisingEdge(self.cfg.vif.clk)
        self.cfg.vif.enable.value = 1

        while self.cfg.vif.ready.value != 1:
            await RisingEdge(self.cfg.vif.clk)

        # Capture slave response
        if self.req.access == AccessType.RD:
            self.req.data = self.cfg.vif.rdata.value.integer
            self.rsp.data = self.cfg.vif.rdata.value.integer

        # Return to idle
        await RisingEdge(self.cfg.vif.clk)
        self.cfg.vif.enable.value = 0
        self.cfg.vif.sel.value = 0

        self.logger.debug(f"REQ object: {self.req}")
        self.logger.debug(f"RSP object: {self.rsp}")

    async def cons_loop(self):
        # Not implemented
        ...
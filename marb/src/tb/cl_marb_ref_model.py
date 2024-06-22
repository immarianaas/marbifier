
from pyuvm import uvm_component, uvm_tlm_analysis_fifo, uvm_analysis_port
import time
from cocotb.queue import Queue
import cocotb

from ref_model.seq_item import SeqItem, SeqItemOut

from cocotb.triggers import NextTimeStep, Timer, ClockCycles, RisingEdge, FallingEdge
import globalvars


# Reference model for the marb design
class marb_ref_model(uvm_component):

    def __init__(self, name="marb_ref_model", parent=None):
        super().__init__(name, parent)
        self.analysis_port = None
        self.uvc_sdt_c0_fifo = None
        self.uvc_sdt_c1_fifo = None
        self.uvc_sdt_c2_fifo = None
        self.uvc_sdt_m_fifo = None
        self.uvc_apb_fifo = None

        self.items = None  # list of 3 queues

        self.DATA_WIDTH = 1  # i dont know
        self.ADDR_WIDTH = 1

    def build_phase(self):
        super().build_phase()

        self.uvc_sdt_c0_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c0_fifo", self)
        self.uvc_sdt_c1_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c1_fifo", self)
        self.uvc_sdt_c2_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c2_fifo", self)
        self.uvc_sdt_m_fifo = uvm_tlm_analysis_fifo("uvc_sdt_m_fifo", self)
        self.uvc_apb_fifo = uvm_tlm_analysis_fifo(
            "uvc_apb_fifo", self)  # TODO: what to do with this?

        self.analysis_port = uvm_analysis_port(
            f"{self.get_name()}_analysis_port", self)

        self.items = [Queue(maxsize=-1), Queue(maxsize=-1), Queue(maxsize=-1)]

    async def run_phase(self):

        await super().run_phase()
        cocotb.start_soon(self.static_fifos2queue())
        cocotb.start_soon(self.sample_item())

    async def sample_item(self):

        while True:
            if self.all_queues_empty():
                await ClockCycles(cocotb.top.clk, 1)
                continue

            assert globalvars.STATIC is not None
            item_to_handle = await self.get_item_to_handle()
            if item_to_handle is None:
                continue

            output_item = item_to_handle.clone()
            output_item.data = output_item.data if output_item.access == 1 else 42

            self.analysis_port.write(output_item)

            await FallingEdge(cocotb.top.m_ack)
            await RisingEdge(cocotb.top.clk)

    async def get_item_to_handle(self):

        highest, middle, lowest = (
            0, 1, 2) if globalvars.STATIC else self.get_order_dynamic()

        # self.logger.warning(f"order= ({highest}, {middle}, {lowest})")

        if not self.items[highest].empty():
            return await self.items[highest].get()

        if not self.items[middle].empty():
            return await self.items[middle].get()

        if not self.items[lowest].empty():
            return await self.items[lowest].get()

    def get_order_dynamic(self):
        assert globalvars.ORDER is not None

        max_index = globalvars.ORDER.index(max(globalvars.ORDER))
        min_index = globalvars.ORDER.index(min(globalvars.ORDER))
        middle_val = sum(globalvars.ORDER) - \
            globalvars.ORDER[max_index] - globalvars.ORDER[min_index]
        middle_index = globalvars.ORDER.index(middle_val)

        return max_index, middle_index, min_index

    def all_queues_empty(self) -> bool:
        return self.items[0].empty() and self.items[1].empty(
        ) and self.items[2].empty()

    async def static_fifos2queue(self):
        async def add_item_to_queue(fifo, queue):
            while True:
                fifo_item = await fifo.get()
                await queue.put(fifo_item)

        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c0_fifo, self.items[0]))
        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c1_fifo, self.items[1]))
        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c2_fifo, self.items[2]))

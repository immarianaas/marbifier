
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

        self.items = None

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
        print("\n[sample_item]\n")

        if not globalvars.STATIC:
            return await self.sample_item_dynamic()

        while True:
            if self.all_queues_empty():
                await ClockCycles(cocotb.top.clk, 1)

                # await RisingEdge(cocotb.top.clk)
                continue
            #  -  await RisingEdge(cocotb.top.clk)

            # while self.all_queues_empty():
            #     await ClockCycles(cocotb.top.clk, 1)
            # await RisingEdge(cocotb.top.clk)

            item_to_handle = self.get_item_to_handle_no_wait()
            if item_to_handle is None:
                continue

            print(f"\nitem_to:handle {item_to_handle}\n")

            output_item = item_to_handle.clone()
            output_item.data = output_item.data if output_item.access == 1 else 42

            self.analysis_port.write(output_item)

            await FallingEdge(cocotb.top.m_ack)
            await RisingEdge(cocotb.top.clk)



    async def sample_item_dynamic(self):
        print("\n[sample_item_dynamic]\n")

        while True:
            await ClockCycles(cocotb.top.clk, 1)

            if globalvars.ORDER is None:
                continue

            item_to_handle = await self.get_item_to_handle_dynamic()
            if item_to_handle is None:
                continue

            print("\nitem_to:handle\n")

            output_item = item_to_handle.clone()
            output_item.data = output_item.data if output_item.access == 1 else 42

            self.analysis_port.write(output_item)

    async def get_item_to_handle_dynamic(self):
        print("\n[get_item_to_handle_dynamic]\n")

        highest, middle, lowest = self.get_order()
        print(f"highest={highest}, middle={middle}, lowest={lowest}")
        if not self.items[lowest].empty():
            return await self.items[lowest].get()

        if not self.items[middle].empty():
            return await self.items[middle].get()

        if not self.items[highest].empty():
            return await self.items[highest].get()

    def get_order(self):
        print("\n[get_item_to_handle_dynamic]")
        print(
            f"c1={globalvars.ORDER[0]}, c2={globalvars.ORDER[1]}, c3={globalvars.ORDER[2]} ")

        max_index = globalvars.ORDER.index(max(globalvars.ORDER)) 
        min_index  = globalvars.ORDER.index(min(globalvars.ORDER)) 
        middle_val = sum(globalvars.ORDER) - globalvars.ORDER[max_index] - globalvars.ORDER[min_index]
        middle_index = globalvars.ORDER.index(middle_val)
     
        return max_index, middle_index, min_index     

        return highest, middle, lowest

    async def get_item_to_handle(self):
        """
        if (self.items[0].qsize() != 0 or self.items[1].qsize() != 0 or self.items[2].qsize() != 0):
            print(f"----- start -----")

            print(f"self.items[0].qsize()? {self.items[0].qsize()}")
            print(f"self.items[1].qsize()? {self.items[1].qsize()}")
            print(f"self.items[2].qsize()? {self.items[2].qsize()}")

            print(f"----- end -----")
        """
        if not self.items[0].empty():
            return await self.items[0].get()

        if not self.items[1].empty():
            return await self.items[1].get()

        if not self.items[2].empty():
            return await self.items[2].get()

        return None

    def get_item_to_handle_no_wait(self):
        if not self.all_queues_empty():

            self.logger.warning("----- start -----")

            self.logger.warning(
                f"self.items[0].qsize()? {self.items[0].qsize()}")
            self.logger.warning(
                f"self.items[1].qsize()? {self.items[1].qsize()}")
            self.logger.warning(
                f"self.items[2].qsize()? {self.items[2].qsize()}")

            self.logger.warning(f"----- end -----")
        if not self.items[0].empty():
            return self.items[0].get_nowait()

        if not self.items[1].empty():
            return self.items[1].get_nowait()

        if not self.items[2].empty():
            return self.items[2].get_nowait()

        return None

    def all_queues_empty(self) -> bool:
        res = self.items[0].empty() and self.items[1].empty(
        ) and self.items[2].empty()
        # print(res)
        return res

    async def static_fifos2queue(self):
        async def add_item_to_queue(fifo, queue):
            while True:
                fifo_item = await fifo.get()
                """
                seq_item = SeqItem(DATA_WIDTH=self.DATA_WIDTH,
                                   ADDR_WIDTH=self.ADDR_WIDTH)

                seq_item.set_data(rd=0 if fifo_item.access == 1 else 1,
                                  wr=fifo_item.access,
                                  addr=fifo_item.addr,
                                  wr_data=fifo_item.data)

                await self.items.put(seq_item.clone())
                """
                await queue.put(fifo_item)

        # not quite correct, it is quite correct ;D
        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c0_fifo, self.items[0]))
        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c1_fifo, self.items[1]))
        cocotb.start_soon(add_item_to_queue(
            self.uvc_sdt_c2_fifo, self.items[2]))

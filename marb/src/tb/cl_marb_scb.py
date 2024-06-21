from pyuvm import uvm_scoreboard, uvm_analysis_port, uvm_tlm_analysis_fifo
import cocotb
from cocotb.queue import Queue


class cl_marb_scoreboard(uvm_scoreboard):
    """ Scoreboard for MARB. """

    def __init__(self, name="cl_marb_scoreboard", parent=None):
        super().__init__(name, parent)

        self.cfg = None
        self.analysis_port = None

        self.uvc_sdt_m_consumer_fifo = None
        self.ref_model_fifo = None

        self.uvc_sdt_m_consumer_queue = None
        self.ref_model_queue = None

        self.successes = 0
        self.failures = 0

    def build_phase(self):
        super().build_phase()

        self.cfg = self.cdb_get("cfg", "")

        self.analysis_port = uvm_analysis_port(
            f"{self.get_name()}_analysis_port", self)

        self.uvc_sdt_m_consumer_fifo = uvm_tlm_analysis_fifo(
            "uvc_sdt_m_consumer_fifo", self)
        self.ref_model_fifo = uvm_tlm_analysis_fifo("ref_model_fifo", self)

        self.uvc_sdt_m_consumer_queue = Queue(maxsize=1)
        self.ref_model_queue = Queue(maxsize=1)

    async def run_phase(self):
        """
        - Get the item from the FIFOs
        - Compare the samples received
        """

        await super().run_phase()

        cocotb.start_soon(self.fifo2queue(
            self.uvc_sdt_m_consumer_fifo, self.uvc_sdt_m_consumer_queue))
        cocotb.start_soon(self.fifo2queue(
            self.ref_model_fifo, self.ref_model_queue))

        while True:
            uvc_val = await self.uvc_sdt_m_consumer_queue.get()
            ref_val = await self.ref_model_queue.get()

            if uvc_val == ref_val:
                self.successes += 1
                self.logger.warning(f"Correct! Reference= {ref_val}")
            else:
                self.failures += 1
                self.logger.error(
                    "Reference and obtained values are different!")
                self.logger.error(
                    f"Reference= {ref_val}")
                self.logger.error(
                    f"Obtained= {uvc_val}")

    async def fifo2queue(self, fifo, queue):
        while True:
            await queue.put(await fifo.get())

    def check_phase(self):
        super().check_phase()
        self.logger.info("*"*40)
        self.logger.info(f'**{"SUCCESSES":>16s} |{"FAILURES":>17s} **')
        self.logger.info(f'**{self.successes:>16d} |{self.failures:>17d} **')
        self.logger.info("*"*40)
        # self.logger.info(
        #     f"Successes: {self.successes} | Failures: {self.failures}")

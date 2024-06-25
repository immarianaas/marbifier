import cocotb
from cocotb.triggers import RisingEdge
from pyuvm import uvm_subscriber
import vsc


@vsc.covergroup
class covergroup_parallel_requests(object):
    def __init__(self, name) -> None:
        self.options.per_instance = True
        self.options.name = name

        self.with_sample(number=vsc.uint32_t())

        self.parallel_point = vsc.coverpoint(self.number,
                                             bins={
                                                 "one": vsc.bin(1),
                                                 "two": vsc.bin(2),
                                                 "three": vsc.bin(3)
                                             })


class cl_marb_req_coverage(uvm_subscriber):

    def __init__(self, name, parent):

        super().__init__(name, parent)
        self.cfg = None
        self.parallel_input = None

        self.number_items = 0

    def build_phase(self):
        super().build_phase()

        self.cfg = self.cdb_get("cfg", "")

        self.parallel_input = covergroup_parallel_requests(
            name=f"{self.get_name()}.cvg_parallel_input"
        )

        cocotb.start_soon(self.sample_items())

    def write(self, _):
        self.number_items += 1

    async def sample_items(self):

        while True:
            await RisingEdge(cocotb.top.clk)

            # internal check that it works as it should
            assert self.number_items <= 3

            self.parallel_input.sample(self.number_items)
            self.number_items = 0

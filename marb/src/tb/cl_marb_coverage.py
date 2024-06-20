from pyuvm import uvm_subscriber
import vsc

# Covergroup class


@vsc.covergroup
class covergroup_memory(object):
    def __init__(self, name, data_width, addr_width) -> None:
        self.DATA_WIDTH = 8  # data_width
        self.ADDR_WIDTH = 8  # addr_width

        self.options.per_instance = True
        self.options.name = name

        self.with_sample(rd=vsc.bit_t(1),
                         wr=vsc.bit_t(1),
                         addr=vsc.bit_t(self.ADDR_WIDTH))

        self.rd_point = vsc.coverpoint(self.rd,
                                       bins={
                                           "rd": vsc.bin_array([], 0, 1)
                                       })

        self.wr_point = vsc.coverpoint(self.wr,
                                       bins={
                                           "wr": vsc.bin_array([], 0, 1)
                                       })

        self.addr_point = vsc.coverpoint(self.addr,
                                         bins={
                                             "zero": vsc.bin_array([], 0),
                                             # TODO: check the actual size
                                             "valid": vsc.bin_array([4], 1, 2**self.ADDR_WIDTH-1)
                                         })


@vsc.covergroup
class covergroup_read_followed_by_write(object):
    def __init__(self, name) -> None:
        self.options.per_instance = True
        self.options.name = name

        self.with_sample(result=vsc.bool_t())

        self.result_point = vsc.coverpoint(self.result,
                                           bins={
                                               "result": vsc.bin_array([], True, False)
                                           })


class cl_marb_coverage(uvm_subscriber):

    def __init__(self, name, parent):

        super().__init__(name, parent)
        self.cfg = None
        self.covergroup = None

        self.past_read_addr = None

    def build_phase(self):
        super().build_phase()

        self.cfg = self.cdb_get("cfg", "")
        self.covergroup = covergroup_memory(name=f"{self.get_name()}.cvg",  # TODO: FIXME
                                            data_width=8,  # self.cfg.DATA_WIDTH,
                                            addr_width=8)  # self.cfg.ADDR_WIDTH)

        self.read_followed_by_write = covergroup_read_followed_by_write(
            name=f"{self.get_name()}.cvg_read_followed_by_write")

    def write(self, rd: int, wr: int, addr: int):
        self.covergroup.sample(rd, wr, addr)

        if wr == 1:
            if self.past_read_addr is not None and self.past_read_addr == addr:
                self.read_followed_by_write.sample(True)  # True
            else:
                self.read_followed_by_write.sample(False)  # False
                self.past_read_addr = None

        elif rd == 1:
            if self.past_read_addr is not None:
                self.read_followed_by_write.sample(False)  # False
            self.past_read_addr = addr


# QUESTIONS:
# 2. Must be connected to the monitor of the MIF;
#   . connected to the *monitor*? did I do this correctly?
# 3. read followed by a write to the same address
#   . we get some False, is this correct?
# 4. what is a burst?
# 5. "Note that as the address grows the lengths decrease", how so?
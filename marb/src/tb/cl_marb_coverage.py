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
                                             "zero": vsc.bin(0),
                                             # TODO: check the actual size
                                             "valid1": vsc.bin([1, (2**self.ADDR_WIDTH)/2]),
                                             "valid2": vsc.bin([(2**self.ADDR_WIDTH)/2 + 1, (2**self.ADDR_WIDTH)-1])
                                         })


@vsc.covergroup
class covergroup_write_followed_by_read(object):
    def __init__(self, name, addr_width) -> None:
        self.options.per_instance = True
        self.options.name = name

        self.with_sample(result=vsc.bool_t(), addr=vsc.bit_t(addr_width))

        self.result_point = vsc.coverpoint(self.result,
                                           bins={
                                               "yes": vsc.bin(True),
                                               "no": vsc.bin(False)
                                           })

        self.addr_point = vsc.coverpoint(self.addr,
                                         bins={
                                             "zero": vsc.bin(0),
                                             # TODO: check the actual size
                                             "valid1": vsc.bin([1, (2**addr_width)/2]),
                                             "valid2": vsc.bin([(2**addr_width)/2 + 1, (2**addr_width)-1])
                                         })

        self.result_addr_cross = vsc.cross(
            [self.result_point, self.addr_point])


@vsc.covergroup
class covergroup_burst(object):
    def __init__(self, name, addr_width) -> None:
        self.options.per_instance = True
        self.options.name = name

        self.with_sample(length=vsc.uint32_t(), addr=vsc.bit_t(addr_width))

        self.length_point = vsc.coverpoint(self.length,
                                           bins={
                                               "zero": vsc.bin(0),
                                               "one": vsc.bin(1),
                                               "b1": vsc.bin_array([4], [2, addr_width**2-1])
                                           })

        self.addr_point = vsc.coverpoint(self.addr,
                                         bins={
                                             "zero": vsc.bin(0),
                                             # TODO: check the actual size
                                             "valid1": vsc.bin([1, (2**addr_width)/2]),
                                             "valid2": vsc.bin([(2**addr_width)/2 + 1, (2**addr_width)-1])
                                         })

        self.len_addr_cross = vsc.cross(
            [self.length_point, self.addr_point])


class cl_marb_coverage(uvm_subscriber):

    def __init__(self, name, parent):

        super().__init__(name, parent)
        self.cfg = None
        self.covergroup = None

        self.past_addrs = []

        # (read, addr)
        self.past_operation = None
        self.burst_count = 0
        self.starting_addr = None

    def build_phase(self):
        super().build_phase()

        self.cfg = self.cdb_get("cfg", "")
        self.covergroup = covergroup_memory(name=f"{self.get_name()}.cvg",  # TODO: FIXME
                                            data_width=8,  # self.cfg.DATA_WIDTH,
                                            addr_width=8)  # self.cfg.ADDR_WIDTH)

        self.read_followed_by_write = covergroup_write_followed_by_read(
            name=f"{self.get_name()}.cvg_read_followed_by_write",
            addr_width=8
        )

        self.rd_burst = covergroup_burst(
            name=f"{self.get_name()}.cvg_read_burst",
            addr_width=8
        )

        self.wr_burst = covergroup_burst(
            name=f"{self.get_name()}.cvg_write_burst",
            addr_width=8
        )

    def write(self, item):
        print(item)
        rd = 0 if item.access == 1 else 1
        wr = item.access
        addr = item.addr

        self.covergroup.sample(rd, wr, addr)
        self.handle_read_followed_by_write(rd, wr, addr)
        self.handle_bursts(rd, wr, addr)

    def handle_read_followed_by_write(self, rd, wr, addr):

        # 1. receive a write (save the addr)
        # 2. if a read to the same addr - positive
        # 3. if a read to the diff addr - negative
        # 4. we can have write followed by write  (nested stuff)
        #

        assert wr != 1 or rd != 1

        if wr == 1:
            self.past_addrs.append(addr)

        if rd == 1:
            if addr in self.past_addrs:
                self.read_followed_by_write.sample(True, addr)
                self.past_addrs.remove(addr)  # only deletes the first
            else:
                self.read_followed_by_write.sample(False, addr)

    def handle_bursts(self, rd, wr, addr):
        # burst is when read or write consecutive addresses
        # but always the same kind of operation

        def reset_counters():
            self.past_operation = (rd, addr)
            self.burst_count = 1
            self.starting_addr = addr


        if self.past_operation is None:
            reset_counters()

        rd_past_op = self.past_operation[0]
        addr_past_op = self.past_operation[1]

        if rd_past_op != rd or addr != (addr_past_op + self.burst_count):
            # self.burst.sample(self.burst_count, self.starting_addr)
            reset_counters()
        else:
            # continuing the burst!
            self.burst_count += 1


        if rd_past_op:  # if it was a READ
            self.rd_burst.sample(
                self.burst_count, addr_past_op)  # length, addr
        else:  # if it was a WRITE
            self.wr_burst.sample(
                self.burst_count, addr_past_op)  # length, addr

        # self.past_operation = (rd, addr)

    # def write(self, rd: int, wr: int, addr: int):
    #     self.covergroup.sample(rd, wr, addr)


# QUESTIONS:
# 2. Must be connected to the monitor of the MIF;
#   . connected to the *monitor*? did I do this correctly?
# 3. read followed by a write to the same address
#   . we get some False, is this correct?
# 4. what is a burst?
# 5. "Note that as the address grows the lengths decrease", how so?

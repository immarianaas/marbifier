from pyuvm import uvm_subscriber
import vsc

# Covergroup class


@vsc.covergroup
class covergroup_memory(object):
    def __init__(self, name, data_width, addr_width) -> None:
        self.DATA_WIDTH = data_width
        self.ADDR_WIDTH = addr_width

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
                                             "valid": vsc.bin_array([4], [1, addr_width**2-1])
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
                                             "valid": vsc.bin_array([4], [1, addr_width**2-1])
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
                                               "one": vsc.bin(1),
                                               "one_plus": vsc.bin_array([4], [2, addr_width**2-1])
                                           })

        self.addr_point = vsc.coverpoint(self.addr,
                                         bins={
                                             "valid": vsc.bin_array([4], [1, addr_width**2-1])
                                         })

        self.len_addr_cross = vsc.cross(
            [self.length_point, self.addr_point]
        )


class cl_marb_coverage(uvm_subscriber):

    def __init__(self, name, parent):

        super().__init__(name, parent)
        self.cfg = None
        self.covergroup = None

        self.past_addrs = []

        # (read, addr)
        self.past_operation = None
        self.past_read = None
        self.burst_count = 0
        self.starting_addr = None
        self.read_followed_by_write = None
        self.write_followed_by_read = None
        self.queue = None

    def build_phase(self):
        super().build_phase()

        self.cfg = self.cdb_get("cfg", "")

        self.covergroup = covergroup_memory(name=f"{self.get_name()}.cvg_general",
                                            data_width=self.cfg.DATA_WIDTH,
                                            addr_width=self.cfg.ADDR_WIDTH)

        self.read_followed_by_write = covergroup_write_followed_by_read(
            name=f"{self.get_name()}.cvg_read_followed_by_write",
            addr_width=8
        )
        self.write_followed_by_read = covergroup_write_followed_by_read(
            name=f"{self.get_name()}.cvg_write_followed_by_read",
            addr_width=8
        )

        self.rd_burst = covergroup_burst(
            name=f"{self.get_name()}.cvg_read_burst",
            addr_width=self.cfg.ADDR_WIDTH
        )

        self.wr_burst = covergroup_burst(
            name=f"{self.get_name()}.cvg_write_burst",
            addr_width=self.cfg.ADDR_WIDTH
        )

    def write(self, item):
        print(item)
        rd = 0 if item.access == 1 else 1
        wr = item.access
        addr = item.addr

        self.covergroup.sample(rd, wr, addr)
        self.handle_read_followed_by_write(rd, wr, addr)
        self.handle_write_followed_by_read(rd, wr, addr)
        self.handle_bursts(rd, wr, addr)

    def handle_write_followed_by_read(self, rd, wr, addr):
        # 1. receive a write (save the addr)
        # 2. if a read to the same addr - positive
        # 3. if a read to the diff addr - negative
        # 4. we can have write followed by write  (nested stuff)
        #

        assert wr != 1 or rd != 1
        
        def reset_counters():
            self.past_read = addr
            self.starting_addr = addr


        if self.past_read is None:
            reset_counters()
        
        if rd:  # if it was a READ
            if addr==self.past_read:
                self.write_followed_by_read.sample(True, self.past_read)
            else:
                self.write_followed_by_read.sample(False, self.past_read)
        else:  # if it was a WRITE
            self.past_read = addr


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
        assert rd != wr

        def reset_counters():
            self.past_operation = (rd, addr)
            self.burst_count = 1
            self.sample_burst(rd, self.burst_count, addr)

        if self.past_operation is None:
            return reset_counters()

        rd_past_op, addr_past_op = self.past_operation

        if rd_past_op != rd or addr != (addr_past_op + self.burst_count):
            return reset_counters()

        # continuing the burst!
        self.burst_count += 1

        self.sample_burst(rd_past_op, self.burst_count, addr_past_op)

    def sample_burst(self, is_rd, count, initial_addr):
        if is_rd:  # if it was a READ
            self.rd_burst.sample(
                count, initial_addr)  # length, addr
        else:  # if it was a WRITE
            self.wr_burst.sample(
                count, initial_addr)  # length, addr

# QUESTIONS:
# 5. "Note that as the address grows the lengths decrease", how so?

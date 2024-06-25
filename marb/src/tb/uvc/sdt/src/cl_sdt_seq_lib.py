""" SDT-UVC sequence library	
- The UVM Sequence is composed of several sequence items which can be put together in different ways to generate various scenarios.
- They are executed by an assigned sequencer which then sends data items to the driver. Hence, sequences make up the core stimuli of any verification plan."""

from pyuvm import uvm_sequence
import vsc
from random import randint
from cocotb.triggers import Timer

from .cl_sdt_seq_item import *
from .sdt_common import *

############################
# Worked on it:            #
# - Mariana                #
# - Tobias                 #
############################


@vsc.randobj
class cl_sdt_base_seq(uvm_sequence, object):
    """ Base sequence for the SDT agent

    body method should be overwritten in new classes to define sequence."""

    def __init__(self, name="sdt_base_seq"):
        uvm_sequence.__init__(self, name)
        object.__init__(self)

        # Sequence item
        self.s_item = vsc.rand_attr(cl_sdt_seq_item.create(name + ".sdt_item"))

        # Delay before transaction
        self.delay_before_transaction = vsc.rand_uint32_t()

    @vsc.constraint
    def c_delay_before_transaction(self):
        self.delay_before_transaction in vsc.rangelist(vsc.rng(0, 15))

    async def body(self):
        if self.delay_before_transaction != 0:
            await Timer(self.delay_before_transaction * 1, 'ns')


class cl_sdt_single_seq(cl_sdt_base_seq):
    """Sequence generating one random item"""

    def __init__(self, name="sdt_single_seq"):
        super().__init__(name)

    async def body(self):
        if self.sequencer.cfg.driver == DriverType.PRODUCER:
            await super().body()

        await self.start_item(self.s_item)

        self.sequencer.logger.debug(self.s_item)

        # Send transaction to driver
        await self.finish_item(self.s_item)


class cl_sdt_single_zd_seq(cl_sdt_single_seq):
    """Sequence generating one random zero delay item"""

    def __init__(self, name="sdt_single_zd_seq"):
        super().__init__(name)

    @vsc.constraint
    def c_delay_before(self):
        self.delay_before_transaction == 0

    @vsc.constraint
    def c_zero_delay(self):
        self.s_item.no_producer_consumer_delays == 1


class cl_sdt_consumer_rsp_seq(cl_sdt_base_seq):
    """Sequence generating consumer response items"""

    def __init__(self, name="sdt_consumer_rsp_seq"):
        super().__init__(name)

    async def body(self):
        # Define the body of consumer_rsp_seq from num_consumer_seq
        if self.sequencer.cfg.num_consumer_seq == None:
            while True:
                # Create transaction
                seq_item_name = self.sequencer.get_full_name() + ".consumer_rsp_item"
                self.s_item = cl_sdt_seq_item.create(seq_item_name)

                await self.start_item(self.s_item)

                # Randomize transaction
                self.s_item.randomize()

                self.sequencer.logger.debug(f"Sending item: {self.s_item}")

                # Send transaction to driver
                await self.finish_item(self.s_item)

        elif self.sequencer.cfg.num_consumer_seq == 0:
            pass

        elif self.sequencer.cfg.num_consumer_seq > 0:
            for _ in range(self.sequencer.cfg.num_consumer_seq):
                # Create transaction
                seq_item_name = self.sequencer.get_full_name() + ".consumer_rsp_item"
                self.s_item = cl_sdt_seq_item.create(seq_item_name)

                await self.start_item(self.s_item)

                # Randomize transaction
                self.s_item.randomize()

                self.sequencer.logger.debug(f"Sending item: {self.s_item}")

                # Send transaction to driver
                await self.finish_item(self.s_item)
        else:
            self.sequencer.logger.critical(
                f"Num of sequences must be None or >=0, was {self.sequencer.cfg.num_consumer_seq}")


@vsc.randobj
class cl_sdt_count_seq(cl_sdt_base_seq):
    """Sequence generating <count> random item"""

    def __init__(self, name="sdt_count_seq"):
        super().__init__(name)
        self.count = vsc.rand_uint32_t()

    @vsc.constraint
    def c_count(self):
        self.count in vsc.rangelist(vsc.rng(0, 100))

    async def body(self):
        for _ in range(self.count):
            if self.sequencer.cfg.driver == DriverType.PRODUCER:
                await super().body()

            # Create transaction
            seq_item_name = self.sequencer.get_full_name() + ".sdt_count_seq_item"
            self.s_item = cl_sdt_seq_item.create(seq_item_name)
            self.s_item.randomize()

            await self.start_item(self.s_item)

            self.sequencer.logger.debug(f"Sending item: {self.s_item}")

            # Send transaction to driver
            await self.finish_item(self.s_item)


@vsc.randobj
class cl_sdt_burst_seq(cl_sdt_base_seq):
    """Sequence generating <count> item in a burst of <count_length> elements"""

    def __init__(self, name="sdt_burst_seq"):
        super().__init__(name)
        self.max_burst_length = vsc.rand_uint32_t()
        self.count = vsc.rand_uint32_t()

    @vsc.constraint
    def c_count(self):
        self.count in vsc.rangelist(vsc.rng(0, 5))
        self.max_burst_length in vsc.rangelist(vsc.rng(0, 256))

    async def body(self):
        # Create transaction

        for _ in range(self.count):
            seq_item_name = self.sequencer.get_full_name() + ".sdt_count_seq_item"
            self.s_item = cl_sdt_seq_item.create(seq_item_name)
            self.s_item.randomize()

            for _ in range(self.max_burst_length):

                if self.s_item.addr + 1 >= 2**self.sequencer.cfg.ADDR_WIDTH:
                    break

                if self.sequencer.cfg.driver == DriverType.PRODUCER:
                    await super().body()

                self.s_item.addr += 1
                await self.start_item(self.s_item)

                self.sequencer.logger.debug(f"Sending item: {self.s_item}")

                # Send transaction to driver
                await self.finish_item(self.s_item)


@vsc.randobj
class cl_sdt_write_read_seq(cl_sdt_base_seq):
    """Sequence generating <count> items such that after a write there's always a read for the same address"""

    def __init__(self, name="sdt_burst_seq"):
        super().__init__(name)
        self.count = vsc.rand_uint32_t()

    @vsc.constraint
    def c_count(self):
        self.count in vsc.rangelist(vsc.rng(0, 100))

    async def body(self):
        # Create transaction
        write_addresses = set()

        # 1. send random values, save the addr to the writes
        for _ in range(self.count):
            seq_item_name = self.sequencer.get_full_name() + ".sdt_count_seq_item"
            self.s_item = cl_sdt_seq_item.create(seq_item_name)
            self.s_item.randomize()

            # if is a write, save the addr
            if self.s_item.access == 1:
                write_addresses.add(self.s_item.addr)

            # if it's a read and not in the list, skip
            elif self.s_item.addr not in write_addresses:
                continue

            # if is a read and on the list, remove value from list
            else:
                write_addresses.remove(self.s_item.addr)

            if self.sequencer.cfg.driver == DriverType.PRODUCER:
                await super().body()

            await self.start_item(self.s_item)

            self.sequencer.logger.debug(f"Sending item: {self.s_item}")

            # Send transaction to driver
            await self.finish_item(self.s_item)

        # 2. send the reads for the write addresses
        for addr in write_addresses:
            self.s_item = cl_sdt_seq_item.create(seq_item_name)
            self.s_item.randomize()
            self.s_item.access = 0  # read
            self.s_item.addr = addr

            if self.sequencer.cfg.driver == DriverType.PRODUCER:
                await super().body()

            await self.start_item(self.s_item)

            self.sequencer.logger.debug(f"Sending item: {self.s_item}")

            # Send transaction to driver
            await self.finish_item(self.s_item)

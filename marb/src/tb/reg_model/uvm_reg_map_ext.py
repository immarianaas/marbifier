from pyuvm import *
from .uvm_reg_model import *

class uvm_reg_map_ext(uvm_reg_map):
    def __init__(self, name="uvm_reg_map"):
        super().__init__(name)

        self._parent_map = None

        # only valid info if top-level map
        self._auto_predict = False
        self._sequencer = None
        self._adapter = None

    def get_root_map(self):
        """Return top-level map"""
        if self._parent_map is None:
            return self
        else:
            return self._parent_map.get_root_map()

    def set_sequencer(self, sequencer, adapter):
        """Set the sequencer and adapter associated with map"""
        if sequencer is None:
            print("ERROR")

        if adapter is None:
            print("ERROR")

        self._sequencer = sequencer
        self._adapter = adapter

    def get_adapter(self):
        return self._adapter

    def get_sequencer(self):
        return self._sequencer

    def get_auto_predict(self):
        return self._auto_predict

    async def do_write(self, rw):
        """Perform a write operation"""

        system_map = self.get_root_map()
        adapter = system_map.get_adapter()
        sequencer = system_map.get_sequencer()

        # transfer sequence
        rw.set_parent_sequence(adapter.parent_sequence)

        await self.do_bus_write(rw, sequencer, adapter)

    async def do_read(self, rw):
        """Perform a read operation"""
        system_map = self.get_root_map()
        adapter = system_map.get_adapter()
        sequencer = system_map.get_sequencer()

        # transfer sequence
        rw.set_parent_sequence(adapter.parent_sequence)

        await self.do_bus_read(rw, sequencer, adapter)

    async def do_bus_write(self, rw, sequencer, adapter):
        """Perform a bus write operation"""

        await self.do_bus_access(rw, sequencer, adapter)

    async def do_bus_read(self, rw, sequencer, adapter):
        """Perform a bus read operation"""
        await self.do_bus_access(rw, sequencer, adapter)

    async def do_bus_access(self, rw, sequencer, adapter):
        """Perform bus accesses defined by ~rw~ on the sequencer ~sequencer~
        utilizing the adapter ~adapter~"""

        system_map = self.get_root_map()

        sequencer.logger.debug(f"do bus access for item: {rw}")
        reg = rw.get_element()

        addr = self.get_physical_addr(reg)

        # convert to <uvm_reg_bus_op>
        rw_access = uvm_reg_bus_op()
        rw_access.kind = rw.get_kind()
        rw_access.addr = addr
        rw_access.data = rw.get_value()
        rw_access.n_bits = reg.get_n_bits()

        # perform bus operations ~rw_access~
        await self.perform_accesses(rw_access, rw, adapter, sequencer)

    async def perform_accesses(self, rw_access, rw, adapter, sequencer):
        """Perform bus operations ~access~ generated from ~rw~ via adapter ~adapter~ on sequencer ~sequencer~"""

        # convert item to bus-specific item
        adapter.set_item(rw)
        bus_req = adapter.reg2bus(rw_access)
        adapter.set_item(None)

        if bus_req is None:
            raise UVMFatalError(
                f"Adapter {adapter.get_name()}: "
                f"didn't return a bus transacation")

        # define sequence for access
        rw_parent_seq = rw.get_parent_sequence()
        rw_parent_seq.sequencer = sequencer

        sequencer.logger.debug(f"Starting item on sequencer: {bus_req}")
        await rw_parent_seq.start_item(bus_req)
        await rw_parent_seq.finish_item(bus_req)

        # get response and convert back to <uvm_bus_reg_op>
        bus_rsp = await rw_parent_seq.get_response()
        adapter.bus2reg(bus_rsp, rw_access)

        # transfer data members to reg item ~rw~
        rw.set_status(rw_access.status)
        rw.set_value(rw_access.data)

    def get_physical_addr(self, reg):
        """get address for ~reg~ through map"""

        if self._parent_map is not None:
            print("cannot handle map hierarchy")
        else:
            addr = self._base_addr
            for r in self.get_registers():
                if r is reg:
                    return addr
                else:
                    addr += round(r.get_n_bits()/8)
            # if register not in map return -1
            return -1

    def __str__(self) -> str:
        out = f"Register Map: {self.get_name()}, "
        out += f"base_addr = {self.get_base_addr()} \n"
        for r in self.get_registers():
            out += f"\t {r} \n"

        return out
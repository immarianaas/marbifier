
from pyuvm import uvm_component, uvm_tlm_analysis_fifo, uvm_analysis_port
import time
import queue
from ref_model import SeqItem, SeqItemOut

#Reference model for the marb design
class marb_ref_model(uvm_component):

    def __init__(self, name="marb_ref_model", parent=None):
        super().__init__(name, parent)
        self.analysis_port = None
        self.uvc_sdt_c0_fifo = None
        self.uvc_sdt_c1_fifo = None
        self.uvc_sdt_c2_fifo = None
        self.uvc_sdt_m_fifo = None
        self.uvc_apb_fifo = None

        self.is_static = True
        self.order = (0,0,0)
        self.DATA_WIDTH = 1 # i dont know
        self.ADDR_WIDTH = 1

    def build_phase(self):
        super().build_phase()

        self.uvc_sdt_c0_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c0_fifo", self)
        self.uvc_sdt_c1_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c1_fifo", self)
        self.uvc_sdt_c2_fifo = uvm_tlm_analysis_fifo("uvc_sdt_c2_fifo", self)
        self.uvc_sdt_m_fifo = uvm_tlm_analysis_fifo("uvc_sdt_m_fifo", self)
        self.uvc_apb_fifo = uvm_tlm_analysis_fifo("uvc_apb_fifo", self) # TODO: what to do with this?
        self.analysis_port = uvm_analysis_port(f"{self.get_name()}_analysis_port", self)

    async def run_phase(self):
        await super().run_phase()
    
    


    async def sample_item(self):
        if not self.is_static: return

        items = queue.Queue(maxsize=-1)
        seq_item = SeqItem(DATA_WIDTH=self.DATA_WIDTH, ADDR_WIDTH= self.ADDR_WIDTH)

        def add_item_to_queue(fifo_item):
            seq_item.set_data(rd=0 if fifo_item.access == 1 else 1,
                              wr=fifo_item.access,
                              addr=fifo_item.addr,
                              wr_data=fifo_item.data )
            items.put( seq_item.clone() )

        while items.empty():
            # get first message that appears
            # simulate clock?
            time.sleep(0.5)
            if not self.uvc_sdt_c0_fifo.is_empty():
                fifo_item = await self.uvc_sdt_c0_fifo.get() # cl_sdt_seq_item
                add_item_to_queue(fifo_item.clone())

            if not self.uvc_sdt_c1_fifo.is_empty():
                fifo_item = await self.uvc_sdt_c1_fifo.get() 
                add_item_to_queue(fifo_item.clone())

            if not self.uvc_sdt_c2_fifo.is_empty():
                fifo_item = await self.uvc_sdt_c2_fifo.get()
                add_item_to_queue(fifo_item.clone())

            
        # the one that wins is going to be on top of the queue
        item_to_handle = items.get()

        output_item = SeqItemOut(DATA_WIDTH=self.DATA_WIDTH, ADDR_WIDTH= self.ADDR_WIDTH)
        output_item.set_data(base=item_to_handle, rd_data=1, ack=0) #read data we dont know ?

        self.analysis_port.write(output_item)


    
        
            

        

        


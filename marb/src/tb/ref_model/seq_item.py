class SeqItem():
    def __init__(self, DATA_WIDTH, ADDR_WIDTH ):
        self.rd = 0
        self.wr = 0
        self.addr = 0
        self.wr_data = 0

        self.DATA_WIDTH = DATA_WIDTH
        self.ADDR_WIDTH = ADDR_WIDTH
        
    def set_data(self,rd,wr,addr,wr_data):
        self.rd = rd
        self.wr = wr
        self.addr = addr
        self.wr_data = wr_data
        
    def __str__(self):
        return f"rd={self.rd}, wr={self.wr}, addr={self.addr}, wr_data={self.wr_data}, ADDR_WIDTH={self.ADDR_WIDTH}, DATA_WIDTH={self.DATA_WIDTH}"



class SeqItemOut(SeqItem):
    def __init__(self, DATA_WIDTH, ADDR_WIDTH):
        super().__init__(DATA_WIDTH, ADDR_WIDTH)
        
        self.rd_data = None
        self.ack = 0

    def set_data(self, base: SeqItem, rd_data, ack):
        super().set_data(base.rd, base.wr, base.addr, base.wr_data)
        self.rd_data = rd_data
        self.ack = ack

    def __str__(self):
        return f"rd_data={self.rd_data}, ack={self.ack}, ADDR_WIDTH={self.ADDR_WIDTH}, DATA_WIDTH={self.DATA_WIDTH}"
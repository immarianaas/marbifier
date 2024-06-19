class SimpleSeqItemAPB():
    """ 
    When the enable field is set to 0
    the module will operate without any arbitration. When the enable field is set to 1 the module
    will operate with the arbitration defned in the Mode field.
    The Mode field can be set to 0, to
    operate with the static prioritization, or set to 1, to operate with the dynamic prioritization
    defined in the DPrio register. The DPrio register contains a single field, named priority,
    where is defined the order of the CIFs by id.
    """
    def __init__(self):

        self.enable = 0 
        self.mode = 0
        self.DPRIO = 0
        
    def set_data(self, enable, mode, DPRIO):
        self.enable = enable
        self.mode = mode
        self.DPRIO = DPRIO

        
# Python module for register interface testing with cocotb
# TODO: Make it like the AXI module of cocotb, which only takes the name of the port, and extracts the pins


class RegisterInterface:
    def __init__(self, dut, valid, ready, addr, write, wdata, wstrb, rdata, error):
        self.dut   = dut
        self.valid = valid
        self.ready = ready
        self.addr  = addr
        self.write = write
        self.wdata = wdata
        self.wstrb = wstrb
        self.rdata = rdata
        self.error = error

    async def _read(self, addr):
        # Drive values at the Falling edge, to synchronize the rising edge read
        await FallingEdge(self.dut.clk) 
        self.valid.value = 1
        self.addr.value  = addr

        # Garantee we read the value at the rising edge
        await RisingEdge(self.dut.clk) 
        # Clocked wait until the ready signal is 1
        while self.ready.value != 1:
            await RisingEdge(self.dut.clk)

        return self.rdata.value
        
    async def _write(self, addr, data, strb):
        # Drive values at the Falling edge, to synchronize the rising edge write
        await FallingEdge(self.dut.clk)
        self.addr.value  = addr
        self.wdata.value = data
        self.wstrb.value = strb

        self.write.value = 1
        self.valid.value = 1

        self.dut._log.debug(f"Register Interface: Writing {hex(data)} to addr: {hex(addr)}")
        # Garantee we write the value at the rising edge
        await RisingEdge(self.dut.clk) 
        # Clocked wait until the ready signal is 1
        while self.ready.value != 1:
            await RisingEdge(self.dut.clk)
        
        assert self.error.value  == 0, f"register interface recorded an error {self.error.value}"

        await FallingEdge(self.dut.clk)
        self.write.value = 0
        self.valid.value = 0
        await RisingEdge(self.dut.clk)

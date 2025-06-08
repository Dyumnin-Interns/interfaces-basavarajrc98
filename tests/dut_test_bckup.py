import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer,RisingEdge, NextTimeStep, ReadOnly
from cocotb_bus.drivers import BusDriver

#Scoreboard Callback
def callback(actual_value):
	global expected_value
	assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"

#Test Coroutine
#Runs the test when we simulate the testbench

@cocotb.test()
async def dut_test(dut):
	global expected_value
	a = (0, 0, 1, 1)	
	b = (0, 1, 0, 1)	
	expected_value = [0, 1, 1, 1]

	clock = Clock(dut.CLK,10,units="ns") #100MHz clock
	cocotb.start_soon(clock.start())

	#wait for a few clock edges
	await RisingEdge(dut.CLK)
	await RisingEdge(dut.CLK)
	dut._log.info("Clock is running")

	#Reset sequence
	dut.RST_N.value = 1
	await Timer(1, 'ns')
	dut.RST_N.value = 0
	await Timer(1, 'ns')
	await RisingEdge(dut.CLK)
	dut.RST_N.value = 1

	#Instantiating Drivers
	adrv = InputDriver(dut,'a',dut.CLK)
	bdrv = InputDriver(dut,'b',dut.CLK)
	OutputDriver(dut, 'y', dut.CLK, callback)

	#Driving inputs	
	for i in range(4):
		adrv.append((4,a[i]))
		bdrv.append((5,b[i]))
	
	#Wait until all expected values have been checked by the scorebaord
	while len(expected_value)>0:
		await(Timer(2,'ns'))

#Input Driver Class
# Waits for rdy signal
# Asserts en and drives data
# Releases control after a clock edge
class InputDriver(BusDriver):
	_signals = ['write_rdy', 'write_en', 'write_data', 'write_addr']

	def __init__(self,dut,name,clk):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.write_en.value = 0
		self.clk = clk

	async def _driver_send(self,addr, value, sync=True):
		if self.bus.rdy.value != 1:
			await RisingEdge(self.bus.rdy)
		# Enable and drive data
		self.bus.addr.value = addr
		self.bus.en.value = 1
		self.bus.data.value = value

		await ReadOnly()
		await RisingEdge(self.clk)

		self.bus.en.value = 0
		await NextTimeStep()

#Output Driver Class
# Waits for DUT to assert rdy
# Captures data value
# Calls the scoreboard callback

class OutputDriver(BusDriver):
	_signals = ['rdy', 'en', 'data','addr']

	def __init__(self,dut,name,clk,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value = 0
		self.clk = clk
		self.callback = sb_callback
		self.append(0)

	async def _driver_send(self, value, sync=True):
		while True:
				if self.bus.rdy.value != 1:
					await RisingEdge(self.bus.rdy)
				self.bus.addr.value = addr
				self.bus.en.value = 1
				await ReadOnly()
				# Call scoreboard callback with received data
				self.callback(self.bus.data.value)
				await RisingEdge(self.clk)
				self.bus.en.value = 0
				await NextTimeStep()
				return int(self.bus.data.value)

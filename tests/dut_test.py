import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from cocotb.triggers import ReadOnly

@cocotb.test()
async def dut_test(dut):
    a = (0, 0, 1, 1)
    b = (0, 1, 0, 1)
    expected = [0, 1, 1, 1]

    # Start clock
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())

    # Reset
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1

    # Apply input and check output
    for i in range(4):
        await write_to_dut(dut, 4, a[i])
        await write_to_dut(dut, 5, b[i])
        await RisingEdge(dut.CLK)

        y = await read_from_dut(dut, 3)
        assert y == expected[i], f"Mismatch: got {y}, expected {expected[i]}"

async def write_to_dut(dut, addr, data):
    dut.write_address.value = addr
    dut.write_data.value = data
    dut.write_en.value = 1
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0
    await RisingEdge(dut.CLK)

async def read_from_dut(dut, addr):
    dut.read_address.value = addr
    dut.read_en.value = 1
    val = dut.read_data.value
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)
    return int(val)


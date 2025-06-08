module cocotb_iverilog_dump();
initial begin
    $dumpfile("sim_build/dut.fst");
    $dumpvars(0, dut);
end
endmodule

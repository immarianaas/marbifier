# Defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Defining path
PWD=$(shell pwd)

# setting the python path to open_source_verfication/src
export PYTHONPATH = $(PWD)/../../../

# Adding all SystemVerilog sources
VERILOG_SOURCES = b2b_tb_dut.sv

# TOPLEVEL is the name of the toplevel module in the Verilog file(s)
TOPLEVEL := toplevel

# RTL Parameters
COMPILE_ARGS += -P$(TOPLEVEL).ADDR_WIDTH=8
COMPILE_ARGS += -P$(TOPLEVEL).DATA_WIDTH=8

# MODULE is the basename of the Python test file
MODULE   := cl_sdt_b2b_test_lib

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
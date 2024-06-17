# This is the makefile for running cocotb tests for the Saturation Filter

PWD=$(shell pwd)

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/hdl/sat_filter.sv

# Defines toplevel RTL
TOPLEVEL := sat_filter

# RTL Parameters
THRESHOLD ?= 8
DATA_W ?= 4

COMPILE_ARGS += -P$(TOPLEVEL).THRESHOLD=$(THRESHOLD)
COMPILE_ARGS += -P$(TOPLEVEL).DATA_W=$(DATA_W)

# Defines cocotb test files
# !!! new tests must be added without spaces, e.g.,
# MODULE := sat_default_test,another_test,another_test !!!
MODULE := sat_default_test

# Set build folder
SIM_BUILD = $(PWD)/sim_build

include $(shell cocotb-config --makefiles)/Makefile.sim
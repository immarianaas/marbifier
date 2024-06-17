# -------------------------------------------------------------------------------
# NOT COCOTB ARGS
# -------------------------------------------------------------------------------

ROOT_DIR = $(shell pwd)

# Defining paths
RTL_DIR = $(ROOT_DIR)/../rtl
TB_DIR = $(ROOT_DIR)

TB_TESTS_DIR = $(ROOT_DIR)/tests

# ALl test modules, for regression testing
TB_TEST_PATHS = $(wildcard tests/cl_marb_*_test.py)
TB_TEST_LIST = $(patsubst tests/%.py, %, $(TB_TEST_PATHS))

REF_MODEL_SOURCEDIR := $(ROOT_DIR)/ref_model
REF_MODEL_BUILDDIR := $(REF_MODEL_SOURCEDIR)/_build

# Make dir if does not exist
$(shell mkdir -p $(REF_MODEL_BUILDDIR))

# because Makefile is in a different directory
export PYTHONPATH := $(TB_DIR):$(TB_TESTS_DIR)

# TODO: This is hard coded because to build it requires the 'Python.h' lib that is only installed with 'python-dev' package.
export PYTHON_H_HOME = '/usr/include/python3.10'
export PYTHON_LIB = $(VIRTUAL_ENV)/lib/python3.10/:$(REF_MODEL_BUILDDIR):$(TB_TESTS_DIR)

# ------------------------------------------------------------------------------
# COCOTB ARGS
# ------------------------------------------------------------------------------

# Defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Verilog source files to include
VERILOG_INCLUDE_DIRS := $(RTL_DIR)
VERILOG_SOURCES := $(RTL_DIR)/pkg_mem_arb_types.sv
VERILOG_SOURCES += $(RTL_DIR)/apb_config_if.sv
VERILOG_SOURCES += $(RTL_DIR)/priority_sel.sv
VERILOG_SOURCES += $(RTL_DIR)/single_sort.sv
VERILOG_SOURCES += $(RTL_DIR)/mem_arb.sv

# TOPLEVEL is the DUT instance
TOPLEVEL := mem_arb

# RTL Parameters
ADDR_WIDTH ?= 8
DATA_WIDTH ?= 8

COMPILE_ARGS += -P$(TOPLEVEL).ADDR_WIDTH=$(ADDR_WIDTH)
COMPILE_ARGS += -P$(TOPLEVEL).DATA_WIDTH=$(DATA_WIDTH)

# MODULE is the basename of the Python test file
MODULE   := tests.cl_marb_basic_test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# ------------------------------------------------------------------------------

# To run our targets and cocotb targets
debug: local-debug
clean::
	@$(MAKE) local-clean -C $(TB_DIR)

# ------------------------------------------------------------------------------
# Because of Reference Model
# ------------------------------------------------------------------------------

# Compiler
CC := gcc

# Flags for compilation (adding warnings are always good)
CFLAGS = -g -Wall --debug

# Source files
REF_MODEL_SOURCES = $(REF_MODEL_SOURCEDIR)/ref_model_wrapper.c \
					$(REF_MODEL_SOURCEDIR)/ref_model.c \
					$(REF_MODEL_SOURCEDIR)/ref_model.h

# ------------------------------------------------------------------------------
# Simulation targets
# ------------------------------------------------------------------------------

# Build wrapper module to be used in Python

# -------------------------------------------------------------------------------
# Clean-up target
# -------------------------------------------------------------------------------

.PHONY: local-clean
local-clean:
	@echo -e "\n------------------ Internal cleanup --------------------\n"
	# Remove build stuff from ref. model
	@rm -fv $(shell find $(REF_MODEL_SOURCEDIR) -type f \( -iname "*.*o" \);)
	# Remove all __pycache__ folders
	@rm -fvr $(shell find $(ROOT_DIR) -type d \( -iname '__pycache__' \);)

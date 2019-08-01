CDPP_PATH 		 = ../cdpp/src
KERNEL_SRC       = $(CDPP_PATH)/cd++
OUT_DIR          = $(shell pwd)/../bin
OBJ_DIR          = $(OUT_DIR)

MODEL_FLAGS      = -DREGISTER_ATOMICS

SOURCES          = $(wildcard *.cpp)
DEPS             = $(SOURCES:.cpp=.dep)
OBJS             = $(SOURCES:.cpp=.o)
OBJS_W_DIR       = $(addprefix ${OBJ_DIR}/, $(OBJS))

NODEPS = clean


include $(KERNEL_SRC)/Makefile.rules
include $(KERNEL_SRC)/Makefile.defs


all : $(OBJS_W_DIR) kernel

kernel :
	$(MAKE) -C $(KERNEL_SRC) cd++ OUT_DIR=$(OUT_DIR) MODEL_FLAGS=$(MODEL_FLAGS)

clean :
	@rm -rf *.dep
	$(MAKE) -C $(KERNEL_SRC) clean OUT_DIR=$(OUT_DIR)

ifeq (0, $(words $(findstring $(MAKECMDGOALS), $(NODEPS))))
sinclude $(DEPS)
endif
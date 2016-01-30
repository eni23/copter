PROJECT_DIR			= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ARDUINO_DIR 		= /home/eni/progs/arduino-1.6.7
FQBN 						= arduino:avr:nano:cpu=atmega328
SRCDIR					= $(PROJECT_DIR)src
OBJDIR					= $(PROJECT_DIR)build
MAINFILE				= main.ino
SRCDIR					= $(PROJECT_DIR)src
OBJDIR					= $(PROJECT_DIR)build
ALIB_DIR				= /home/eni/Arduino/libraries
SERIAL_DEVICE		= /dev/ttyUSB*


# non-config
SKETCH_NAME=$(basename $(MAINFILE))
SRCTMP=$(join $(OBJDIR)/sketch/,$(SKETCH_NAME))
MAIN=$(join $(SRCTMP)/,$(MAINFILE))
ABCMD=$(ARDUINO_DIR)/arduino-builder -compile -hardware "$(ARDUINO_DIR)/hardware" -tools "$(ARDUINO_DIR)/tools-builder" -tools "$(ARDUINO_DIR)/hardware/tools/avr" -built-in-libraries "$(ARDUINO_DIR)/libraries" -libraries "$(ALIB_DIR)" -fqbn=$(FQBN) -build-path "$(OBJDIR)/hex" -warnings=all -verbose
AVRDUDEC=$(ARDUINO_DIR)/hardware/tools/avr/bin/avrdude -C$(ARDUINO_DIR)/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -carduino -b57600 -D -Uflash:w:$(OBJDIR)/hex/$(SKETCH_NAME).ino.hex:i


.PHONY: build find-serial update-temp upload find-monitor-baud

default: build

build: update-temp
	$(ABCMD) $(PROJECT_DIR)build/sketch/$(SKETCH_NAME)/$(SKETCH_NAME).ino

find-serial:
	$(eval USBTTY=$(shell ls -1 $(SERIAL_DEVICE) 2>/dev/null | head -n1 ))
	# Serial device: $(USBTTY)

find-monitor-baud:
	$(eval MONITOR_BAUD=$(shell egrep -Rioh 'Serial.begin[[:punct:]][0-9]{3,5}' $(SRCDIR) | egrep -o '[0-9]{3,5}'))
	# Baudrate: $(MONITOR_BAUD)

monitor: find-serial find-monitor-baud
	screen $(USBTTY) $(MONITOR_BAUD)

upload: find-serial
	$(AVRDUDEC) -P$(USBTTY)

all: build upload

clean:
	-rm -r $(OBJDIR)/*
	-touch $(OBJDIR)/.gitkeep

update-temp:
	mkdir -p $(OBJDIR)/sketch/$(SKETCH_NAME)
	mkdir -p $(OBJDIR)/hex
	cp -r $(SRCDIR)/* $(OBJDIR)/sketch/$(SKETCH_NAME)

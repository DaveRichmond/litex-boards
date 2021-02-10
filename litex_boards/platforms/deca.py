#
# This file is part of LiteX-Boards.
# 
# Copyright (c) David Richmond <dave@prstat.org>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs -------------------------------------------------------------------------
_io = [
    # Clk / Rst
    ("clk50", 0, Pins("M8"),  IOStandard("2.5 V")),
    ("clk50", 1, Pins("P11"), IOStandard("3.3V LVTTL")),
    ("clk50", 2, Pins("N15"), IOStandard("1.5 V")), # DDR3 Clock
    ("clk10", 0, Pins("M9"),  IOStandard("2.5 V")),

    ("serial", 0, 
        Subsignal("tx", Pins("W18")),
        Subsignal("rx", Pins("Y18")),
        IOStandard("3.3-V LVTTL")),

    # Buttons
    ("user_btn", 0, Pins("H21"), IOStandard("1.5 V Schmitt Trigger")),
    ("user_btn", 1, Pins("H22"), IOStandard("1.5 V Schmitt Trigger")),
    ("pwr_btn",  0, Pins("U6"),  IOStandard("3.3-V LVTTL")), 
    
    # Switches
    ("user_sw", 0, Pins("J21"), IOStandard("1.5 V Schmitt Trigger")),
    ("user_sw", 1, Pins("J22"), IOStandard("1.5 V Schmitt Trigger")),

    # LEDs
    ("user_led", 0, Pins("C7"), IOStandard("1.2 V")),
    ("user_led", 1, Pins("C8"), IOStandard("1.2 V")),
    ("user_led", 2, Pins("A6"), IOStandard("1.2 V")),
    ("user_led", 3, Pins("B7"), IOStandard("1.2 V")),
    ("user_led", 4, Pins("C4"), IOStandard("1.2 V")),
    ("user_led", 5, Pins("A5"), IOStandard("1.2 V")),
    ("user_led", 6, Pins("B4"), IOStandard("1.2 V")),
    ("user_led", 7, Pins("C5"), IOStandard("1.2 V")),

    # I2C Capsense
    ("i2c", 0,
        Subsignal("scl", Pins("AB2")),
        Subsignal("sda", Pins("AB3")),
        IOStandard("3.3-V LVTTL")),

    # I2C Power Monitor
    ("i2c", 1, 
        Subsignal("scl", Pins("Y3")),
        Subsignal("sda", Pins("Y1")),
        Subsignal("alert", Pins("Y4")),
        IOStandard("3.3-V LVTTL")),

    # I2C Light/Proximity
    ("i2c", 2, 
        Subsignal("scl", Pins("Y8")),
        Subsignal("sda", Pins("AA8")),
        Subsignal("int", Pins("AA9")),
        IOStandard("3.3-V LVTTL")),

    # I2C Humidity/Temperature
    ("i2c", 3, 
        Subsignal("scl", Pins("Y10")),
        Subsignal("sda", Pins("AA10")),
        Subsignal("data_ready", Pins("AB9")),
        IOStandard("3.3-V LVTTL")),

    ("lm71", 0,
        Subsignal("sc", Pins("AA1")),
        Subsignal("sio", Pins("Y2")),
        Subsignal("cs_n", Pins("AB4")),
        IOStandard("3.3-V LVTTL")),

    ("spi-accel", 0,
        Subsignal("cs_n", Pins("E9")),
        Subsignal("sclk", Pins("B5")),
        Subsignal("miso", Pins("C6")),
        Subsignal("mosi", Pins("D5")),
        Subsignal("int", Pins("E8 D7")),
        IOStandard("1.2 V")),

    ("sdcard", 0,
        Subsignal("clk", Pins("T20")),
        Subsignal("cmd", Pins("T21")),
        Subsignal("dat", Pins("R18 T18 T19 R20")),
        # non-standard controls
        Subsignal("cmd_dir", Pins("U22")),
        Subsignal("d0_dir", Pins("T22")),
        Subsignal("d123_dir", Pins("U21")),
        Subsignal("clk_fb", Pins("R22")),
        IOStandard("1.5 V")),
    ("sdcard_sel", 0, Pins("P13"), IOStandard("3.3-V LVTTL")),

    # Audio
    ("audio", 0,
            Subsignal("aud_mclk", Pins("P14")),
            Subsignal("aud_bclk", Pins("R14")),
            Subsignal("aud_wclk", Pins("R15")),
            Subsignal("aud_din_mfp1", Pins("P15")),
            Subsignal("aud_dout_mfp2", Pins("P18")),
            Subsignal("aud_sclk_mfp3", Pins("P19")),
            Subsignal("aud_spi_ss", Pins("P20")), # also i2c scl
            Subsignal("aud_spi_mosi", Pins("P21")), # i2c sda
            Subsignal("aud_spi_miso", Pins("N21")),
            Subsignal("aud_spi_select", Pins("N22")),
            Subsignal("aud_reset", Pins("M21")),
            Subsignal("aud_gpio_mfp5", Pins("M22")),
            IOStandard("1.5 V")),

    # DDR3 SDRAM
    ("ddram", 0, 
            Subsignal("a", Pins(
                "E21 V20 V21 C20 Y20 J14 V18 U20",
                "Y20 W22 C22 Y22 N18 V22 W20"),
                IOStandard("SSTL-15 Class I")),
            Subsignal("ba", Pins("D19 W19 F19"), IOStandard("SSTL-15 Class I")),
            Subsignal("cas_n", Pins("E20"), IOStandard("SSTL-15 Class I")),
            Subsignal("cke", Pins("B22"), IOStandard("SSTL-15 Class I")),
            Subsignal("clk_p", 
                Pins("D18"), IOStandard("Differential 1.5-V SSTL Class I")),
            Subsignal("clk_n", 
                Pins("E18"), IOStandard("Differential 1.5-V SSTL Class I")),
            Subsignal("cs_n", Pins("F22"), IOStandard("SSTL-15 Class I")),
            Subsignal("dm", Pins("N19 J15"), IOStandard("SSTL-15 Class I")),
            Subsignal("dq", Pins(
                "L20 L19 L18 M15 M18 M14 M20 N20",
                "K19 K18 J18 K20 H18 J20 H20 H19"),
                IOStandard("SSTL-15 Class I")),
            Subsignal("dqs_n", Pins("L15 K15"),
                IOStandard("Differential 1.5-V SSTL Class I")),
            Subsignal("dqs_p", Pins("L14 K14"),
                IOStandard("Differential 1.5-V SSTL Class I")),
            Subsignal("odt", Pins("G22"), IOStandard("SSTL-15 Class I")),
            Subsignal("ras_n", Pins("d22"), IOStandard("SSTL-15 Class I")),
            Subsignal("reset_n", Pins("U19"), IOStandard("SSTL-15 Class I")),
            Subsignal("we_n", Pins("E22"), IOStandard("SSTL-15 Class I"))
        ),
    ("spiflash", 0, 
            Subsignal("cs_n", Pins("R10")),
            Subsignal("clk", Pins("R12")),
            Subsignal("mosi", Pins("P12")),
            Subsignal("miso", Pins("V4")),
            Subsignal("wp", Pins("V5")),
            Subsignal("hold", Pins("P10")),
            IOStandard("3.3-V LVTTL")),
    ("spiflash4x", 0,
            Subsignal("cs_n", Pins("R10")),
            Subsignal("clk", Pins("R12")),
            Subsignal("dq", Pins("P12 V4 V5 P10")),
            IOStandard("3.3-V LVTTL")),

    # GMII Ethernet
    ("eth_clocks", 0,
            Subsignal("tx", Pins("T5")),
            Subsignal("rx", Pins("T6")),
            IOStandard("2.5 V")),
    ("eth", 0,
            Subsignal("rst_n", Pins("R3")),
            Subsignal("mdio", Pins("N8")),
            Subsignal("mdc", Pins("R5")),
            Subsignal("rx_dv", Pins("P4")),
            Subsignal("rx_er", Pins("V1")),
            Subsignal("rx_data", Pins("U5 U4 R7 T6")),
            Subsignal("tx_en", Pins("P3")),
            Subsignal("tx_data", Pins("U2 W1 N9 W2")),
            Subsignal("col", Pins("R4")),
            Subsignal("crs", Pins("P5")),
            IOStandard("2.5 V")),
    ("eth_pcf", 0,
            Subsignal("V9"), IOStandard("3.3-V LVTTL")),

    # HDMI
    ("hdmi", 0,
            Subsignal("d", Pins(
                "C18 D17 C17 C19 D14 B19 D13 A19",
                "C14 A17 B16 C15 A14 A15 A12 A16",
                "A13 C16 C12 B17 B12 B14 A18 C13")),
            Subsignal("clk", Pins("A12")),
            Subsignal("de", Pins("C9")),
            Subsignal("hsync", Pins("B11")),
            Subsignal("vsync", Pins("C11")),
            Subsignal("int", Pins("B10")),
            Subsignal("i2c_scl", Pins("C10")),
            Subsignal("i2c_sda", Pins("B15")),
            Subsignal("i2s_mclk", Pins("A7")),
            Subsignal("i2s_lrclk", Pins("A10")),
            Subsignal("i2s_sclk", Pins("D12")),
            Subsignal("i2s_data", Pins("A9 A11 A8 B8")),
            IOStandard("1.8 V")),

    # USB ULPI
    ("upli", 0, 
            #Subsignal("clk", Pins("H11")), # 1.2V!
            #Subsignal("fault", Pins("D8")), # 1.2V!?!
            Subsignal("stp", Pins("J12")),
            Subsignal("dir", Pins("J13")),
            Subsignal("nxr", Pins("H12")),
            Subsignal("cs", Pins("J11")),
            Subsignal("reset", Pins("E16")),
            Subsignal("data", Pins("E12 E13 H13 E14 H14 D15 E15 F15")),
            IOStandard("1.8 V")),
]

_connectors = [
    # BBB GPIOs
    ("gpio0",
        "W18  Y18  Y19  AA17 AA20 AA19 AB21 AB20 AB19 Y16 " +
        "V16  AB18 V15  W17  AB17 AA16 AB16 W16  AB15 W15 " + 
        "Y14  AA15 AB14 AA14 AB13 AA13 AB12 AA12 AB11 AA11 " +
        "AB10 Y13  Y11  W13  W12  W11  V12  V11  V13  V14 " +
        "Y17  W14  U15  R13"),
    ("gpio1", 
        "Y5   Y6   W6   W7   W8   V8   AB8  V7   R11  AB7 " +
        "AB6  AA7  AA6  Y7   V10  U7   W9   W5   R9   W4 " +
        "P9   V17  W3"),
    ("adc", 
        "F5 F4 J8 J9 J4 H3 K5"),
]

# FIXME!
#def serial_bbb_io(gpio):
#    return [
#        # As there is no onboard serial, we'll attach it to the gpio header
#        ("serial", 0, 
#            Subsignal("tx", Pins(f"{gpio}:0")),
#            Subsignal("rx", Pins(f"{gpio}:1")),
#            IOStandard("3.3-V LVTTL"))
#    ]
#_serial_bbb_io = serial_bbb_io("gpio0")

class Platform(AlteraPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf = False

    def __init__(self):
        AlteraPlatform.__init__(self, "10M50DAF484C6G", _io, _connectors)
        self.add_platform_command("set_global_assignment -name FAMILY \"MAX 10\"")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")

        # and disable config pin so we can use 1.2V on bank8
        self.add_platform_command("set_global_assignment -name AUTO_RESTART_CONFIGURATION ON")
        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name ENABLE_BOOT_SEL_PIN OFF")

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", 0, loose=True), 1e6/50e6)
        self.add_period_constraint(self.lookup_request("clk50", 1, loose=True), 1e6/50e6)
        self.add_period_constraint(self.lookup_request("clk50", 2, loose=True), 1e6/50e6)
        self.add_period_constraint(self.lookup_request("clk10",    loose=True), 1e6/10e6)

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

_io = [
    ("cpu_reset", 0, Pins("K5"), IOStandard("LVCMOS33")),
    ("clk50", 0, Pins("N11"), IOStandard("LVCMOS33")),

    ("spiflash4x", 0, 
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk", Pins("M15")),
        Subsignal("dq", Pins("J13", "J14", "K15", "K16")),
        IOStandard("LVCMOS33")),
    ("spiflash", 0,
        Subsignal("cs_n", Pins("L12")),
        Subsignal("clk", Pins("M15")),
        Subsignal("mosi", Pins("J13")),
        Subsignal("miso", Pins("J14")),
        Subsignal("wp", Pins("K15")),
        Subsignal("hold", Pins("K16")),
        IOStandard("LVCMOS33")),

    ("ddram", 0, 
        Subsignal("a", Pins(
            "B14 C8 A14 C14 C9 B10 D9 A12",
            "D8 A13 B12 A9 A8 B11"),
            IOStandard("SSTL135")),
        Subsignal("ba", Pins("C16 A15 B15"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("B16"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("C11"), IOStandard("SSTL135")),
        Subsignal("we_n", Pins("C12"), IOStandard("SSTL135")),
        #Subsignal("cs_n", Pins(""), IOStandard("SSTL135")),
        Subsignal("dm", Pins("F12 H11"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "F15 F13 E16 D11 E12 E13 D16 E11",
            "G12 J16 G16 J15 H14 H12 H16 H13"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("D14 G14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("D15 F14"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("B9"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("A10"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke", Pins("D13"), IOStandard("SSTL135")),
        Subsignal("odt", Pins("C13"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("E15"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    ("led", 0, Pins("E6"), IOStandard("LVCMOS33")),
    ("user_led", 0, Pins("R6"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("T5"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("R7"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("T7"), IOStandard("LVCMOS33")),
    ("user_led", 4, Pins("R8"), IOStandard("LVCMOS33")),
    ("user_btn", 0, Pins("B7"), IOStandard("LVCMOS33")),
    ("user_btn", 1, Pins("M6"), IOStandard("LVCMOS33")),
    ("user_btn", 2, Pins("N6"), IOStandard("LVCMOS33")),
    ("user_btn", 3, Pins("R5"), IOStandard("LVCMOS33")),
    ("user_btn", 4, Pins("P6"), IOStandard("LVCMOS33")),

    ("sdcard", 0,
            Subsignal("data", Pins("B5 B6 J4 J5")),
            Subsignal("cmd", Pins("K5")),
            Subsignal("clk", Pins("E6")),
            Subsignal("cd", Pins("A7")),
            IOStandard("LVCMOS33"), Misc("SLEW=FAST")),

    ("serial", 0, 
            Subsignal("tx", Pins("T14")),
            Subsignal("rx", Pins("T15")),
            IOStandard("LVCMOS33")),

    ("vga_out", 0,
            Subsignal("hsync_n", Pins("G1")),
            Subsignal("vsync_n", Pins("G2")),
            Subsignal("r", Pins("N2 M4 N3 K2 L4")),
            Subsignal("g", Pins("K3 H3 H4 J3 L2 H5")),
            Subsignal("b", Pins("L3 K1 J1 H2 H1")),
            IOStandard("LVCMOS33")),

    ("eth_ref_clk", 0, Pins("B2"), IOStandard("LVCMOS33")),
    ("eth_clocks", 0, 
            Subsignal("tx", Pins("A4")),
            Subsignal("rx", Pins("F5")),
            IOStandard("LVCMOS33")),
    ("eth", 0,
            Subsignal("rst_n", Pins("C4")),
            Subsignal("mdio", Pins("G5")),
            Subsignal("mdc", Pins("G4")),
            Subsignal("rx_dv", Pins("F3")),
            Subsignal("rx_er", Pins("B1")),
            Subsignal("rx_data", Pins("F4 E1 F2 E5 D3 E3 D1 E2")),
            Subsignal("tx_en", Pins("C2")),
            Subsignal("tx_er", Pins("C7")),
            Subsignal("tx_data", Pins("C3 D4 A3 B4 A5 D5 D6 C6")),
            Subsignal("col", Pins("C1")),
            Subsignal("crs", Pins("A2")),
            IOStandard("LVCMOS33")),
]

class Platform(XilinxPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6
    def __init__(self):
        XilinxPlatform.__init__(self, "xc7a35tftg256-1", _io, toolchain="vivado")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bit"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 15]")
        self.add_platform_command("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets eth_clocks_tx_IBUF]")
        # to allow litevideo to build...
        self.toolchain.pre_synthesis_commands = \
            ["set_param synth.elaboration.rodinMoreOptions "
             "{{rt::set_parameter dissolveMemorySizeLimit 71168}}"]

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)

    def create_programmer(self):
        return VivadoProgrammer()

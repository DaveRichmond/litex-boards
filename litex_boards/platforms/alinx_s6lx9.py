from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

_io = [
    # clock / reset
    ("clk50",     0, Pins("T8"),  IOStandard("LVCMOS33")),
    ("cpu_reset", 0, Pins("L3"),  IOStandard("LVCMOS33")),

    # leds
    ("user_led",  0, Pins("P4"),  IOStandard("LVCMOS33")),
    ("user_led",  1, Pins("N5"),  IOStandard("LVCMOS33")),
    ("user_led",  2, Pins("P5"),  IOStandard("LVCMOS33")),
    ("user_led",  3, Pins("N6"),  IOStandard("LVCMOS33")),

    # Buttons
    ("user_sw",   0, Pins("C3"),  IOStandard("LVCMOS33")),
    ("user_sw",   1, Pins("D3"),  IOStandard("LVCMOS33")),
    ("user_sw",   2, Pins("E4"),  IOStandard("LVCMOS33")),
    ("user_sw",   3, Pins("E3"),  IOStandard("LVCMOS33")),

    # serial
    ("serial", 0, 
        Subsignal("tx", Pins("D12")),
        Subsignal("rx", Pins("C11")),
        IOStandard("LVCMOS33")
    ),

    # spi flash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T3"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("R11"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("P10"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("T10"), IOStandard("LVCMOS33")),
    ),

    # sdram
    ("sdram_clock", 0, Pins("H4"), IOStandard("LVCMOS33"), Misc("SLEW=FAST")),
    ("sdram", 0, 
        Subsignal("a", Pins(
            "J3 J4 K3 K5 P1 N1 M2 M1",
            "L1 K2 K6 K1 J1")),
        Subsignal("dq", Pins(
                "A3 B3 A2 B2 B1 C2 C1 D1",
                "H5 G5 H3 F6 G3 F5 F3 F4")),
        Subsignal("we_n",  Pins("E1")),
        Subsignal("ras_n", Pins("F1")),
        Subsignal("cas_n", Pins("F2")),
        Subsignal("cs_n",  Pins("G1")),
        Subsignal("cke",   Pins("H2")), 
        Subsignal("ba",    Pins("G6 J6")),
        Subsignal("dm",    Pins("E2 H1")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33")
    ),

    # sd
    ("spisdcard", 0,
        Subsignal("clk", Pins("M3")),
        Subsignal("mosi", Pins("L4"), Misc("PULLUP")),
        Subsignal("miso", Pins("L5"), Misc("PULLUP")),
        Subsignal("cs_n", Pins("N3"), Misc("PULLUP")),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),

        # VGA...
]


class Platform(XilinxPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6
    variants = {
        "xc6slx9": "xc6slx9-3-ftg256",
    }
    def __init__(self, programmer="impact", variant="xc6slx9"):
        assert variant in self.variants.keys()
        XilinxPlatform.__init__(self, self.variants[variant], _io)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)

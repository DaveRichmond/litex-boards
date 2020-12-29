from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

_io = [
    ("clk50", 0, Pins("G1"), IOStandard("3.3-V LVTTL")),

    ("serial", 0, 
        Subsignal("tx", Pins("AA21")),
        Subsignal("rx", Pins("AA22")),
        IOStandard("3.3-V LVTTL")),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("E2")),
        Subsignal("clk", Pins("K2")),
        Subsignal("mosi", Pins("D1")),
        Subsignal("miso", Pins("K1")),
        IOStandard("3.3-V LVTTL")),

    ("user_led", 0, Pins("W17"), IOStandard("3.3-V LVTTL")),
    ("user_led", 1, Pins("Y17"), IOStandard("3.3-V LVTTL")),

    ("user_btn", 0, Pins("P4"), IOStandard("3.3-V LVTTL")),
    ("user_btn", 1, Pins("P3"), IOStandard("3.3-V LVTTL")),

    ("seven_seg", 0, 
        Subsignal("segment", Pins("AA19 R19 U20 AB19 AA18 W20 R20 W19")),
        Subsignal("digit", Pins("AB18 U19 R18")),
        IOStandard("3.3-V LVTTL")),

    ("sdram_clock", 0, Pins("W8"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins("V2 V1 U2 U1 T4 T5 V3 Y3 V4 W6 W1 Y6")),
        Subsignal("ba", Pins("Y1 W2")),
        Subsignal("cs_n", Pins("Y2")),
        Subsignal("cke", Pins("Y7")),
        Subsignal("ras_n", Pins("AA3")),
        Subsignal("cas_n", Pins("AB3")),
        Subsignal("we_n", Pins("AA4")),
        Subsignal("dq", Pins("AB9 AA9 AB8 AA8 AB7 AA7 AB5 AA5",
                             "W10 Y10 V11 V12 Y13 W13 V14 W15")),
        Subsignal("dm", Pins("AB4 Y8")),
        IOStandard("3.3-V LVTTL")),

    ("eth_ref_clk", 0, Pins("J22"), IOStandard("3.3-V LVTTL")),
    ("eth_clocks", 0,
        Subsignal("tx", Pins("U21")),
        Subsignal("rx", Pins("D22")),
        IOStandard("3.3-V LVTTL")),
    ("eth", 0,
        Subsignal("rst_n", Pins("P21")),
        Subsignal("mdio", Pins("Y22")),
        Subsignal("mdc", Pins("Y21")),
        Subsignal("rx_dv", Pins("B21")),
        Subsignal("rx_er", Pins("H21")),
        Subsignal("rx_data", Pins("B22 C21 C22 D21 E21 E22 F21 F22")),
        Subsignal("tx_en", Pins("M21")),
        Subsignal("tx_er", Pins("W22")),
        Subsignal("tx_data", Pins("M22 P22 R21 R22 U22 V21 V22 W21")),
        Subsignal("col", Pins("H22")),
        Subsignal("crs", Pins("J21")),
        IOStandard("3.3-V LVTTL")),
]

class Platform(AlteraPlatform):
    default_clk_name = "clk50"
    default_clk_period = 1e9/50e6
    create_rbf = False

    def __init__(self):
        AlteraPlatform.__init__(self, "10CL016YU484C8G", _io)
        self.add_platform_command("set_global_assignment -name FAMILY \"CYCLONE 10 LP\"")

    def create_programmer(self):
        return USBBlaster()
    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", 0, loose=True), 1e9/50e6)

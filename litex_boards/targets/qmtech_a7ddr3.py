import os
import argparse

from migen import *
from litex_boards.platforms import qmtech_a7ddr3
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from litevideo.terminal.core import Terminal

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()
        #self.clock_domains.cd_vga       = ClockDomain(reset_less=True)

        self.submodules.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200, 200e6)
        pll.create_clkout(self.cd_eth, 25e6)
        #pll.create_clkout(self.cd_vga, 25e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)
        #self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_ethernet=False, **kwargs):
        platform = qmtech_a7ddr3.Platform()
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)
        self.submodules.crg = _CRG(platform, sys_clk_freq)
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(
                    platform.request("ddram"),
                    memtype = "DDR3",
                    nphases = 4,
                    sys_clk_freq = sys_clk_freq,
                    interface_type = "MEMORY")
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                    phy = self.ddrphy,
                    module = MT41K128M16(sys_clk_freq, "1:4"),
                    origin = self.mem_map["main_ram"],
                    size = kwargs.get("max_sdram_size", 0x40000000),
                    l2_cache_size = kwargs.get("l2_size", 8192),
                    l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                    l2_cache_reverse = True)

class VGASoC(BaseSoC):
    mem_map = {
        "terminal": 0x30000000,
    }
    mem_map.update(BaseSoC.mem_map)
    def __init__(self, **kwargs):
        BaseSoC.__init__(self, **kwargs)

        self.submodules.terminal = terminal = Terminal()
        self.add_wb_slave(self.mem_map["terminal"], self.terminal.bus)
        self.add_memory_region("terminal", self.mem_map["terminal"], 0x10000)
        vga = self.platform.request("vga_out", 0)
        self.comb += [
            vga.vsync_n.eq(terminal.vsync),
            vga.hsync_n.eq(terminal.hsync),
            vga.r.eq(terminal.red[3:8]),
            vga.g.eq(terminal.green[2:8]),
            vga.b.eq(terminal.blue[3:8]),
        ]

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on QMTech Artix 7 DDR3")
    parser.add_argument("--build", action="store_true", help="build bitstream")
    parser.add_argument("--load", action="store_true", help="load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    parser.add_argument("--with-ethernet", action="store_true", help="Enable ethernet")
    parser.add_argument("--with-vga", action="store_true", help="Enable VGA support")
    args = parser.parse_args()

    soc_class = VGASoC if args.with_vga else BaseSoC
    soc = soc_class(with_ethernet=args.with_ethernet, **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()


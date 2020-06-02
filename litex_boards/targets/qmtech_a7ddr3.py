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

from liteeth.phy.mii import LiteEthPHYMII

from litevideo.terminal.core import Terminal

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()

        # platform signals
        n_reset = ~platform.request("cpu_reset")
        clk50 = platform.request("clk50")

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(n_reset)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200, 200e6)
        pll.create_clkout(self.cd_eth, 25e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_ethernet=False, with_etherbone=False, **kwargs):
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
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYMII(
                    clock_pads = self.platform.request("eth_clocks"),
                    pads = self.platform.request("eth"))
            self.add_csr("ethphy")
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy)
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy)
        self.submodules.leds = LedChaser(
                pads = Cat(*[platform.request("user_led", i) for i in range(5)]),
                sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on QMTech Artix 7 DDR3")
    parser.add_argument("--build", action="store_true", help="build bitstream")
    parser.add_argument("--load", action="store_true", help="load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    parser.add_argument("--with-ethernet", action="store_true", help="Enable ethernet")
    parser.add_argument("--with-etherbone", action="store_true", help="Eneable etherbone")
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc_class = BaseSoC
    soc = soc_class(
            with_ethernet=args.with_ethernet, 
            with_etherbone=args.with_etherbone,
            **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args), run=args.build)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".bit"))

if __name__ == "__main__":
    main()


import os
import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput
from litex_boards.platforms import qmtech_c10starter

from litex.soc.cores.clock import Cyclone10LPPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import W9825G6KH
from litedram.phy import GENSDRPHY

from liteeth.phy.mii import LiteEthPHYMII

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)
        self.clock_domains.cd_eth = ClockDomain()
        clk50 = platform.request("clk50")
        self.submodules.pll = pll = Cyclone10LPPLL(speedgrade="-C8")
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_eth, 25e6)
        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), with_ethernet=False, with_etherbone=False, **kwargs):
        platform = qmtech_c10starter.Platform()
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                    phy                     = self.sdrphy,
                    module                  = W9825G6KH(sys_clk_freq, "1:1"),
                    origin                  = self.mem_map["main_ram"],
                    size                    = kwargs.get("max_sdram_size", 0x2000000),
                    l2_cache_size           = kwargs.get("l2_size", 8192),
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
                pads = Cat(*[platform.request("user_led", i) for i in range(2)]),
                sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on QMTech Cyclone 10 Starter")
    parser.add_argument("--build", action="store_true", help="Build")
    parser.add_argument("--load", action="store_true", help="Load bitfile")
    builder_args(parser)
    soc_sdram_args(parser)
    parser.add_argument("--with-ethernet", action="store_true", help="Enable Ethernet Support")
    parser.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support")
    # shrink memory requirements a little if possible to allow ethernet space
    # still can't create enough spacce for the ethernet buffers :(
    #parser.set_defaults(integrated_rom_size=(28*1024))
    #parser.set_defaults(l2_size=(1*1024))
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc = BaseSoC(
            with_ethernet=args.with_ethernet,
            with_etherbone=args.with_etherbone,
            **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)
    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, soc.build_name + ".sof"))

if __name__ == "__main__": main()

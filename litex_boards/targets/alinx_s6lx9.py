import os
import argparse
from fractions import Fraction

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.io import DDROutput

from litex_boards.platforms import alinx_s6lx9

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser

from litedram.modules import MT48LC16M16
from litedram.phy import GENSDRPHY

class _CRG(Module):
    def __init__(self, platform, clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain(reset_less=True)

        self.submodules.pll = pll = S6PLL(speedgrade=-1)
        pll.register_clkin(platform.request("clk50"), 50e6)
        pll.create_clkout(self.cd_sys,    clk_freq)
        pll.create_clkout(self.cd_sys_ps, clk_freq, phase=90)

        self.specials += DDROutput(1, 0, platform.request("sdram_clock"), ClockSignal("sys_ps"))

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(80e6), **kwargs):
        platform = alinx_s6lx9.Platform()

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            self.add_sdram("sdram",
                phy            = self.sdrphy,
                module         = MT48LC16M16(sys_clk_freq, "1:1"),
                origin         = self.mem_map["main_ram"],
                size           = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size  = kwargs.get("l2_size", 1024),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse = True
            )
        self.submodules.leds = LedChaser(
            pads = Cat(*[platform.request("user_led", i) for i in range(4)]),
            sys_clk_freq = sys_clk_freq)
        self.add_csr("leds")

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Alinx S6LX9 board")
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(os.path.join(builder.gateware_dir, "top.sof"))

if __name__ == "__main__":
    main()
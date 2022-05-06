import os

from my_funcs import update_vendor_counts
from scrapers import *


def main() -> None:
    if os.name != "posix":
        ai.main()
    blinky.main()
    bostik.main()
    cfol.main()
    clc.main()
    east.main()
    es.main()
    fpd.main()
    geaux_bright.main()
    haus_of_holiday_lights.main()
    hc.main()
    hs.main()
    inspire.main()
    innovative.main()
    jjs.main()
    justrgb.main()
    jl_pixel_sequences.main()
    led.main()
    lightem.main()
    lights_on_mamie.main()
    livermore.main()
    ll.main()
    lotn.main()
    magical.main()
  #  mwm.main()
    og.main()
    ppd.main()
    pps.main()
    psp.main()
    rgbsequences.main()
    sa.main()
    sd.main()
    sequence_solutions.main()
    sequence_outlet.main()
    showtime.main()
    sl.main()
    ss.main()
    sol_sequences.main()
    ssequence.main()
    visionarylightshows.main()
    vivid_sequences.main()
    wls.main()
    xl.main()
    xtreme.main()
    update_vendor_counts.main()
    print("Scraping complete.")


if __name__ == "__main__":
    main()

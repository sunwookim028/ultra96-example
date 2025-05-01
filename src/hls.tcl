open_project build_hls
set_top vvadd
add_files vvadd.cpp
open_solution "solution1"
set_part {xczu3eg-sbva484-1-i}
create_clock -period 5 -name default
csynth_design
export_design -rtl verilog -format ip_catalog

exit
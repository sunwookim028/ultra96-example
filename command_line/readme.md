# Command Line Scripting Tutorial for Vivado

## Overview
This tutorial shows how to export a tcl script to recreate the [Quick Start Tutorial](../quick_start/README.md)
project from command line, and how to modify the script to efficiently run the project with different parameters.

## Pre-requisites
A Linux machine with:
- Vitis HLS 2023.2
- Vivado 2023.2
- Finishing the [Quick Start Tutorial](../quick_start/README.md)

## 1. Exporting the TCL script
We now open the Quick Start Tutorial project from command line and export the tcl script to recreate the project here.
```bash
cd command_line
mkdir build_vivado
cd build_vivado
vivado -mode tcl
```
you should see the following prompt:
```

****** Vivado v2023.2 (64-bit)
  **** SW Build 4029153 on Fri Oct 13 20:13:54 MDT 2023
  **** IP Build 4028589 on Sat Oct 14 00:45:43 MDT 2023
  **** SharedData Build 4025554 on Tue Oct 10 17:18:54 MDT 2023
    ** Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
    ** Copyright 2022-2023 Advanced Micro Devices, Inc. All Rights Reserved.

Sourcing tcl script '/home/yd383/.Xilinx/Vivado/Vivado_init.tcl'
initializing Vivado using custom script...
done
```
which means Vivado has lunched it's interactive tcl shell mode. Let's open the Quick Start Tutorial project:
```tcl
open_project ../../quickstart/src/build_vivado/project_1/project_1.xpr
```
Vivado will output some information about the command you just executed:
```
Scanning sources...
Finished scanning sources
INFO: [IP_Flow 19-234] Refreshing IP repositories
INFO: [IP_Flow 19-1700] Loaded user IP repository '/scratch/users/phd/yd383/ultra96-example/quickstart/src/build_hls/solution1/impl/ip'.
INFO: [IP_Flow 19-2313] Loaded Vivado IP repository '/opt/xilinx/Vivado/2023.2/data/ip'.
open_project: Time (s): cpu = 00:00:09 ; elapsed = 00:00:10 . Memory (MB): peak = 1614.953 ; gain = 95.156 ; free physical = 142194 ; free virtual = 197406
project_1
```
Now we export a tcl script to recreate the project:
```tcl
write_project_tcl project_1.tcl
```
You will see Vivado executing the command. Pay attention to the output location:
```
INFO: [Vivado-projutils-8] Tcl script 'project_1.tcl' generated in output directory '/scratch/users/phd/yd383/ultra96-example/command_line/build_vivado'
```
it tells us where to find the exported tcl script. It says the script is saved in the `ultra96-example/command_line/build_vivado` directory.
Now we have the script. Let's exit the Vivado tcl shell:
```tcl
exit
```
and return to the tutorial directory:
```bash
cd ..
```

## 2. Recreate the project from the tcl script
Now let's assume we only have the Vivado source files and the tcl script we just created, and try to recreate the project without using the Vivado GUI.
> Here "Vivado source files" means the input files to Vivado, which is the output of HLS. It does not refer to our C++ source of the vector add kernel.

Let's to some setup. We copy the source files from the Quick Start Tutorial:
```bash
cp -r ../quickstart/src/build_hls ./build_hls
```
And the tcl script we just created:
```bash
cp build_vivado/project_1.tcl .
```
Also delete `build_vivado` to pretend a clean start:
```bash
rm -r build_vivado
```
Now you should have a `build_hls` directory, a `project_1.tcl` file, and a readme file (this file) in the `command_line` directory.

We need to make some tweaks to the paths in the tcl script to make it work. Open the `project_1.tcl` file in a text editor, and change all occurances of `$origin_dir/../../quickstart/src` to `$origin_dir/..`. There should be only 3 occurances.
This is because when exporting the script, Vivado will assume you still want to refer to the original source files, which are in the `quickstart/src` directory. So it calculates the relative path from where the script is exported to the original source files. But here we have copied the source files to the `command_line/build_hls` directory, so we need to change the path to refer to the current directory instead.

> At line 50, `$origin_dir` is default to the directory where the script is executed.

Save the tcl file, make a `build_vivado` directory, and run the script inside it:
```bash
mkdir build_vivado
cd build_vivado
vivado -mode batch -source ../project_1.tcl
```
Vivado will execute the script as well as echoing the commands being executed. In a few seconds you should see the following output:
```
# set obj [get_dashboard_gadgets [ list "utilization_2" ] ]
# set_property -name "reports" -value "impl_1#impl_1_place_report_utilization_0" -objects $obj
# move_dashboard_gadget -name {utilization_1} -row 0 -col 0
# move_dashboard_gadget -name {power_1} -row 1 -col 0
# move_dashboard_gadget -name {drc_1} -row 2 -col 0
# move_dashboard_gadget -name {timing_1} -row 0 -col 1
# move_dashboard_gadget -name {utilization_2} -row 1 -col 1
# move_dashboard_gadget -name {methodology_1} -row 2 -col 1
INFO: [Common 17-206] Exiting Vivado at Mon Jun 23 22:11:58 2025...
```
and you should see a `project_1` directory created in the `build_vivado` directory, which contains the recreated Vivado project.
The project has been recreated successfully and is ready to be implemented. Note that synthesis and implementation are not launched yet.

> You can check this by see if the HDL wrapper, `design_1_wrapper.v`, presents in `build_vivado/project_1/project_1.gen/sources_1/bd/design_1/hdl`.

## 3. Modify the script to run synthesis, implementation, and bitstream generation
Now let's modify the script to run synthesis and implementation automatically. Open the `project_1.tcl` file in a text editor, and add the following lines at the end of the file:
```tcl
launch_runs impl_1 -to_step write_bitstream
wait_on_run [get_runs impl_1]
```

Save the tcl file, delete `build_viivado` for a clean start, and run the script again.
This time we run Vivado with the `-notrace` option to surpress the command echoing, so we can focus on the Vivado outputs.
```bash
cd ..
rm -r build_vivado
mkdir build_vivado
cd build_vivado
vivado -mode batch -notrace -source ../project_1.tcl
```
when you see Vivado outputs:
```
[Mon Jun 23 22:21:35 2025] Launched impl_1...
Run output will be captured here: /scratch/users/phd/yd383/ultra96-example/command_line/build_vivado/project_1/project_1.runs/impl_1/runme.log
launch_runs: Time (s): cpu = 00:00:30 ; elapsed = 00:00:31 . Memory (MB): peak = 3281.059 ; gain = 259.094 ; free physical = 140694 ; free virtual = 195959
[Mon Jun 23 22:21:35 2025] Waiting for impl_1 to finish...
```
it means the synthesis and implementation are launched successfully. It should take a few minutes to finish.
Vivado will output some messages about the implementation progress.
When the implementation is finished, you should see the following output:
```
write_bitstream completed successfully
write_bitstream: Time (s): cpu = 00:00:14 ; elapsed = 00:00:17 . Memory (MB): peak = 5065.660 ; gain = 0.000 ; free physical = 137001 ; free virtual = 192336
INFO: [Common 17-206] Exiting Vivado at Mon Jun 23 22:34:23 2025...
[Mon Jun 23 22:34:28 2025] impl_1 finished
wait_on_runs: Time (s): cpu = 00:09:02 ; elapsed = 00:12:53 . Memory (MB): peak = 3281.059 ; gain = 0.000 ; free physical = 140648 ; free virtual = 195983
INFO: [Common 17-206] Exiting Vivado at Mon Jun 23 22:34:28 2025...
```
and you should fild `design_1_wrapper.bit` in the `build_vivado/project_1/project_1.runs/impl_1` directory, which is the generated bitstream file.

> You can check the reports in the `build_vivado/project_1/project_1.runs/impl_1` directory, such as timing report `design_1_wrapper_timing_summary_routed.rpt`, utilization report `design_1_wrapper_utilization_placed.rpt`, and power report `design_1_wrapper_power_routed.rpt`.

## 4. Extend the script to build the design towards a different frequency
Now let's add a command line argument to the script which allows us to change the target clock frequency of the design.
Open the `project_1.tcl` file in a text editor, lines 96 ~ 111 parses the command line arguments:
```tcl
if { $::argc > 0 } {
  for {set i 0} {$i < $::argc} {incr i} {
    set option [string trim [lindex $::argv $i]]
    switch -regexp -- $option {
      "--origin_dir"   { incr i; set origin_dir [lindex $::argv $i] }
      "--project_name" { incr i; set _xil_proj_name_ [lindex $::argv $i] }
      "--help"         { print_help }
      default {
        if { [regexp {^-} $option] } {
          puts "ERROR: Unknown option '$option' specified, please type '$script_file -tclargs --help' for usage info.\n"
          return 1
        }
      }
    }
  }
}
```
Let's add a new command line argument `--freq` to specify the target clock frequency of the design. Note that all arguments are optional, so we need to set a default value for it. Add a line above the `if { $::argc > 0 }` line as:
```tcl
set target_freq 200
```
and add the following case to the `switch` statement:
```tcl
"--freq" { incr i; set target_freq [lindex $::argv $i] }
```
now the target frequency will be default to 200 MHz, and can be changed by the `--freq` command line argument.

We should aldo change the help message to provide usage information about the new argument. See the process `print_help` defined at line 69:
```tcl
proc print_help {} {
  variable script_file
  puts "\nDescription:"
  puts "Recreate a Vivado project from this script. The created project will be"
  puts "functionally equivalent to the original project for which this script was"
  puts "generated. The script contains commands for creating a project, filesets,"
  puts "runs, adding/importing sources and setting properties on various objects.\n"
  puts "Syntax:"
  puts "$script_file"
  puts "$script_file -tclargs \[--origin_dir <path>\]"
  puts "$script_file -tclargs \[--project_name <name>\]"
  puts "$script_file -tclargs \[--help\]\n"
  puts "Usage:"
  puts "Name                   Description"
  puts "-------------------------------------------------------------------------"
  puts "\[--origin_dir <path>\]  Determine source file paths wrt this path. Default"
  puts "                       origin_dir path value is \".\", otherwise, the value"
  puts "                       that was set with the \"-paths_relative_to\" switch"
  puts "                       when this script was generated.\n"
  puts "\[--project_name <name>\] Create project with the specified name. Default"
  puts "                       name is the name of the project from where this"
  puts "                       script was generated.\n"
  puts "\[--help\]               Print help information for this script"
  puts "-------------------------------------------------------------------------\n"
  exit 0
}
```
Add a new line about our new argument:
```tcl
puts "\[--freq <MHz>\]         Set the target clock frequency of the design in MHz. Default is 200."
```

Next, we need to pass this argument to the Clock Wizard IP. Vivado defines a process named `cr_bd_design_1` that encodes the commands to create the block design so we need to let it accept such parameter first. Search for `proc cr_bd_design_1 { parentCell }` in the tcl file, and add an argument named `target_freq` to the process. The process definition should look like this:
```tcl
proc cr_bd_design_1 { parentCell target_freq } {
```
Then we find the instantiation of the Clock Wizard IP in the process, which should look like this:
```tcl
set clk_wiz_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0 ]
  set_property -dict [list \
    CONFIG.CLKOUT1_JITTER {102.087} \
    CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {200} \
    CONFIG.MMCM_CLKOUT0_DIVIDE_F {6.000} \
    CONFIG.RESET_PORT {resetn} \
    CONFIG.RESET_TYPE {ACTIVE_LOW} \
  ] $clk_wiz_0
```
note the `CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {200}` line, which sets the target clock frequency to 200 MHz. We need to change this to use the `target_freq` argument instead:
```tcl
CONFIG.CLKOUT1_REQUESTED_OUT_FREQ $target_freq
```

Finally, we pass the `target_freq` argument to the `cr_bd_design_1` process when it is called. Search for the line that calls the process as `cr_bd_design_1 ""`, and change it to:
```tcl
cr_bd_design_1 "" $target_freq
```

Save the tcl file, delete `build_vivado` for a clean start, and run the script again with the `--freq` argument:
```bash
cd ..
rm -r build_vivado
mkdir build_vivado
cd build_vivado
vivado -mode batch -notrace -source ../project_1.tcl -tclargs --freq 100
```
When the build is finished, check the timing report and see if the target clock frequency is set to 100 MHz. Open the timing report `build_vivado/project_1/project_1.runs/impl_1/design_1_wrapper_timing_summary_routed.rpt` in a text editor, and search for `Clock Summary` section. You should see something like this:
```
------------------------------------------------------------------------------------------------
| Clock Summary
| -------------
------------------------------------------------------------------------------------------------

Clock                              Waveform(ns)       Period(ns)      Frequency(MHz)
-----                              ------------       ----------      --------------
clk_pl_0                           {0.000 5.000}      10.000          100.000
design_1_i/clk_wiz_0/inst/clk_in1  {0.000 5.000}      10.000          100.000
  clk_out1_design_1_clk_wiz_0_0    {0.000 5.000}      10.000          100.000
```
which the output clock frequency of the Clock Wizard IP is set to 100 MHz, as we specified in the command line argument.

## Conclusion
This tutorial shows how to export a tcl script for a Vivado project, run it from command line, and some simple customizations.
For the full reference of the Vivado tcl commands, please refer to the [Vivado Design Suite Tcl Command Reference Guide](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands).

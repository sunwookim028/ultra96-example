# Quickstart Tutorial for PYNQ using Ultra96-V2 as an Example

## Overview
This tutorial provides a starting example for hardware acceleration using PYNQ on the Ultra96-V2 board. It demonstrates how to create a simple hardware vector-vector addition accelerator using Vitis HLS, build a PYNQ overlay for it, and run it on the Ultra96-V2 board.

## Pre-requisites
A Linux machine with:
- Vitis HLS 2023.2
- Vivado 2023.2
- Graphical interface (either you directly run a GUI Linux OS like Ubuntu Desktop, or use a remote desktop solution)
- Access to a PYNQ Ultra96-V2 board

## Background

### Ultra96-V2 Board
The Ultra96-V2 is a low-cost, low-power development board based on the Xilinx Zynq UltraScale+ MPSoC. It features a dual-core ARM Cortex-A53 processor and an FPGA section called programmable logic (PL) that can be used for hardware acceleration.


<div align="center">

<img src="images/TNN22685-front.jpg" alt="Front view of the Ultra96-V2 board" style="width:300px; height:200px;" />

<i>Ultra96-V2 board. Source: <a herf="https://www.avnet.com/americas/products/avnet-boards/avnet-board-families/ultra96-v2/">avnet.com</a></i>

</div>

The board comes with a pre-installed PYNQ OS image, which is based on Linux and includes the necessary drivers and libraries to interact with the hardware. You can remote login to the board with SSH, copy deployment files with SCP, and use Python to run the accelerated applications.

The ARM processor shares the same 2GB memory with the PL, which allows for efficient data transfer between the two. However, there is no protection from the PL side, which means if a bug in the hardware caused it to mess with the memory that the OS is using, the board will crash. You need to reboot the board to recover from this.

Also the 2GB memory is pretty limited if you want to directly code on it with modern IDEs. I highly recommend you finish most of the coding elsewhere and only use the board for testing. If you need to make small on-site tweaks to the code, use some lightweight text editor like vim or nano. **Do not** try to install a full IDE (like VSCode or PyCharm) on the board.

> Also **do not** login to the board with the remote-ssh extension in VSCode. It will install a full-fleged VSCode server on the board, which is too much for its capabilities. Login with a regular terminal instead.

### PYNQ Framework
The <u>Py</u>thon productivipy for ZY<u>NQ</u> (PYNQ) framework allows users to easily invoke the accelerators in the PL with Python. It provides a Python API to program the PL, discover accelerators, and read and write the interface registers of the PL accelerators. For your accelerator to be compatible with PYNQ, it must obey a few interfacing and control rules. In this tutorial, we use Vitis HLS to generate a PYNQ-compatiable accelerator so there is no need to worry about these rules.

On the Ultra96-V2 board we are using, it runs Python 3.6.5 with PYNQ 2.6.0.

## The Tutorial

### 1. Setting up the Environment
First, clone this repo:
```bash
git clone git@github.com:yxd97/ultra96-example.git
cd ultra96-example
```

We then need to setup the tools to generate the example vector-vector addition accelerator. We need Vitis HLS to trun our C++ code into Verilog, and use Vivado in GUI mode to generate the FPGA bitstream for the Ultra96-V2 board. Please make sure the `vitis_hls` and `vivado` tools are usable, also please check you can reach the Ultra96-V2 board via SSH.

> <p style="color:Red; background-color:#FF000030"> For Conrell Zhang Research Group users:</p>
> We will be using the `brg-zhang-xcel` server for this tutorial.
> I have included a `setup.sh` script that will set things up on our research servers. On our servers, simply do:
> ```bash
> source setup.sh
> ```
> Our research servers have direct network access to them, but from your local machine you must connect to **Cornell ECE Departmental VPN** (it is different than the Cornell VPN). The username of the all boards is `xilinx`. Please ask your mentor for the password.
>
> Here are the device IP addresses in our research lab:
> - 132.236.59.63
> - 132.236.59.64
> - 132.236.59.68
> - 132.236.59.70
> - 132.236.59.71
> - 132.236.59.72
> - 132.236.59.75
> - 132.236.59.76
> - 132.236.59.77
> - 132.236.59.80
>
> Not all of them may be up and running. You need to try SSH and see which ones are available.
> Also, since these boards use an SD card as the disk, they have the risk of file system corruption. If you see weird file IO errors please avoid using that board.

> In case you need to do a factory-reset of the board (usually due to file system corruption), you can use the vendor-provided [factory image from Avnet](https://www.avnet.com/wcm/connect/7339b7a6-0c1c-4bf4-bf60-8e53898ab358/Ultra96v2_Factory_Image_Write_190611.zip?MOD=AJPERES&CVID=picLVU9)

### 2. Use Vitis HLS to Generate the Verilog Code
I have provided the C++ implementation for the vector-vector addition accelerator in `src/vvadd.cpp`. It is a simple function that takes two vectors of floats and adds them together. We will use Vitis HLS to convert this C++ code into Verilog code that can be synthesized into hardware, with the following steps:
```bash
cd src
vitis_hls -f hls.tcl
```
You will see Vitis HLS outputing information to the terminal. When there are no errors, a directory named `build_hls` will be created under `src`. Vitis HLS packges our RTL into an IP core located at `src/build_hls/solution1/impl/ip`, which we will import into Vivado soon. Although this tutorial is not about HLS, it's still recommended to check the synthesis report to see if the design meets your timing and resource requirements. You can find the synthesis report in `src/build_hls/solution1/syn/report` directory. The report is named `vvadd_csynth.rpt`.

> Notice the `#pragma HLS INTERFACE` directives in the C++ code. They are how we tell Vitis HLS to generate a PYNQ-compatible accelerator. Details are out of the scope of this tutorial, but you can check the [Vitis HLS User Guide](https://docs.amd.com/r/2023.2-English/ug1399-vitis-hls/pragma-HLS-interface) for more information.

### 3. Use Vivado to Build the PYNQ Hardware Overlay

> I recommend you regularly save your project in Vivado, which will minimize the loss of unexpected crashes.

#### 3.1 Create a Vivado Project
Now we will be using Vivado in GUI mode. Make sure you are working with a GUI Linux environment.

> <p style="color:Red; background-color:#FF000030"> For Conrell Zhang Research Group users:</p>
> You may connect to our servers with any Microsoft Remote Desktop client.
> If you are using Windows, you can use the built-in Remote Desktop Connection app.
> If you are using MacOS, you can use the Microsoft Remote Desktop app from the App Store.


I recommend you also make a build directory for Vivado by:
```bash
mkdir build_vivado
cd build_vivado
```
Then under the `build_vivado` directory we just created, run:
```bash
vivado
```
to open the Vivado GUI. You should see a window like this:

<div align="center">
<img src="images/vivado_welcome.png"/>
</div>

Click "Create Project", then "Next > Next > Next > Next > Next" until is asks you to select the FPGA part number:
<div align="center">
<img src="images/select_part.png"/>
</div>

Search for `xczu3eg-sbva484-1-i`, select it and click "Next > Finish".
<div align="center">
<img src="images/part_selected.png"/>
</div>

A project named `project_1` will be created under the `build_vivado` directory. Now you should see the project window:
<div align="center">
<img src="images/empty_project.png"/>
</div>

#### 3.2 Import the HLS IP Core

Now we need to import the IP core we generated with Vitis HLS. Click "IP Catalog" on the "PROJECT MANAGER" on the left, a new tab named "IP Catalog" will be opened on the right. Right click anywhere in the "IP Catalog" tab and select "Add Repository...":
<div align="center">
<img src="images/add_ip_repo.png"/>
</div>

Navigate to `src/build_hls/solution1/impl/ip` in the pop-up window and click "Select":
<div align="center">
<img src="images/select_ip_repo.png"/>
</div>

Vivado should say there is 1 repository added to the project:
<div align="center">
<img src="images/ip_repo_added.png"/>
</div>
click "OK" to confirm.

#### 3.3 Create a Block Design
Vivado provides block design, an elegant way to glue different IP cores together to quickly bring up a system design. Click "Create Block Design" under the "IP INTEGRATOR" item in the "PROJECT MANAGER" panel on the left, then click "OK" in the pop-up window asking for the name of the block design. We will just stick to the default name for simplicity.
<div align="center">
<img src="images/create_bd.png"/>
</div>

**3.3.1: Add IP Blocks**
A new tab named "Diagram" has been opened on the right, saying "This design is empty. Press the + button to add IP.":
click the <img src="images/btn_add_ip.png"/> icon on the top of the "Diagram" tab to add our HLS IP. Our IP is named as "vvadd" so we can search for it:
<div align="center">
<img src="images/add_ip_vvadd.png"/>
</div>
double-click the found IP to add it to the block design. You should see a block named "vvadd_0" in the diagram.
Repeat the same process to add two other major IPs of our system:
- Clocking Wizard
- Zynq UltraScale+ MPSoC

Now we should have a block design with three blocks similar to this:
<div align="center">
<img src="images/bd_w_main_ips.png"/>
</div>

**3.3.2: Configure IP Parameters.**
The next step is to configure each IP correctly. Double-clicking any IP will open its customization window where we can tweak its parameters.

Let's start with the Clocking Wizard. Double-click the block named "clk_wiz_0", a window named "Re-customize IP" will pop up. In the "Output Clocks" tab, set the requested output frequency to 200MHz and "Reset Type" to "Active Low". This will be the clock driving the accelerator:
<div align="center" style="display: flex; justify-content: center; gap: 10px;">
<img src="images/config_clk_1.png" style="width:50%;" />
<img src="images/config_clk_2.png" style="width:50%;" />
</div>
Click "OK" to confirm.

> Please set this value according to the timing results of your design. An overly high frequency may cause it to crash.

Then we configure the Zynq UltraScale+ MPSoC. Double-click the block named "zynq_ultra_ps_e_0", select "PS-PL Configuration" in the left panel, check the box after "PS-PL Interfaces > Slave Interface > AXI HP > AXI HPC0 FPD" and set the data width to 32 bits:
<div align="center">
<img src="images/config_zynq.png"/>
</div>

**3.3.3: Connect the IPs.**
Now it's time to connect some wires. We will leverage the "connection automation" feature of Vivado to automatically create bridging IPs for clock-domain corssing and asynchronous reset handling.
Click the "Run Connection Automation" message on the top of the "Diagram" tab:
<div align="center">
<img src="images/run_connect_automation.png"/>
</div>

A pop-up window will list the connections that the tool can make. We can configure how we would like these ports to be connected. Here are the configurations:

For `clk_wiz_0` > `clk_in1`, use `/zynq_ultra_ps_e_0/pl_clk0` as the clock source:
<div align="center">
<img src="images/ca_clk_wiz_0_clk_in1.png"/>
</div>

For `clk_wiz_0` > `resetn`, use `/zynq_ultra_ps_e_0/pl_resetn0` as the reset source:
<div align="center">
<img src="images/ca_clk_wiz_0_resetn.png"/>
</div>

For `vvad_0` > `s_axi_control`:
- set "Clock source for driving Bridge IP" to `/zynq_ultra_ps_e_0/pl_clk0`
- set "Clock source for Slave interface" to `/clk_wiz_0/clk_out1`"
- set "Clock source for Master interface" to `zynq_ultra_ps_e_0/pl_clk0`:
<div align="center">
<img src="images/ca_vvadd_0_s_axi_control.png"/>
</div>

For `zync_ultra_ps_e_0` > `S_AXI_HPC0_FPD`:
- set "Clock source for driving Bridge IP" to `/clk_wiz_0/clk_out1`
- set "Clock source for Slave interface" to `/zynq_ultra_ps_e_0/pl_clk0`"
- set "Clock source for Master interface" to `/clk_wiz_0/clk_out1`:
<div align="center">
<img src="images/ca_zynq_ultra_ps_e_0_S_AXI_HPC0_FPD.png"/>
</div>

Click "OK" to confirm. Vivado will automatically create the necessary bridging IPs and connect the wires. The rest pins do not need to be connected. You should see a diagram like this:
<div align="center">
<img src="images/complete_bd.png"/>
</div>

> You can drag the blocks around to make the diagram look nicer.

> You can also use the "Regenerate Layout" (<img src="images/btn_regenerate_layout.png"/>) button to automatically arrange the blocks.

> Now it's a good time to save the project.

**3.3.4: Validate the Block Design.**
Click the <img src="images/btn_validate_bd.png"/> button to validate the design:
<div align="center">
<img src="images/validate_bd.png"/>
</div>

If everything is correct you should see a pop-up window saying "Validation successful. There are no errors or cirtical warnings in the design". Click "OK" to confirm:
<div align="center">
<img src="images/validate_bd_success.png"/>
</div>

> If you see warnings like "[PSU-1]  Actual device frequency is : 479.995209. Minimum actual device frequency supported for DDR for current part is 500.000000.", it's safe to ignore them.

> Now it's a good time to save the project.

#### 3.4 Generate the Bitstream

A block design cannot be directly synthesized. We need to create a Verilog wrapper for it. In the "Sources" tab on the left of the "Diagram" tab, right-click the block design (design_1.bd) and select "Create HDL Wrapper":
<div align="center">
<img src="images/create_hdl_wrapper.png"/>
</div>

In the pop-up window, select "Let Vivado manage wrapper and auto-update" and click "OK". A new file named `design_1_wrapper.v` will be created and selected as the top-level module in the "Sources" tab. The design is now ready for implementation.

> Now it's a good time to save the project.

Click the "Generate Bitstream" button on the left of the Vivado window. A pop-up window will ask you if you want to run synthesis and implementation. Click "Yes" to start the process:
<div align="center">
<img src="images/generate_bitstream.png"/>
</div>

Another pop-up window will ask you about some options. We will stick to defaults now. Click "OK" to start the process and wait for it to finish.

> Depending on the scale of the design, it may take minutes to hours. For this simple example it should take around 10 minutes.

When the process is finished, you should see a window saying "Bitstream Generation successfully completed". This time click "Cancel" to close it because we will not be examining the implemented design in this tutorial:
<div align="center">
<img src="images/bitstream_generated.png"/>
</div>


The "Design Runs" tab on the bottom will show the timing results of the design:
<div align="center">
<img src="images/timing_results.png"/>
</div>

All slack numbers are positive, our design meets timing! Now we can save the project and close Vivado.

### 4. Deploy Our Design to the Ultra96-V2 Board
Now we collect the necessary files to run our accelerated program on the Ultra96-V2 board. We need:
- The bitstream: `src/build_vivado/project_1/project_1.runs/impl_1/design_1_wrapper.bit`
- The hardware handoff : `src/build_vivado/project_1/project_1.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh`
- The host program: `src/host.py`

Let's collect them into one directory that we will SCP to the board. Note PYNQ requires the bitstream and the hardware handoff to have the same base name and placed together.
```bash
cd src
mkdir -p deploy/vvadd-example
cp build_vivado/project_1/project_1.runs/impl_1/design_1_wrapper.bit deploy/vvadd-example/vvadd.bit
cp build_vivado/project_1/project_1.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh deploy/vvadd-example/vvadd.hwh
cp host.py deploy/vvadd-example/host.py
```
Now we can SCP the deployment files to the Ultra96-V2 board. We will directly place it at the home directory of the `xilinx` user:
```bash
scp -r deploy/vvadd-example xilinx@<ip>:~
```
`<ip>` is one of the IP addresses of a running board.

### 5. Run the Program
Once the files are copied, we will SSH to the same board to run the accelerated program:
```bash
# should be the same IP address as above
ssh xilinx@<ip>
```
Then we run the host program:
```bash
cd ~/vvadd-example
sudo python3 host.py vvadd.bit 1024
```
> You may run `sudo python3 host.py -h` to see the help message. The first argument is the bitstream file name, and the second argument is the size of the vectors to be added.

> Do not forget to use `sudo` to run the program. The PYNQ framework requires root privileges to access the hardware.

If you see the following output:
```
Running vector-vector add of size 1024
Software vvadd finished in 0.06306299474090338 ms
Hardware vvadd finished in 0.4180169926257804 ms
Results match!
Speedup: 0.15x
```
Congratulations! You have successfully run your first "hardware-accelerated" program on the Ultra96-V2 board!
There can be various reasons for the speedup to be less than 1x, but optimizing the design is out of the scope of this tutorial.

## Closing Remarks
This tutorial only reveals the tip of the iceberg of what you can do with HLS, PYNQ, and the Ultra96-V2 board.
If you want to learn more, here are some resources:
- [Vitis HLS Programmers Guide](https://docs.amd.com/r/2023.2-English/ug1399-vitis-hls/HLS-Programmers-Guide)
- [PYNQ Documentation](https://pynq.readthedocs.io/en/v2.6.1/)
- [Vivado AXI Reference Guide](https://docs.amd.com/v/u/en-US/ug1037-vivado-axi-reference-guide)
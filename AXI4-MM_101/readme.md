# AXI4-MM 101: A Brief Introduction to the AXI4 Memory-Mapped Interface

## Overview
This tutorial briefly introduces the AXI4 memory-mapped interface, which is used in hardware accelerators for communication between the programmable logic (PL) and the ARM processor on the Ultra96-V2 board. It also provides two hands-on examples to build AXI4-MM systems using Vivado block design.

## Pre-requisites
A Linux machine with:
- Vitis HLS 2023.2
- Vivado 2023.2
- Graphical interface (either you directly run a GUI Linux OS like Ubuntu Desktop, or use a remote desktop solution)
- Access to a PYNQ Ultra96-V2 board

## 1. What is AXI4 Memory-Mapped Interface?
AXI4 (Advanced eXtensible Interface version 4) is part of ARM’s AMBA 4 standard. It includes two main flavors:
- **Memory-Mapped Interfaces**: includes AXI4-Full and AXI4-Lite, access data according to addresses. **It will be the topic of this tutorial.**
- **Stream Interfaces**: includes AXI4-Stream, used for streaming data transfer without address mapping.

AXI4 memory-mapped interfaces (AXI4-MM) are used to connect the programmable logic (PL) with the ARM processor (named processing system, PS) on the Ultra96-V2 board. They allow the PL to read and write data from/to the shared memory, and the PS to read/write PL registers for control and status.

Building a highly optimized AXI-MM system is a complex task and far exceeds the scope of this tutorial. Here, we will only focus building a functional AXI4-MM system. AXI4-MM is a point-to-point, synchronous protocol, which means you can only connect **master-slave paris** driven by the **same clock**. The one sending the address and instructions is called the **master**, and the one responding to the instructions is called the **slave**.

> Although in ARM's terms, the master is called the **manager** and the slave is called the **subordinate**, master/slave is still more widely used in practice.

<detials>
<summary> Quiz </summary>
Which one of the following is a valid AXI4-MM connection?
<div align="center">
<img src="images/quiz1.png"/>
</div>

<detials>
<summary> Answer </summary>
A <br>
B connects a master and a slave from different clocks. C connects two masters. D connects one master to two slaves.
</detials>

</detials>

AXI4-MM adpots a decoupled address/data protocol --- the address and data can be transferred at different times. It is done by implementing five valid-ready handshake **channels**:
- **Read Address Channel (AR)**: the master sends the address of the data to be read on this channel.
- **Read Data Channel (R)**: the slave sends the data back to the master on this channel, along with a status code to indicate whether the read was successful.
- **Write Address Channel (AW)**: the master sends the address of the data to be written on this channel.
- **Write Data Channel (W)**: the master sends the data to be written on this channel.
- **Write Response Channel (B)**: the slave sends back a status code on this channel to indicate whether the write was successful.

We will not go into the details of how to operate these channels in this tutorial. Please refer to [(ARM Developer) Learn the architecture - An introduction to AMBA AXI: Channel transfers and transactions](https://developer.arm.com/documentation/102202/0300/Channel-transfers-and-transactions) for more information.

## 2. Connecting Multiple Masters and Slaves
Of course a realistic system will have multiple masters and slaves. AXI4-MM supports this by using **interconnect components**.
An interconnect component has both master and slave interfaces and coordinates the communication between multiple masters and slaves.
Masters and slaves will expose address spaces for the interconnect component to manage with an **address assignment**,
which is a function that outputs the slave address when fed with a master address.
A valid address assignment must ensure:
- Any master address is mapped to only one slave address (single-valued function).
- All mapped address segments are of equal size.
However, not all the addresses must be used; accessing unused addresses will return an error status code.

<detials>
<summary> Quiz </summary>
Which one of the following is a valid AXI4-MM address assignment?
<div align="center">
<img src="images/quiz2.png"/>
</div>

<detials>
<summary> Answer </summary>
A <br>
B maps one master segment to multiple slave segments.
</detials>

</detials>

## 3. Example of Multi-Master AXI4-MM System
to be finished.

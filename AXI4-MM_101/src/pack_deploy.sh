#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target_ip_address>"
    exit 1
fi
mkdir -p deploy/vvdot-example
cp build_vivado/project_1/project_1.runs/impl_1/design_1_wrapper.bit deploy/vvdot-example/vvdot.bit
cp build_vivado/project_1/project_1.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh deploy/vvdot-example/vvdot.hwh
cp host.py deploy/vvdot-example/host.py
scp -r deploy/vvdot-example xilinx@$1:~
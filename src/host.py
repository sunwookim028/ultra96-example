import argparse, time, pynq, os
import numpy as np
from collections import namedtuple

from pynq.buffer import PynqBuffer as Buffer

class VectorAdd:
    '''
        Helper class to handle the vector add accelerator
    '''

    def __init__(self):
        self.hw_ready = False

    def program_hw(self, bitstream_path:str):
        """
        Program the FPGA with the given bitstream
        """

        # check if the hwh is at the same location as the bitstream
        hwh_path = os.path.splitext(bitstream_path)[0] + ".hwh"
        if not os.path.exists(hwh_path):
            raise FileNotFoundError(f"Cannot find the hwh file at {hwh_path}")

        self.bitstream_path = bitstream_path
        self.pynq_overlay = pynq.Overlay(bitstream_path)
        self.vvadd = self.pynq_overlay.vvadd_0
        self.hw_ready = True
        self.reset_hw()

    def reset_hw(self):
        self.vvadd.register_map.CRTL = 0

    def load_vvadd_inputs(self, a:np.ndarray, b:np.ndarray):
        """
        Load the inputs to the hardware accelerator
        """
        if not self.hw_ready:
            raise RuntimeError("Hardware not ready. Please program the FPGA first.")
        if a.shape != b.shape:
            raise ValueError("Input arrays must have the same shape.")
        if a.dtype != b.dtype:
            raise ValueError("Input arrays must have the same dtype.")
        if a.dtype != np.float32:
            raise ValueError("Input arrays must be of type float32.")

        self.a_buf:Buffer = pynq.buffer.allocate(shape=a.shape[0], dtype=np.float32)
        self.b_buf:Buffer = pynq.buffer.allocate(shape=b.shape[0], dtype=np.float32)
        for i in range(a.shape[0]):
            self.a_buf[i] = a[i]
            self.b_buf[i] = b[i]

    def allocate_vvadd_output_space(self, n:int):
        """
        Allocate space for the output of the hardware accelerator
        """
        if not self.hw_ready:
            raise RuntimeError("Hardware not ready. Please program the FPGA first.")
        if n <= 0:
            raise ValueError("Output size must be greater than 0.")

        self.c_buf:Buffer = pynq.buffer.allocate(shape=n, dtype=np.float32)

    def run_hw_vvadd(self):
        """
        Run the hardware accelerator
        """
        if not self.hw_ready:
            raise RuntimeError("Hardware not ready. Please program the FPGA first.")

        # Load the inputs to the hardware accelerator
        self.a_buf.sync_to_device()
        self.b_buf.sync_to_device()

        # pass pointers to the accelerator
        self.vvadd.register_map.a_1 = self.a_buf.physical_address
        self.vvadd.register_map.b_1 = self.b_buf.physical_address
        self.vvadd.register_map.c_1 = self.c_buf.physical_address
        self.vvadd.register_map.n = self.a_buf.shape[0]

        # Start the hardware accelerator
        self.vvadd.register_map.CTRL.AP_START = 1

        # Wait for the hardware accelerator to finish
        start_time = time.perf_counter()
        while not self.vvadd.register_map.CTRL.AP_DONE:
            pass
        end_time = time.perf_counter()
        hw_time_ms = (end_time - start_time) * 1e3

        # Read the output from the hardware accelerator
        self.c_buf.sync_from_device()
        return np.frombuffer(self.c_buf, dtype=np.float32), hw_time_ms

def main():
    parser = argparse.ArgumentParser(description="Host Program for Vector Add Accelerator")
    parser.add_argument("bitstream", type=str, help="Path to the bitstream file")
    parser.add_argument("size", type=int, help="Size of the vectors to add")
    args = parser.parse_args()
    bitstream_path:str = args.bitstream
    size:int = args.size
    if not os.path.exists(bitstream_path):
        raise FileNotFoundError(f"Cannot find the bitstream file at {bitstream_path}")
    if size <= 0:
        raise ValueError("Size must be greater than 0.")

    print(f"Running vector-vector add of size {size}")

    # Create the input vectors
    a = np.random.rand(size).astype(np.float32)
    b = np.random.rand(size).astype(np.float32)

    # Compute the reference output and time it
    start_time = time.perf_counter()
    c_ref = a + b
    end_time = time.perf_counter()
    sw_time_ms = (end_time - start_time) * 1e3
    print(f"Software vvadd finished in {sw_time_ms} ms")

    # Create the hardware accelerator instance and program it
    xcel = VectorAdd()
    xcel.program_hw(bitstream_path)
    xcel.load_vvadd_inputs(a, b)
    xcel.allocate_vvadd_output_space(size)
    # Run the hardware accelerator and time it
    c_hw, hw_time_ms = xcel.run_hw_vvadd()
    print(f"Hardware vvadd finished in {hw_time_ms} ms")

    # Check the results
    if np.allclose(c_ref, c_hw):
        print("Results match!")
    else:
        print("ERROR: Results do not match!")
        mismatch_idx = np.argmax(c_ref != c_hw)
        print(f"  Mismatch at index {mismatch_idx}")
        print(f"  Reference: {c_ref[mismatch_idx]}")
        print(f"     Actual: {c_hw[mismatch_idx]}")

    # print speedup
    speedup = sw_time_ms / hw_time_ms
    print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    main()
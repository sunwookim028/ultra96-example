import argparse, time, pynq, os
import numpy as np

from pynq.buffer import PynqBuffer

def main():
    parser = argparse.ArgumentParser(description="Host Program for Vector Add Accelerator")
    parser.add_argument("bitstream", type=str, help="Path to the bitstream file")
    parser.add_argument("size", type=int, help="Size of the vectors to add")
    args = parser.parse_args()
    bitstream_path:str = args.bitstream
    size:int = args.size
    if not os.path.exists(bitstream_path):
        raise FileNotFoundError(f"Cannot find the bitstream file at {bitstream_path}")
    hwh_path = os.path.splitext(bitstream_path)[0] + ".hwh"
    if not os.path.exists(hwh_path):
        raise FileNotFoundError(f"Cannot find the hwh file at {hwh_path}")
    if size <= 0:
        raise ValueError("Size must be greater than 0.")

    print(f"Programming hardware with bitstream {bitstream_path}")
    overlay = pynq.Overlay(bitstream_path)
    vvadd_hw = overlay.vvadd_0
    vvadd_hw.register_map.CTRL.AP_START = 0

    print(f"Running vector-vector add of size {size}")

    # Create the input vectors
    a:PynqBuffer = pynq.allocate(size, dtype=np.float32)
    b:PynqBuffer = pynq.allocate(size, dtype=np.float32)

    # Compute the reference output and time it
    start_time = time.perf_counter()
    c_reference = a + b
    end_time = time.perf_counter()
    sw_time_ms = (end_time - start_time) * 1e3
    print(f"Software vvadd finished in {sw_time_ms} ms")

    # allocate space for the output
    c:PynqBuffer = pynq.allocate(size, dtype=np.float32)
    # Run the hardware accelerator and time it
    a.sync_to_device()
    b.sync_to_device()
    vvadd_hw.register_map.a_1 = a.physical_address
    vvadd_hw.register_map.b_1 = b.physical_address
    vvadd_hw.register_map.c_1 = c.physical_address
    vvadd_hw.register_map.n = size
    vvadd_hw.register_map.CTRL.AP_START = 1
    start_time = time.perf_counter()
    while not vvadd_hw.register_map.CTRL.AP_DONE:
        pass
    end_time = time.perf_counter()
    hw_time_ms = (end_time - start_time) * 1e3
    c.sync_from_device()
    print(f"Hardware vvadd finished in {hw_time_ms} ms")

    # Check the results
    if np.allclose(c_reference, c):
        print("Results match!")
    else:
        print("ERROR: Results do not match!")
        mismatch_idx = np.argmax(c_reference != c)
        print(f"  Mismatch at index {mismatch_idx}")
        print(f"  Reference: {c_reference[mismatch_idx]}")
        print(f"     Actual: {c[mismatch_idx]}")

    # print speedup
    speedup = sw_time_ms / hw_time_ms
    print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    main()
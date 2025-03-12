import hashlib
import os
import time
from concurrent.futures import ProcessPoolExecutor
import sys

class AaxHashAlgorithm:
    def __init__(self):
        self.__fixed_key = bytes([0x77, 0x21, 0x4d, 0x4b, 0x19, 0x6a, 0x87, 0xcd, 0x52, 0x00, 0x45, 0xfd, 0x20, 0xa5, 0x1d, 0x67])
        self.__sha1 = hashlib.sha1

    def calculate_checksum(self, activation_hex: str) -> str:
        data = bytes.fromhex(activation_hex)
        intermediate_key = self.__sha1(self.__fixed_key + data).digest()
        intermediate_iv = self.__sha1(self.__fixed_key + intermediate_key + data).digest()
        checksum = self.__sha1(intermediate_key[:16] + intermediate_iv[:16]).digest()
        return checksum.hex()

def calculate_and_append_checksum(activation_key: str, aax_hash: AaxHashAlgorithm, file_handle):
    checksum = aax_hash.calculate_checksum(activation_key)
    data_to_append = f'{checksum} {activation_key}\n'.encode('ascii')  # Encode to bytes
    file_handle.write(data_to_append)


def worker(start: int, end: int, filename: str):
    aax_hash = AaxHashAlgorithm()
    try:
        with open(filename, "ab") as file_handle:  # Use append binary mode for performance
            for i in range(start, end):
                activation_key = format(i, '08x')
                calculate_and_append_checksum(activation_key, aax_hash, file_handle)
            file_handle.flush()  # important to flush together after the loop

    except Exception as e:
        print(f"Worker: Error in worker: {e}", file=sys.stderr)
        return -1


def main():
    filename = "keysToChecksumMap.txt"
    num_processes = 0
    start_time = 0

    if os.path.exists(filename):
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Main: Error removing file: {e}", file=sys.stderr)
            return

    try:
        num_processes = int(input(f"Enter the number of processes to use (default: {os.cpu_count()}): ") or os.cpu_count())
        if num_processes <= 0:
            print("Number of processes must be positive.")
            return #must return
    except ValueError:
        print("Invalid input. Please enter an integer.")
        return #must return


    start_time = time.time()
    total_keys = 0xFFFFFFFF + 1
    chunk_size = total_keys // num_processes

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = []
        for i in range(num_processes):
            start = i * chunk_size
            end = start + chunk_size if i < num_processes - 1 else total_keys
            future = executor.submit(worker, start, end, filename)
            futures.append(future)

        for future in futures:
            try:
                future.result()  # Check for exceptions
            except Exception as e:
                print(f"Main: Exception in worker process: {e}", file=sys.stderr)

    end_time = time.time()
    elapsed_time = end_time - start_time
    total_lines = 0
    try:
       with open(filename,'r') as f:
            total_lines = sum(1 for _ in f)
    except:
        print('no file to count lines')
        return

    lines_per_second = total_lines / elapsed_time if elapsed_time > 0 else 0

    print(f"Finished processing. Total time: {elapsed_time:.2f} seconds")
    print(f"Lines per second: {lines_per_second:.2f}")
    print(f"Total lines made: {total_lines}")

    sys.stdout.flush()

if __name__ == "__main__":
    main()
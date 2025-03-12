package main

import (
	"fmt"
	"os"
	"runtime"
	"sync"
	"time"

	"github.com/StupidRepo/Amaze-on/pkg/utils"
)

func main() {
	f, err := os.Create("checksums.bin")
	if err != nil {
		panic(err)
	}
	defer f.Close()

	startTime := time.Now()
	numWorkers := runtime.NumCPU()
	var wg sync.WaitGroup

	// Determine chunk size
	totalRange := uint64(0xffffffff) + 1
	chunkSize := totalRange / uint64(numWorkers)

	for w := range numWorkers {
		start := uint64(w) * chunkSize
		end := start + chunkSize - 1

		// For the last worker, extend to cover any remaining range
		if w == numWorkers-1 {
			end = 0xffffffff
		}

		wg.Add(1)
		go func(start, end uint64) {
			defer wg.Done()

			const interval = 250_000

			for i := start; i <= end; i++ {
				activationHex := fmt.Sprintf("%08x", i)
				checksum, err := utils.CalculateChecksum(activationHex)
				if err != nil {
					continue
				}

				// Write to file
				fmt.Fprintf(f, "%s:%s\n", activationHex, checksum)

				// Periodic progress update
				if i%interval == 0 {
					fmt.Printf("[Worker %d] Time elapsed: %s, Progress: %.2f%%\n", w, time.Since(startTime), float64(i)/float64(end)*100)
				}
			}

			// Final progress update
			fmt.Printf("[Worker %d] Finished processing range %08x to %08x\n", w, start, end)
		}(start, end)
	}

	wg.Wait()

	endTime := time.Now()
	elapsed := endTime.Sub(startTime)
	fmt.Printf("Total time taken: %s\n", elapsed)
}

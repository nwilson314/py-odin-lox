package benchmark

import "core:fmt"
import "core:time"

fib :: proc(n: int) -> int {
    if n < 2 {
        return n
    }
    return fib(n-1) + fib(n-2)
}

main :: proc() {
    start := time.now()
    result := fib(35)
    end := time.now()
    
    duration := time.diff(start, end)
    seconds := time.duration_seconds(duration)
    
    fmt.printf("fib(35) = %v\n", result)
    fmt.printf("Time taken: %.2f seconds\n", seconds)
}
import time

def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

start_time = time.time()
result = fib(35)
end_time = time.time()

print(f"fib(35) = {result}")
print(f"Time taken: {end_time - start_time:.2f} seconds")
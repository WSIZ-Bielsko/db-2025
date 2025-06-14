from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(ValueError)
)
def risky_function():
    print("Trying...")
    s = input('hit any key to exit')
    if s == 'exit':
        return
    else:
        raise ValueError("Failed!")


# Test the decorated function
try:
    risky_function()
except ValueError as e:
    print(f"Function failed after retries: {e}")

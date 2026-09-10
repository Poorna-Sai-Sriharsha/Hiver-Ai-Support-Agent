from src.generation.safety_guard import SafetyGuard


def test_safety():
    guard = SafetyGuard()
    
    tests = [
        ("Your order is on the way.", True, "Normal response"),
        ("Contact me at test@example.com", False, "Email PII"),
        ("Call me at 1234567890", False, "Phone PII"),
        ("Your order ID is ORDER #12345", False, "Order ID PII"),
        ("You are a stupid idiot", False, "Inappropriate language"),
        ("The total is 10000 USD", False, "Hallucinated number"),
    ]
    
    print(f"{'Test Case':<40} | {'Expected':<10} | {'Actual':<10} | {'Result'}")
    print("-" * 75)
    
    for text, expected, desc in tests:
        is_safe, err = guard.check(text, "")
        print(f"{desc:<40} | {expected!s:<10} | {is_safe!s:<10} | {'PASS' if is_safe == expected else 'FAIL'}")

if __name__ == "__main__":
    test_safety()

# nea
Python to Scratch compiler

A really horrible compiler which only works for about 10% of Python's features.

As of right now, it can turn this into Scratch code:
```python
hello = "Hello world"

def repeat(times: int):
    index = 0
    while index < times:
        index += 1

repeat(40)
```

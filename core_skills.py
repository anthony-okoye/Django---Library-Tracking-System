import random

rand_list = [random.randint(1,20) for _ in range(10)]

list_comprehension_below_10 = [x for x in rand_list if x < 10]

list_filter_below_10 = list(filter(lambda x:x < 10, rand_list))

print(f"Rand_list: {rand_list}")
print(f"List comprehension below 10: {list_comprehension_below_10}")
print(f"Filter below 10: {list_filter_below_10}")

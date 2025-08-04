
import itertools

# _ + _ * _^2 + _^3 - _ = 399

coins = {
    2 : "red",
    9 : "blue",
    5 : "shiny",
    7 : "concave",
    3 : "corroded"
}

for a, b, c, d, e in itertools.permutations(coins, 5):
    x = a + b * c**2 + d**3 - e
    if x == 399:
        y = (a,b,c,d,e)
        print(*y)
        colors = tuple(map(coins.get, y))
        print(*colors)

# def term1(rem):
#     for s3 in rem:
#         t1 = s3**2
#         if term2(t1, rem - {s3}):
#             return True
#     return False

# def term2(t1, rem):
#     for s2 in rem:
#         t2 = s2*t1
#         if t2 > 390:
#             return False
#         if term3(t2, rem - {s2}):
#             return True
#     return False

# def term3(t2, rem):
#     for s4 in rem:
#         t3 = t2 + s4**3
#         if t3 > 390:
#             return False
#         if term4(t3, rem - {s4}):
#             return True
#     return False

# def term4(t3, rem):
#     for s5 in rem:
#         t4 = t3 - s5
#         if t4 > 399:
#             return False
#         if term5(t4, rem - {s5}):
#             return True
#     return False


# def term5(t4, rem):
#     for s1 in rem:
#         t5 = t4 + s1
#         if t5 == 399:
#             return True
#     return False

# print(term1(set(coins)))'
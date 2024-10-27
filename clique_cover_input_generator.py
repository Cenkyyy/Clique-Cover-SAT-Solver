import random

file = open("generated.txt","w")
n = int(input())
k = int(input())
max_edges = (n*(n-1)) // 2

file.writelines(str(n) + "\n")
file.writelines(str(k) + "\n")

for i in range(max_edges):
    u = random.randint(1,n)
    v = random.randint(1,n)
    while(v == u):
        v = random.randint(1,n)
    file.writelines(str(u) + " " + str(v) + "\n")

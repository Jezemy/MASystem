n = int(input())
res = 1
k = 1
while res < n:
	k += 1
	res += 1 / k

print(k)
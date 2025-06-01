import re

def messages_from_file(name):
    with open(name, "r") as file:
        content = file.readlines()
    
    result = []
    for c in content[1:]:
        splitted = c.split(":")
        message = splitted[1].strip()
        result.append(message.split(" "))
    return result

messages = messages_from_file("/home/vyacheslav/1.txt")

print(f"Найдено {len(messages)} зашумленных посылок")

def fix_byte(index):
    res = 0
    a = ""
    for i in range(7):
        b = 0        
        for m in messages:
            char = m[index][i]
            if char=='1':
                b = b + 1
            elif char=='0':
                b = b - 1
        if b < 0:
            res = res<<1
            a = a + '0'
        elif b > 0:            
            res = (res<<1) + 1
            a = a + '1'
        else:
            raise Exception("parity error")
    return res, a

nums = []
bytes = bytearray()
aa = ""
for i in range(len(messages[0])):
    v, a = fix_byte(i)
    aa = aa + " " + a
    nums.append(v)
    bytes.append(v)
print(nums)
print(aa)

print(bytes.decode("ascii"))


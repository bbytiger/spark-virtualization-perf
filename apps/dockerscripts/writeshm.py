from data import get_data

f = open("test.txt", "w+")
print(f"send: writing to shared mem from {__file__}...")
f.write(get_data())
f.close()

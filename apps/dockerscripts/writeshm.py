f = open("test.txt", "w+")
print(f"send writing to shared mem from {__file__}...")
f.write("a very simple message for recv")
f.close()

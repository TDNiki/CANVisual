import can
import queue
queue()
with can.BLFReader("C:\\Users\\NikiD\\Desktop\\camozzi\\CAN1_2204.blf") as reader:
    a = list(reader)

print(a)



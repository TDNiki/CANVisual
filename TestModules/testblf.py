import can

with can.BLFReader("C:\\Users\\NikiD\\Desktop\\camozzi\\CAN1_2204.blf") as reader:
    print(len(list(reader)))
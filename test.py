

file = open('graph_coords.txt', 'r')
line = file.readline()
while line:
    print(line.replace('\n', ''))
    line = file.readline()
print('EOF')

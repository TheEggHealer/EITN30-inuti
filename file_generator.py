data = b'x' * 1000 * 1000

with open('file_1000.txt', 'wb') as file:
  file.write(data)
  file.close()
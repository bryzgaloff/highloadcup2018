import os

now_file_path = os.path.join('/', 'tmp', 'data', 'options.txt')

with open(now_file_path) as now_file:
    now = int(now_file.readline())

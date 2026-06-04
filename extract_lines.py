def extract_lines(filepath, line_ranges):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for start, end in line_ranges:
        print(f"\n{'='*50}")
        print(f"Lines {start} to {end}:")
        print('='*50)
        for i in range(start-1, min(end, len(lines))):
            print(f"{i+1}\t{lines[i]}", end='')

filepath = '/home/ayiecho/projects/yan_website/community.html'

line_ranges = [
    (2325, 2360),
    (2440, 2470),
    (4500, 4520),
    (4805, 4820),
    (4875, 4890),
]

extract_lines(filepath, line_ranges)

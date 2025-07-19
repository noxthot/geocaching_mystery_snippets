import itertools


# Map switches to indices for easier access
switches = ['A', 'B', 'C', 'D', 'E', 'F', 'G']


def is_no_valid_solution(s):
    # s is a dict mapping switch names to 0 (down) or 1 (up)
    
    # 1. C up, B and D down
    if s['C'] == 1 and s['B'] == 0 and s['D'] == 0:
        return True
    
    # 2. A and D down, G up
    if s['A'] == 0 and s['D'] == 0 and s['G'] == 1:
        return True
    
    # 3. A, C, D down
    if s['A'] == 0 and s['C'] == 0 and s['D'] == 0:
        return True
    
    # 4. F down, B and C up
    if s['F'] == 0 and s['B'] == 1 and s['C'] == 1:
        return True
    
    # 5. D and C up
    if s['D'] == 1 and s['C'] == 1:
        return True
    
    # 6. F up, and if G up then A up
    if s['F'] == 1:
        if s['G'] == 1 and s['A'] == 1:
            return True
    
    # 7. A and E up, G down
    if s['A'] == 1 and s['E'] == 1 and s['G'] == 0:
        return True
    
    # 8. C down, D and E up
    if s['C'] == 0 and s['D'] == 1 and s['E'] == 1:
        return True
    
    # 9. A and G up
    if s['A'] == 1 and s['G'] == 1:
        return True
    
    # 10. E down, and if B and F up then C up
    if s['E'] == 0:
        if s['B'] == 1 and s['F'] == 1 and s['C'] == 1:
            return True
    
    # 11. G down and (C or D up)
    if s['G'] == 0 and (s['C'] == 1 or s['D'] == 1):
        return True
    
    # 12. F and G have different positions
    if s['F'] != s['G']:
        return True
    
    # 13. B, C, and E down
    if s['B'] == 0 and s['C'] == 0 and s['E'] == 0:
        return True
    
    # 14. A and B up, E and G down
    if s['A'] == 1 and s['B'] == 1 and s['E'] == 0 and s['G'] == 0:
        return True
    
    # 15. F and G both down
    if s['F'] == 0 and s['G'] == 0:
        return True
    
    return False


def main():
    for vals in itertools.product([0, 1], repeat=len(switches)):
        s = dict(zip(switches, vals))
        if not is_no_valid_solution(s):
            print("Safe configuration:")
            print(' '.join(f"{k}={'up' if v else 'down'}" for k,v in s.items()))


if __name__ == "__main__":
    main()
import re

with open('scraping/emploi.py', encoding='utf-8') as f:
    content = f.read()

# Show the current safe_print definition
m = re.search(r'def safe_print\(.*?\n(?=\S)', content, re.DOTALL)
if m:
    print("Current safe_print:")
    print(m.group())
else:
    print("safe_print function not found with that pattern")

# Fix: replace safe_print body to use builtins
old_func = re.search(r'(def safe_print\(.*?\n)(.*?)((?=\nfrom selenium|\nclass |\nSELENIUM|\n[A-Z_]+\s*=))', content, re.DOTALL)
if old_func:
    print("\nFound function, replacing...")

# Simple approach: replace any self-recursive call inside safe_print
# Replace the inner safe_print( calls (inside the function body) with _print(
fixed = re.sub(
    r'(def safe_print\(\*args, \*\*kwargs\):.*?""".*?""".*?try:.*?)(safe_print\()(\*args, \*\*kwargs\).*?except UnicodeEncodeError:.*?)(safe_print\()([^)]+\), \*\*kwargs\))',
    lambda m2: m2.group(0),  # placeholder
    content,
    flags=re.DOTALL
)

# More targeted: replace the function definition entirely
new_func = '''def safe_print(*args, **kwargs):
    """Print safe pour Windows : remplace les caracteres non-encodables."""
    import builtins
    try:
        builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        builtins.print(msg.encode('ascii', errors='replace').decode('ascii'), **kwargs)'''

# Find and replace the old function
pattern = r'def safe_print\(\*args, \*\*kwargs\):.*?(?=\nfrom selenium|\nclass |\nSELENIUM|\n[A-Z_]+ *=|\ndef (?!safe_print))'
match = re.search(pattern, content, re.DOTALL)
if match:
    print(f"\nFound safe_print at chars {match.start()}-{match.end()}")
    print("Old:")
    print(repr(match.group()[:200]))
    content = content[:match.start()] + new_func + '\n' + content[match.end():]
    with open('scraping/emploi.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("\nFixed! safe_print updated successfully.")
else:
    print("\nCould not find safe_print function with regex")
    # Show first 40 lines
    for i, line in enumerate(content.split('\n')[:40], 1):
        print(f"{i:3}: {line}")

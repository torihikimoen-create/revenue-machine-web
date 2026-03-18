import subprocess
import os

# 実行
result = subprocess.run(['python', 'test_ad_compliance.py'], capture_output=True, text=True, encoding='utf-8', errors='ignore')

# UTF-8で保存
with open('test_output_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    f.write(result.stderr)

print("Test output saved to test_output_utf8.txt (UTF-8)")

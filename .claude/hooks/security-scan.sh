#!/bin/bash
# Auto security scan on code file changes
# Checks for common security issues: secrets, injection patterns, unsafe operations

FILE="$1"
if [ -z "$FILE" ]; then exit 0; fi

# Only scan code files
case "$FILE" in
  *.gd|*.py|*.ts|*.tsx|*.js|*.cs) ;;
  *) exit 0 ;;
esac

ISSUES=0

# Check for hardcoded secrets
if grep -qE "(api_key|secret|password|token)\s*=\s*['\"][^'\"]{8,}" "$FILE" 2>/dev/null; then
    echo "⚠️  SECURITY: 疑似硬編碼密鑰 in $FILE" >&2
    ISSUES=$((ISSUES+1))
fi

# Check for eval/exec on user input (injection risk)
if grep -qE "eval\(|exec\(|os\.system\(" "$FILE" 2>/dev/null; then
    echo "⚠️  SECURITY: 危險函數 eval/exec/os.system in $FILE" >&2
    ISSUES=$((ISSUES+1))
fi

# Check for SQL-like concatenation
if grep -qE "\"SELECT.*\+|'SELECT.*\+" "$FILE" 2>/dev/null; then
    echo "⚠️  SECURITY: 疑似 SQL 拼接 in $FILE" >&2
    ISSUES=$((ISSUES+1))
fi

if [ $ISSUES -gt 0 ]; then
    echo "🔒 安全掃描發現 $ISSUES 個問題，請確認後再繼續。" >&2
fi

exit 0

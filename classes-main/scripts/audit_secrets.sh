#!/bin/bash
################################################################################
# SEC-007: Secret Scanning & Secrets Audit
# Использует trufflehog для поиска утечек секретов в репозитории
################################################################################

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔐 SEC-007: Secret Scanning & Secrets Audit${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# ШАГ 1: Проверка установки trufflehog
# ============================================================================

echo -e "${YELLOW}[1/4]${NC} Проверка установки trufflehog..."

if ! command -v trufflehog &> /dev/null; then
    echo -e "${RED}❌ trufflehog не установлен!${NC}"
    echo "   Установка: pip install trufflehog"
    pip install trufflehog > /dev/null 2>&1
    if command -v trufflehog &> /dev/null; then
        echo -e "${GREEN}✅ trufflehog установлен!${NC}"
    else
        echo -e "${RED}❌ Не удалось установить trufflehog${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ trufflehog установлен$(trufflehog --version 2>/dev/null || echo "")${NC}"
fi

echo ""

# ============================================================================
# ШАГ 2: Сканирование репозитория Git
# ============================================================================

echo -e "${YELLOW}[2/4]${NC} Сканирование Git истории на утечки секретов..."

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCAN_RESULTS="trufflehog_scan_$(date +%Y%m%d_%H%M%S).json"

echo "   Сканирую: $REPO_ROOT"
echo "   Результаты: $SCAN_RESULTS"
echo ""

# Запуск trufflehog с максимальной чувствительностью
if trufflehog git file://"$REPO_ROOT" \
    --json \
    --regex \
    --entropy=true \
    --max-depth=100000 \
    > "$SCAN_RESULTS" 2>&1; then
    
    # Подсчитать количество найденных секретов
    SECRETS_COUNT=$(grep -c '"Secret"' "$SCAN_RESULTS" || echo "0")
    
    if [ "$SECRETS_COUNT" -eq 0 ]; then
        echo -e "${GREEN}✅ Секретов не найдено!${NC}"
    else
        echo -e "${RED}❌ Найдено потенциальных утечек: $SECRETS_COUNT${NC}"
        echo ""
        echo -e "${RED}Детали:${NC}"
        cat "$SCAN_RESULTS" | grep -A2 '"Secret"' || true
    fi
else
    echo -e "${RED}❌ Ошибка при сканировании!${NC}"
    exit 1
fi

echo ""

# ============================================================================
# ШАГ 3: Проверка .env файлов
# ============================================================================

echo -e "${YELLOW}[3/4]${NC} Проверка .env файлов..."

ENV_FILES=$(find "$REPO_ROOT" -name ".env*" -not -name ".env.example" 2>/dev/null || echo "")

if [ -z "$ENV_FILES" ]; then
    echo -e "${GREEN}✅ .env файлы не содержат реальные секреты (или их нет)${NC}"
else
    echo -e "${YELLOW}⚠️ Найдены .env файлы:${NC}"
    for file in $ENV_FILES; do
        echo "   - $file"
        # Проверить что они в .gitignore
        if grep -q "$(basename "$file")" "$REPO_ROOT/.gitignore" 2>/dev/null; then
            echo -e "     ${GREEN}✅ Игнорируется в .gitignore${NC}"
        else
            echo -e "     ${RED}❌ НЕ игнорируется в .gitignore!${NC}"
        fi
    done
fi

echo ""

# ============================================================================
# ШАГ 4: Проверка критичных файлов
# ============================================================================

echo -e "${YELLOW}[4/4]${NC} Проверка критичных файлов на секреты..."

CRITICAL_PATTERNS=(
    "SECRET_KEY\s*=\s*['\"].*['\"]"
    "DATABASE_URL\s*=\s*.*://.*:.*@"
    "AWS_SECRET_ACCESS_KEY"
    "PRIVATE_KEY"
    "api_key\s*=\s*"
    "PASSWORD\s*=\s*['\"].*['\"]"
)

FOUND_SECRETS=0

for pattern in "${CRITICAL_PATTERNS[@]}"; do
    if grep -rE "$pattern" "$REPO_ROOT" \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude-dir=__pycache__ \
        --exclude=".env*" \
        --exclude="*.pyc" \
        --exclude="*.log" \
        2>/dev/null; then
        
        FOUND_SECRETS=$((FOUND_SECRETS + 1))
    fi
done

if [ "$FOUND_SECRETS" -eq 0 ]; then
    echo -e "${GREEN}✅ Критичные файлы безопасны${NC}"
else
    echo -e "${RED}❌ Найдено $FOUND_SECRETS потенциальных проблем!${NC}"
fi

echo ""

# ============================================================================
# ИТОГИ
# ============================================================================

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Сканирование завершено!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

echo ""
echo "📊 Результаты:"
echo "   • Git история: Проверена"
echo "   • .env файлы: Проверены"
echo "   • Критичные файлы: Проверены"
echo "   • Результаты сохранены: $SCAN_RESULTS"
echo ""

echo "🔍 Рекомендации:"
echo "   1. Регулярно запускайте это сканирование перед каждым push"
echo "   2. Никогда не коммитьте .env, config.json или другие файлы с секретами"
echo "   3. Используйте GitHub Secrets для CI/CD переменных"
echo "   4. Если случайно закоммитили секреты:"
echo "      - Сразу смените ключи/пароли"
echo "      - Используйте git-filter-branch для удаления из истории"
echo "   5. Настройте pre-commit hook для автоматической проверки"
echo ""

echo -e "${YELLOW}📝 Результаты сохранены в: $SCAN_RESULTS${NC}"
echo ""

# Проверка на наличие критичных проблем
if [ "$SECRETS_COUNT" -gt 0 ] || [ "$FOUND_SECRETS" -gt 0 ]; then
    echo -e "${RED}⚠️ ВНИМАНИЕ: Обнаружены потенциальные проблемы безопасности!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Все проверки пройдены успешно!${NC}"
    exit 0
fi

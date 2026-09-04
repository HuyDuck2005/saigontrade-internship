#!/bin/bash
OUTPUT="full_source_code.txt"

echo "================ CẤU TRÚC THƯ MỤC ================" > $OUTPUT
find . -not -path '*/\.*' -not -path '*/__pycache__*' | sort | sed 's;[^/]*/;|---;g;s;---|; |;g' >> $OUTPUT

echo -e "\n================ NỘI DUNG CODE ================" >> $OUTPUT
find . -type f -not -path '*/\.*' -not -path '*/__pycache__*' -not -name '*.png' -not -name '*.jpg' -not -name '*.pyc' -not -name 'full_source_code.txt' -not -name 'export_code.sh' | sort | while read -r file; do
    echo -e "\n\n--------------------------------------------------" >> $OUTPUT
    echo "📄 FILE: $file" >> $OUTPUT
    echo "--------------------------------------------------" >> $OUTPUT
    cat "$file" >> $OUTPUT
done

echo "✅ Trích xuất thành công! Hãy mở file full_source_code.txt để xem toàn bộ code."

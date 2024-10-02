#!/bin/bash
set -e

echo "Starting compilation..."
# 컴파일 명령어
gcc -fPIC -shared -o seed_128_lib.so /app/app/services/lib/KISA_SEED_CBC.c
#gcc -fPIC -shared -o seed_128_lib.so /Users/bagjihong/Desktop/KPOP/Backend/app/services/lib/KISA_SEED_CBC.c
# 컴파일이 실패하면 오류 메시지 출력
if [ ! -f "seed_128_lib.so" ]; then
    echo "Error: Failed to create seed_128_lib.so"
    exit 1
fi
file seed_128_lib.so
mv seed_128_lib.so /app/app/services/lib/seed_128_cbc/

#arch -x86_64 gcc -fPIC -c /Users/bagjihong/Desktop/KPOP/Backend/app/services/lib/KISA_SEED_CBC.c -o /Users/bagjihong/Desktop/KPOP/Backend/app/services/lib/KISA_SEED_CBC.o
# rm ./seed_128_lib.so
#arch -x86_64 gcc -shared -o seed_128_lib.so /Users/bagjihong/Desktop/KPOP/Backend/app/services/lib/KISA_SEED_CBC.o

#mv seed_128_lib.so /Users/bagjihong/Desktop/KPOP/Backend/app/services/lib/seed_128_cbc/

echo "seed_128_lib.so created successfully"

# gcc -fPIC -c KISA_SEED_CBC.c -o KISA_SEED_CBC.o
# rm seed_128_lib.so
# gcc -shared -o seed_128_lib.so KISA_SEED_CBC.o
# rm KISA_SEED_CBC.o



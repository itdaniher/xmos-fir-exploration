xmake
xobjdump --split --strip bin/*.xe
~/projects/xtag2-tinkering/load.py image_n0c0.bin
xmake clean
rm platform_def.xn program_info.txt image*.bin

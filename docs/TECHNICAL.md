# Technical notes - Virtual Pro Wrestling

**Conventions:** numbers in hex with `0x`; addresses are RAM addresses unless marked as file
offsets; `u16`/`u32` little-endian unless marked BE. Findings are marked *verified in game* or
*from the code*.

## Contents
- [Image](#image) · [Disc layout](#disc-layout) · [Executable and memory](#executable-and-memory)
- [Archives and compression](#archives-and-compression) · [Text](#text) · [Images](#images)
- [Open questions](#open-questions)

## Image
`Virtual Pro Wrestling (Japan) (Track 01).bin`, 149998800 bytes, SHA-1 `7431095ef7713e440a7e080bf92881eeaa9dc819`.

## Disc layout
| LBA | Size | File | Contents |
|---|---|---|---|
| 23 | 69 | `/SYSTEM.CNF` |  |
| 24 | 200704 | `/SLPS_004.49` |  |
| 122 | 178176 | `/MOV.EXE` |  |
| 209 | 331776 | `/SHINKOU.EXE` |  |
| 371 | 1125840 | `/SHINKOU.BIN` |  |
| 921 | 221184 | `/RESULT.EXE` |  |
| 1029 | 213664 | `/RESULT.BIN` |  |
| 1134 | 131072 | `/STAFF.EXE` |  |
| 1198 | 385776 | `/STAFF.BIN` |  |
| 1387 | 362496 | `/MAIN.EXE` |  |
| 1564 | 45600 | `/SE_MAIN.VH` |  |
| 1587 | 424656 | `/SE_MAIN.VB` |  |
| 1795 | 290 | `/SE_MAIN.SEP` |  |
| 1796 | 61424 | `/D0617.DAT` |  |
| 1826 | 182494 | `/KS0704.BIN` |  |
| 1916 | 281344 | `/T0623.DAT` |  |
| 2055 | 70240 | `/RING/ASM01.DAT` |  |
| 2090 | 70240 | `/RING/ASM03.DAT` |  |
| 2125 | 70240 | `/RING/DAW01.DAT` |  |
| 2160 | 70240 | `/RING/DAW02.DAT` |  |
| 2195 | 70240 | `/RING/EWF01.DAT` |  |
| 2230 | 70240 | `/RING/EWF02.DAT` |  |
| 2265 | 70240 | `/RING/HV_01.DAT` |  |
| 2300 | 70240 | `/RING/HV_03.DAT` |  |
| 2335 | 70240 | `/RING/IAW01.DAT` |  |
| 2370 | 70240 | `/RING/IAW02.DAT` |  |
| 2405 | 70240 | `/RING/ILW01.DAT` |  |
| 2440 | 70240 | `/RING/JR_01.DAT` |  |
| 2475 | 70240 | `/RING/JR_02.DAT` |  |
| 2510 | 70240 | `/RING/NEW01.DAT` |  |
| 2545 | 70240 | `/RING/NEW02.DAT` |  |
| 2580 | 70240 | `/RING/RND00.DAT` |  |
| 2615 | 70240 | `/RING/RND01.DAT` |  |
| 2650 | 70240 | `/RING/RND02.DAT` |  |
| 2685 | 70240 | `/RING/RND04.DAT` |  |
| 2720 | 70240 | `/RING/RND05.DAT` |  |
| 2755 | 70240 | `/RING/RND06.DAT` |  |
| 2790 | 70240 | `/RING/RND07.DAT` |  |
| 2825 | 70240 | `/RING/RND08.DAT` |  |
| 2860 | 70240 | `/RING/WOU01.DAT` |  |
| 2895 | 70240 | `/RING/WOU02.DAT` |  |
| 2932 | 198784 | `/TEX/T30_1/TA01_1.DAT` |  |
| 3030 | 198784 | `/TEX/T30_1/TA02_1.DAT` |  |
| 3128 | 198784 | `/TEX/T30_1/TA03_1.DAT` |  |
| 3226 | 198784 | `/TEX/T30_1/TA04_1.DAT` |  |
| 3324 | 198784 | `/TEX/T30_1/TA05_1.DAT` |  |
| 3422 | 198784 | `/TEX/T30_1/TA06_1.DAT` |  |
| 3520 | 198784 | `/TEX/T30_1/TA07_1.DAT` |  |
| 3618 | 198784 | `/TEX/T30_1/TA08_1.DAT` |  |
| 3716 | 198784 | `/TEX/T30_1/TA09_1.DAT` |  |
| 3814 | 198784 | `/TEX/T30_1/TA10_1.DAT` |  |
| 3912 | 198784 | `/TEX/T30_1/TA11_1.DAT` |  |
| 4010 | 198784 | `/TEX/T30_1/TA12_1.DAT` |  |
| 4108 | 198784 | `/TEX/T30_1/TA13_1.DAT` |  |
| 4206 | 198784 | `/TEX/T30_1/TA14_1.DAT` |  |
| 4304 | 198784 | `/TEX/T30_1/TA15_1.DAT` |  |
| 4402 | 198784 | `/TEX/T30_1/TA16_1.DAT` |  |
| 4500 | 198784 | `/TEX/T30_1/TA17_1.DAT` |  |
| 4598 | 198784 | `/TEX/T30_1/TA18_1.DAT` |  |
| 4696 | 198784 | `/TEX/T30_1/TA19_1.DAT` |  |
| 4794 | 198784 | `/TEX/T30_1/TA20_1.DAT` |  |
| 4892 | 198784 | `/TEX/T30_1/TA21_1.DAT` |  |
| 4990 | 198784 | `/TEX/T30_1/TA22_1.DAT` |  |
| 5088 | 198784 | `/TEX/T30_1/TA23_1.DAT` |  |
| 5186 | 198784 | `/TEX/T30_1/TA24_1.DAT` |  |
| 5284 | 198784 | `/TEX/T30_1/TA25_1.DAT` |  |
| 5382 | 198784 | `/TEX/T30_1/TA26_1.DAT` |  |
| 5480 | 198784 | `/TEX/T30_1/TA27_1.DAT` |  |
| 5578 | 198784 | `/TEX/T30_1/TA28_1.DAT` |  |
| 5676 | 198784 | `/TEX/T30_1/TA29_1.DAT` |  |
| 5774 | 198784 | `/TEX/T30_1/TA30_1.DAT` |  |
| 5873 | 198784 | `/TEX/T30_2/TA01_2.DAT` |  |
| 5971 | 198784 | `/TEX/T30_2/TA02_2.DAT` |  |
| 6069 | 198784 | `/TEX/T30_2/TA03_2.DAT` |  |
| 6167 | 198784 | `/TEX/T30_2/TA04_2.DAT` |  |
| 6265 | 198784 | `/TEX/T30_2/TA05_2.DAT` |  |
| 6363 | 198784 | `/TEX/T30_2/TA06_2.DAT` |  |
| 6461 | 198784 | `/TEX/T30_2/TA07_2.DAT` |  |
| 6559 | 198784 | `/TEX/T30_2/TA08_2.DAT` |  |
| 6657 | 198784 | `/TEX/T30_2/TA09_2.DAT` |  |
| 6755 | 198784 | `/TEX/T30_2/TA10_2.DAT` |  |
| 6853 | 198784 | `/TEX/T30_2/TA11_2.DAT` |  |
| 6951 | 198784 | `/TEX/T30_2/TA12_2.DAT` |  |
| 7049 | 198784 | `/TEX/T30_2/TA13_2.DAT` |  |
| 7147 | 198784 | `/TEX/T30_2/TA14_2.DAT` |  |
| 7245 | 198784 | `/TEX/T30_2/TA15_2.DAT` |  |
| 7343 | 198784 | `/TEX/T30_2/TA16_2.DAT` |  |
| 7441 | 198784 | `/TEX/T30_2/TA17_2.DAT` |  |
| 7539 | 198784 | `/TEX/T30_2/TA18_2.DAT` |  |
| 7637 | 198784 | `/TEX/T30_2/TA19_2.DAT` |  |
| 7735 | 198784 | `/TEX/T30_2/TA20_2.DAT` |  |
| 7833 | 198784 | `/TEX/T30_2/TA21_2.DAT` |  |
| 7931 | 198784 | `/TEX/T30_2/TA22_2.DAT` |  |
| 8029 | 198784 | `/TEX/T30_2/TA23_2.DAT` |  |
| 8127 | 198784 | `/TEX/T30_2/TA24_2.DAT` |  |
| 8225 | 198784 | `/TEX/T30_2/TA25_2.DAT` |  |
| 8323 | 198784 | `/TEX/T30_2/TA26_2.DAT` |  |
| 8421 | 198784 | `/TEX/T30_2/TA27_2.DAT` |  |
| 8519 | 198784 | `/TEX/T30_2/TA28_2.DAT` |  |
| 8617 | 198784 | `/TEX/T30_2/TA29_2.DAT` |  |
| 8715 | 198784 | `/TEX/T30_2/TA30_2.DAT` |  |
| 8814 | 198784 | `/TEX/T60_1/TA31_1.DAT` |  |
| 8912 | 198784 | `/TEX/T60_1/TA32_1.DAT` |  |
| 9010 | 198784 | `/TEX/T60_1/TA33_1.DAT` |  |
| 9108 | 198784 | `/TEX/T60_1/TA34_1.DAT` |  |
| 9206 | 198784 | `/TEX/T60_1/TA35_1.DAT` |  |
| 9304 | 198784 | `/TEX/T60_1/TA36_1.DAT` |  |
| 9402 | 198784 | `/TEX/T60_1/TA37_1.DAT` |  |
| 9500 | 198784 | `/TEX/T60_1/TA38_1.DAT` |  |
| 9598 | 198784 | `/TEX/T60_1/TA39_1.DAT` |  |
| 9696 | 198784 | `/TEX/T60_1/TA40_1.DAT` |  |
| 9794 | 198784 | `/TEX/T60_1/TA41_1.DAT` |  |
| 9892 | 198784 | `/TEX/T60_1/TA42_1.DAT` |  |
| 9990 | 198784 | `/TEX/T60_1/TA43_1.DAT` |  |
| 10088 | 198784 | `/TEX/T60_1/TA44_1.DAT` |  |
| 10186 | 198784 | `/TEX/T60_1/TA45_1.DAT` |  |
| 10284 | 198784 | `/TEX/T60_1/TA46_1.DAT` |  |
| 10382 | 198784 | `/TEX/T60_1/TA47_1.DAT` |  |
| 10480 | 198784 | `/TEX/T60_1/TA48_1.DAT` |  |
| 10578 | 198784 | `/TEX/T60_1/TA49_1.DAT` |  |
| 10676 | 198784 | `/TEX/T60_1/TA50_1.DAT` |  |
| 10774 | 198784 | `/TEX/T60_1/TA51_1.DAT` |  |
| 10872 | 198784 | `/TEX/T60_1/TA52_1.DAT` |  |
| 10970 | 198784 | `/TEX/T60_1/TA53_1.DAT` |  |
| 11068 | 198784 | `/TEX/T60_1/TA54_1.DAT` |  |
| 11166 | 198784 | `/TEX/T60_1/TA55_1.DAT` |  |
| 11264 | 198784 | `/TEX/T60_1/TA56_1.DAT` |  |
| 11362 | 198784 | `/TEX/T60_1/TA57_1.DAT` |  |
| 11460 | 198784 | `/TEX/T60_1/TA58_1.DAT` |  |
| 11558 | 198784 | `/TEX/T60_1/TA59_1.DAT` |  |
| 11656 | 198784 | `/TEX/T60_1/TA60_1.DAT` |  |
| 11755 | 198784 | `/TEX/T60_2/TA31_2.DAT` |  |
| 11853 | 198784 | `/TEX/T60_2/TA32_2.DAT` |  |
| 11951 | 198784 | `/TEX/T60_2/TA33_2.DAT` |  |
| 12049 | 198784 | `/TEX/T60_2/TA34_2.DAT` |  |
| 12147 | 198784 | `/TEX/T60_2/TA35_2.DAT` |  |
| 12245 | 198784 | `/TEX/T60_2/TA36_2.DAT` |  |
| 12343 | 198784 | `/TEX/T60_2/TA37_2.DAT` |  |
| 12441 | 198784 | `/TEX/T60_2/TA38_2.DAT` |  |
| 12539 | 198784 | `/TEX/T60_2/TA39_2.DAT` |  |
| 12637 | 198784 | `/TEX/T60_2/TA40_2.DAT` |  |
| 12735 | 198784 | `/TEX/T60_2/TA41_2.DAT` |  |
| 12833 | 198784 | `/TEX/T60_2/TA42_2.DAT` |  |
| 12931 | 198784 | `/TEX/T60_2/TA43_2.DAT` |  |
| 13029 | 198784 | `/TEX/T60_2/TA44_2.DAT` |  |
| 13127 | 198784 | `/TEX/T60_2/TA45_2.DAT` |  |
| 13225 | 198784 | `/TEX/T60_2/TA46_2.DAT` |  |
| 13323 | 198784 | `/TEX/T60_2/TA47_2.DAT` |  |
| 13421 | 198784 | `/TEX/T60_2/TA48_2.DAT` |  |
| 13519 | 198784 | `/TEX/T60_2/TA49_2.DAT` |  |
| 13617 | 198784 | `/TEX/T60_2/TA50_2.DAT` |  |
| 13715 | 198784 | `/TEX/T60_2/TA51_2.DAT` |  |
| 13813 | 198784 | `/TEX/T60_2/TA52_2.DAT` |  |
| 13911 | 198784 | `/TEX/T60_2/TA53_2.DAT` |  |
| 14009 | 198784 | `/TEX/T60_2/TA54_2.DAT` |  |
| 14107 | 198784 | `/TEX/T60_2/TA55_2.DAT` |  |
| 14205 | 198784 | `/TEX/T60_2/TA56_2.DAT` |  |
| 14303 | 198784 | `/TEX/T60_2/TA57_2.DAT` |  |
| 14401 | 198784 | `/TEX/T60_2/TA58_2.DAT` |  |
| 14499 | 198784 | `/TEX/T60_2/TA59_2.DAT` |  |
| 14597 | 198784 | `/TEX/T60_2/TA60_2.DAT` |  |
| 14697 | 335733 | `/DAT/D30/DA01.DAT` |  |
| 14861 | 363391 | `/DAT/D30/DA02.DAT` |  |
| 15039 | 337692 | `/DAT/D30/DA03.DAT` |  |
| 15204 | 311343 | `/DAT/D30/DA04.DAT` |  |
| 15357 | 302813 | `/DAT/D30/DA05.DAT` |  |
| 15505 | 309452 | `/DAT/D30/DA06.DAT` |  |
| 15657 | 375736 | `/DAT/D30/DA07.DAT` |  |
| 15841 | 323189 | `/DAT/D30/DA08.DAT` |  |
| 15999 | 336816 | `/DAT/D30/DA09.DAT` |  |
| 16164 | 326867 | `/DAT/D30/DA10.DAT` |  |
| 16324 | 340964 | `/DAT/D30/DA11.DAT` |  |
| 16491 | 286943 | `/DAT/D30/DA12.DAT` |  |
| 16632 | 319736 | `/DAT/D30/DA13.DAT` |  |
| 16789 | 330178 | `/DAT/D30/DA14.DAT` |  |
| 16951 | 330908 | `/DAT/D30/DA15.DAT` |  |
| 17113 | 356239 | `/DAT/D30/DA16.DAT` |  |
| 17287 | 328421 | `/DAT/D30/DA17.DAT` |  |
| 17448 | 322009 | `/DAT/D30/DA18.DAT` |  |
| 17606 | 336355 | `/DAT/D30/DA19.DAT` |  |
| 17771 | 301356 | `/DAT/D30/DA20.DAT` |  |
| 17919 | 314563 | `/DAT/D30/DA21.DAT` |  |
| 18073 | 315703 | `/DAT/D30/DA22.DAT` |  |
| 18228 | 322860 | `/DAT/D30/DA23.DAT` |  |
| 18386 | 316289 | `/DAT/D30/DA24.DAT` |  |
| 18541 | 299081 | `/DAT/D30/DA25.DAT` |  |
| 18688 | 341645 | `/DAT/D30/DA26.DAT` |  |
| 18855 | 336887 | `/DAT/D30/DA27.DAT` |  |
| 19020 | 316564 | `/DAT/D30/DA28.DAT` |  |
| 19175 | 306669 | `/DAT/D30/DA29.DAT` |  |
| 19325 | 288556 | `/DAT/D30/DA30.DAT` |  |
| 19467 | 322177 | `/DAT/D60/DA31.DAT` |  |
| 19625 | 304127 | `/DAT/D60/DA32.DAT` |  |
| 19774 | 354765 | `/DAT/D60/DA33.DAT` |  |
| 19948 | 334692 | `/DAT/D60/DA34.DAT` |  |
| 20112 | 367036 | `/DAT/D60/DA35.DAT` |  |
| 20292 | 322818 | `/DAT/D60/DA36.DAT` |  |
| 20450 | 356226 | `/DAT/D60/DA37.DAT` |  |
| 20624 | 330195 | `/DAT/D60/DA38.DAT` |  |
| 20786 | 372881 | `/DAT/D60/DA39.DAT` |  |
| 20969 | 370949 | `/DAT/D60/DA40.DAT` |  |
| 21151 | 376778 | `/DAT/D60/DA41.DAT` |  |
| 21335 | 378407 | `/DAT/D60/DA42.DAT` |  |
| 21520 | 345429 | `/DAT/D60/DA43.DAT` |  |
| 21689 | 329509 | `/DAT/D60/DA44.DAT` |  |
| 21850 | 329074 | `/DAT/D60/DA45.DAT` |  |
| 22011 | 357513 | `/DAT/D60/DA46.DAT` |  |
| 22186 | 347175 | `/DAT/D60/DA47.DAT` |  |
| 22356 | 322023 | `/DAT/D60/DA48.DAT` |  |
| 22514 | 346323 | `/DAT/D60/DA49.DAT` |  |
| 22684 | 348326 | `/DAT/D60/DA50.DAT` |  |
| 22855 | 337745 | `/DAT/D60/DA51.DAT` |  |
| 23020 | 344332 | `/DAT/D60/DA52.DAT` |  |
| 23189 | 351501 | `/DAT/D60/DA53.DAT` |  |
| 23361 | 375678 | `/DAT/D60/DA54.DAT` |  |
| 23545 | 360921 | `/DAT/D60/DA55.DAT` |  |
| 23722 | 378564 | `/DAT/D60/DA56.DAT` |  |
| 23907 | 347582 | `/DAT/D60/DA57.DAT` |  |
| 24077 | 352773 | `/DAT/D60/DA58.DAT` |  |
| 24250 | 356572 | `/DAT/D60/DA59.DAT` |  |
| 24425 | 318803 | `/DAT/D60/DA60.DAT` |  |
| 24583 | 36680 | `/TMD/TMD30_1/01_1M.TMD` |  |
| 24601 | 36376 | `/TMD/TMD30_1/02_1M.TMD` |  |
| 24619 | 35072 | `/TMD/TMD30_1/03_1M.TMD` |  |
| 24637 | 36888 | `/TMD/TMD30_1/04_1M.TMD` |  |
| 24656 | 35640 | `/TMD/TMD30_1/05_1M.TMD` |  |
| 24674 | 35624 | `/TMD/TMD30_1/06_1M.TMD` |  |
| 24692 | 35768 | `/TMD/TMD30_1/07_1M.TMD` |  |
| 24710 | 35960 | `/TMD/TMD30_1/08_1M.TMD` |  |
| 24728 | 36984 | `/TMD/TMD30_1/09_1M.TMD` |  |
| 24747 | 35480 | `/TMD/TMD30_1/10_1M.TMD` |  |
| 24765 | 33976 | `/TMD/TMD30_1/11_1M.TMD` |  |
| 24782 | 35752 | `/TMD/TMD30_1/12_1M.TMD` |  |
| 24800 | 35672 | `/TMD/TMD30_1/13_1M.TMD` |  |
| 24818 | 35472 | `/TMD/TMD30_1/14_1M.TMD` |  |
| 24836 | 34816 | `/TMD/TMD30_1/15_1M.TMD` |  |
| 24853 | 36536 | `/TMD/TMD30_1/16_1M.TMD` |  |
| 24871 | 35200 | `/TMD/TMD30_1/17_1M.TMD` |  |
| 24889 | 35256 | `/TMD/TMD30_1/18_1M.TMD` |  |
| 24907 | 35256 | `/TMD/TMD30_1/19_1M.TMD` |  |
| 24925 | 34648 | `/TMD/TMD30_1/20_1M.TMD` |  |
| 24942 | 36584 | `/TMD/TMD30_1/21_1M.TMD` |  |
| 24960 | 35456 | `/TMD/TMD30_1/22_1M.TMD` |  |
| 24978 | 34552 | `/TMD/TMD30_1/23_1M.TMD` |  |
| 24995 | 36408 | `/TMD/TMD30_1/24_1M.TMD` |  |
| 25013 | 35200 | `/TMD/TMD30_1/25_1M.TMD` |  |
| 25031 | 34672 | `/TMD/TMD30_1/26_1M.TMD` |  |
| 25048 | 35912 | `/TMD/TMD30_1/27_1M.TMD` |  |
| 25066 | 35000 | `/TMD/TMD30_1/28_1M.TMD` |  |
| 25084 | 35288 | `/TMD/TMD30_1/29_1M.TMD` |  |
| 25102 | 34824 | `/TMD/TMD30_1/30_1M.TMD` |  |
| 25121 | 36680 | `/TMD/TMD30_2/01_2M.TMD` |  |
| 25139 | 36376 | `/TMD/TMD30_2/02_2M.TMD` |  |
| 25157 | 35072 | `/TMD/TMD30_2/03_2M.TMD` |  |
| 25175 | 36888 | `/TMD/TMD30_2/04_2M.TMD` |  |
| 25194 | 35640 | `/TMD/TMD30_2/05_2M.TMD` |  |
| 25212 | 35624 | `/TMD/TMD30_2/06_2M.TMD` |  |
| 25230 | 35768 | `/TMD/TMD30_2/07_2M.TMD` |  |
| 25248 | 35960 | `/TMD/TMD30_2/08_2M.TMD` |  |
| 25266 | 36984 | `/TMD/TMD30_2/09_2M.TMD` |  |
| 25285 | 35480 | `/TMD/TMD30_2/10_2M.TMD` |  |
| 25303 | 33976 | `/TMD/TMD30_2/11_2M.TMD` |  |
| 25320 | 35752 | `/TMD/TMD30_2/12_2M.TMD` |  |
| 25338 | 35672 | `/TMD/TMD30_2/13_2M.TMD` |  |
| 25356 | 35472 | `/TMD/TMD30_2/14_2M.TMD` |  |
| 25374 | 34816 | `/TMD/TMD30_2/15_2M.TMD` |  |
| 25391 | 36536 | `/TMD/TMD30_2/16_2M.TMD` |  |
| 25409 | 35200 | `/TMD/TMD30_2/17_2M.TMD` |  |
| 25427 | 35256 | `/TMD/TMD30_2/18_2M.TMD` |  |
| 25445 | 35256 | `/TMD/TMD30_2/19_2M.TMD` |  |
| 25463 | 34648 | `/TMD/TMD30_2/20_2M.TMD` |  |
| 25480 | 36584 | `/TMD/TMD30_2/21_2M.TMD` |  |
| 25498 | 35456 | `/TMD/TMD30_2/22_2M.TMD` |  |
| 25516 | 34552 | `/TMD/TMD30_2/23_2M.TMD` |  |
| 25533 | 36408 | `/TMD/TMD30_2/24_2M.TMD` |  |
| 25551 | 35200 | `/TMD/TMD30_2/25_2M.TMD` |  |
| 25569 | 34672 | `/TMD/TMD30_2/26_2M.TMD` |  |
| 25586 | 35912 | `/TMD/TMD30_2/27_2M.TMD` |  |
| 25604 | 35000 | `/TMD/TMD30_2/28_2M.TMD` |  |
| 25622 | 35288 | `/TMD/TMD30_2/29_2M.TMD` |  |
| 25640 | 34824 | `/TMD/TMD30_2/30_2M.TMD` |  |
| 25659 | 36680 | `/TMD/TMD30_3/01_3M.TMD` |  |
| 25677 | 36376 | `/TMD/TMD30_3/02_3M.TMD` |  |
| 25695 | 35072 | `/TMD/TMD30_3/03_3M.TMD` |  |
| 25713 | 36888 | `/TMD/TMD30_3/04_3M.TMD` |  |
| 25732 | 35640 | `/TMD/TMD30_3/05_3M.TMD` |  |
| 25750 | 35624 | `/TMD/TMD30_3/06_3M.TMD` |  |
| 25768 | 35872 | `/TMD/TMD30_3/07_3M.TMD` |  |
| 25786 | 35872 | `/TMD/TMD30_3/08_3M.TMD` |  |
| 25804 | 36984 | `/TMD/TMD30_3/09_3M.TMD` |  |
| 25823 | 35568 | `/TMD/TMD30_3/10_3M.TMD` |  |
| 25841 | 33976 | `/TMD/TMD30_3/11_3M.TMD` |  |
| 25858 | 35720 | `/TMD/TMD30_3/12_3M.TMD` |  |
| 25876 | 35672 | `/TMD/TMD30_3/13_3M.TMD` |  |
| 25894 | 35472 | `/TMD/TMD30_3/14_3M.TMD` |  |
| 25912 | 34816 | `/TMD/TMD30_3/15_3M.TMD` |  |
| 25929 | 36456 | `/TMD/TMD30_3/16_3M.TMD` |  |
| 25947 | 35200 | `/TMD/TMD30_3/17_3M.TMD` |  |
| 25965 | 35256 | `/TMD/TMD30_3/18_3M.TMD` |  |
| 25983 | 35256 | `/TMD/TMD30_3/19_3M.TMD` |  |
| 26001 | 34648 | `/TMD/TMD30_3/20_3M.TMD` |  |
| 26018 | 36584 | `/TMD/TMD30_3/21_3M.TMD` |  |
| 26036 | 35456 | `/TMD/TMD30_3/22_3M.TMD` |  |
| 26054 | 34552 | `/TMD/TMD30_3/23_3M.TMD` |  |
| 26071 | 36408 | `/TMD/TMD30_3/24_3M.TMD` |  |
| 26089 | 35200 | `/TMD/TMD30_3/25_3M.TMD` |  |
| 26107 | 34672 | `/TMD/TMD30_3/26_3M.TMD` |  |
| 26124 | 35912 | `/TMD/TMD30_3/27_3M.TMD` |  |
| 26142 | 35000 | `/TMD/TMD30_3/28_3M.TMD` |  |
| 26160 | 35288 | `/TMD/TMD30_3/29_3M.TMD` |  |
| 26178 | 34824 | `/TMD/TMD30_3/30_3M.TMD` |  |
| 26197 | 36680 | `/TMD/TMD30_4/01_4M.TMD` |  |
| 26215 | 36376 | `/TMD/TMD30_4/02_4M.TMD` |  |
| 26233 | 35072 | `/TMD/TMD30_4/03_4M.TMD` |  |
| 26251 | 36888 | `/TMD/TMD30_4/04_4M.TMD` |  |
| 26270 | 35640 | `/TMD/TMD30_4/05_4M.TMD` |  |
| 26288 | 35624 | `/TMD/TMD30_4/06_4M.TMD` |  |
| 26306 | 35872 | `/TMD/TMD30_4/07_4M.TMD` |  |
| 26324 | 35872 | `/TMD/TMD30_4/08_4M.TMD` |  |
| 26342 | 36984 | `/TMD/TMD30_4/09_4M.TMD` |  |
| 26361 | 35568 | `/TMD/TMD30_4/10_4M.TMD` |  |
| 26379 | 33976 | `/TMD/TMD30_4/11_4M.TMD` |  |
| 26396 | 35720 | `/TMD/TMD30_4/12_4M.TMD` |  |
| 26414 | 35672 | `/TMD/TMD30_4/13_4M.TMD` |  |
| 26432 | 35472 | `/TMD/TMD30_4/14_4M.TMD` |  |
| 26450 | 34816 | `/TMD/TMD30_4/15_4M.TMD` |  |
| 26467 | 36456 | `/TMD/TMD30_4/16_4M.TMD` |  |
| 26485 | 35200 | `/TMD/TMD30_4/17_4M.TMD` |  |
| 26503 | 35256 | `/TMD/TMD30_4/18_4M.TMD` |  |
| 26521 | 35256 | `/TMD/TMD30_4/19_4M.TMD` |  |
| 26539 | 34648 | `/TMD/TMD30_4/20_4M.TMD` |  |
| 26556 | 36584 | `/TMD/TMD30_4/21_4M.TMD` |  |
| 26574 | 35456 | `/TMD/TMD30_4/22_4M.TMD` |  |
| 26592 | 34552 | `/TMD/TMD30_4/23_4M.TMD` |  |
| 26609 | 36408 | `/TMD/TMD30_4/24_4M.TMD` |  |
| 26627 | 35200 | `/TMD/TMD30_4/25_4M.TMD` |  |
| 26645 | 34672 | `/TMD/TMD30_4/26_4M.TMD` |  |
| 26662 | 35912 | `/TMD/TMD30_4/27_4M.TMD` |  |
| 26680 | 35000 | `/TMD/TMD30_4/28_4M.TMD` |  |
| 26698 | 35288 | `/TMD/TMD30_4/29_4M.TMD` |  |
| 26716 | 34824 | `/TMD/TMD30_4/30_4M.TMD` |  |
| 26735 | 35072 | `/TMD/TMD60_1/31_1M.TMD` |  |
| 26753 | 34912 | `/TMD/TMD60_1/32_1M.TMD` |  |
| 26771 | 36448 | `/TMD/TMD60_1/33_1M.TMD` |  |
| 26789 | 36608 | `/TMD/TMD60_1/34_1M.TMD` |  |
| 26807 | 34864 | `/TMD/TMD60_1/35_1M.TMD` |  |
| 26825 | 35216 | `/TMD/TMD60_1/36_1M.TMD` |  |
| 26843 | 35200 | `/TMD/TMD60_1/37_1M.TMD` |  |
| 26861 | 34144 | `/TMD/TMD60_1/38_1M.TMD` |  |
| 26878 | 34776 | `/TMD/TMD60_1/39_1M.TMD` |  |
| 26895 | 36968 | `/TMD/TMD60_1/40_1M.TMD` |  |
| 26914 | 34728 | `/TMD/TMD60_1/41_1M.TMD` |  |
| 26931 | 34400 | `/TMD/TMD60_1/42_1M.TMD` |  |
| 26948 | 34976 | `/TMD/TMD60_1/43_1M.TMD` |  |
| 26966 | 35640 | `/TMD/TMD60_1/44_1M.TMD` |  |
| 26984 | 35200 | `/TMD/TMD60_1/45_1M.TMD` |  |
| 27002 | 34656 | `/TMD/TMD60_1/46_1M.TMD` |  |
| 27019 | 35360 | `/TMD/TMD60_1/47_1M.TMD` |  |
| 27037 | 34120 | `/TMD/TMD60_1/48_1M.TMD` |  |
| 27054 | 36760 | `/TMD/TMD60_1/49_1M.TMD` |  |
| 27072 | 35512 | `/TMD/TMD60_1/50_1M.TMD` |  |
| 27090 | 34912 | `/TMD/TMD60_1/51_1M.TMD` |  |
| 27108 | 34888 | `/TMD/TMD60_1/52_1M.TMD` |  |
| 27126 | 34552 | `/TMD/TMD60_1/53_1M.TMD` |  |
| 27143 | 34864 | `/TMD/TMD60_1/54_1M.TMD` |  |
| 27161 | 35288 | `/TMD/TMD60_1/55_1M.TMD` |  |
| 27179 | 35472 | `/TMD/TMD60_1/56_1M.TMD` |  |
| 27197 | 35632 | `/TMD/TMD60_1/57_1M.TMD` |  |
| 27215 | 35688 | `/TMD/TMD60_1/58_1M.TMD` |  |
| 27233 | 35784 | `/TMD/TMD60_1/59_1M.TMD` |  |
| 27251 | 35592 | `/TMD/TMD60_1/60_1M.TMD` |  |
| 27270 | 35072 | `/TMD/TMD60_2/31_2M.TMD` |  |
| 27288 | 34912 | `/TMD/TMD60_2/32_2M.TMD` |  |
| 27306 | 36448 | `/TMD/TMD60_2/33_2M.TMD` |  |
| 27324 | 36608 | `/TMD/TMD60_2/34_2M.TMD` |  |
| 27342 | 34864 | `/TMD/TMD60_2/35_2M.TMD` |  |
| 27360 | 35216 | `/TMD/TMD60_2/36_2M.TMD` |  |
| 27378 | 35200 | `/TMD/TMD60_2/37_2M.TMD` |  |
| 27396 | 34144 | `/TMD/TMD60_2/38_2M.TMD` |  |
| 27413 | 34776 | `/TMD/TMD60_2/39_2M.TMD` |  |
| 27430 | 36968 | `/TMD/TMD60_2/40_2M.TMD` |  |
| 27449 | 34728 | `/TMD/TMD60_2/41_2M.TMD` |  |
| 27466 | 34400 | `/TMD/TMD60_2/42_2M.TMD` |  |
| 27483 | 34976 | `/TMD/TMD60_2/43_2M.TMD` |  |
| 27501 | 35640 | `/TMD/TMD60_2/44_2M.TMD` |  |
| 27519 | 35200 | `/TMD/TMD60_2/45_2M.TMD` |  |
| 27537 | 34656 | `/TMD/TMD60_2/46_2M.TMD` |  |
| 27554 | 35360 | `/TMD/TMD60_2/47_2M.TMD` |  |
| 27572 | 34120 | `/TMD/TMD60_2/48_2M.TMD` |  |
| 27589 | 36760 | `/TMD/TMD60_2/49_2M.TMD` |  |
| 27607 | 35512 | `/TMD/TMD60_2/50_2M.TMD` |  |
| 27625 | 34912 | `/TMD/TMD60_2/51_2M.TMD` |  |
| 27643 | 34888 | `/TMD/TMD60_2/52_2M.TMD` |  |
| 27661 | 34552 | `/TMD/TMD60_2/53_2M.TMD` |  |
| 27678 | 34864 | `/TMD/TMD60_2/54_2M.TMD` |  |
| 27696 | 35288 | `/TMD/TMD60_2/55_2M.TMD` |  |
| 27714 | 35472 | `/TMD/TMD60_2/56_2M.TMD` |  |
| 27732 | 35632 | `/TMD/TMD60_2/57_2M.TMD` |  |
| 27750 | 35688 | `/TMD/TMD60_2/58_2M.TMD` |  |
| 27768 | 35784 | `/TMD/TMD60_2/59_2M.TMD` |  |
| 27786 | 35592 | `/TMD/TMD60_2/60_2M.TMD` |  |
| 27805 | 35072 | `/TMD/TMD60_3/31_3M.TMD` |  |
| 27823 | 34912 | `/TMD/TMD60_3/32_3M.TMD` |  |
| 27841 | 36536 | `/TMD/TMD60_3/33_3M.TMD` |  |
| 27859 | 36608 | `/TMD/TMD60_3/34_3M.TMD` |  |
| 27877 | 34864 | `/TMD/TMD60_3/35_3M.TMD` |  |
| 27895 | 35216 | `/TMD/TMD60_3/36_3M.TMD` |  |
| 27913 | 35008 | `/TMD/TMD60_3/37_3M.TMD` |  |
| 27931 | 34808 | `/TMD/TMD60_3/38_3M.TMD` |  |
| 27948 | 34776 | `/TMD/TMD60_3/39_3M.TMD` |  |
| 27965 | 36696 | `/TMD/TMD60_3/40_3M.TMD` |  |
| 27983 | 34728 | `/TMD/TMD60_3/41_3M.TMD` |  |
| 28000 | 34232 | `/TMD/TMD60_3/42_3M.TMD` |  |
| 28017 | 34976 | `/TMD/TMD60_3/43_3M.TMD` |  |
| 28035 | 35640 | `/TMD/TMD60_3/44_3M.TMD` |  |
| 28053 | 35112 | `/TMD/TMD60_3/45_3M.TMD` |  |
| 28071 | 34656 | `/TMD/TMD60_3/46_3M.TMD` |  |
| 28088 | 35360 | `/TMD/TMD60_3/47_3M.TMD` |  |
| 28106 | 34120 | `/TMD/TMD60_3/48_3M.TMD` |  |
| 28123 | 36352 | `/TMD/TMD60_3/49_3M.TMD` |  |
| 28141 | 35344 | `/TMD/TMD60_3/50_3M.TMD` |  |
| 28159 | 34912 | `/TMD/TMD60_3/51_3M.TMD` |  |
| 28177 | 34888 | `/TMD/TMD60_3/52_3M.TMD` |  |
| 28195 | 34552 | `/TMD/TMD60_3/53_3M.TMD` |  |
| 28212 | 34864 | `/TMD/TMD60_3/54_3M.TMD` |  |
| 28230 | 35288 | `/TMD/TMD60_3/55_3M.TMD` |  |
| 28248 | 35472 | `/TMD/TMD60_3/56_3M.TMD` |  |
| 28266 | 35632 | `/TMD/TMD60_3/57_3M.TMD` |  |
| 28284 | 35800 | `/TMD/TMD60_3/58_3M.TMD` |  |
| 28302 | 35208 | `/TMD/TMD60_3/59_3M.TMD` |  |
| 28320 | 35768 | `/TMD/TMD60_3/60_3M.TMD` |  |
| 28339 | 35072 | `/TMD/TMD60_4/31_4M.TMD` |  |
| 28357 | 34912 | `/TMD/TMD60_4/32_4M.TMD` |  |
| 28375 | 36536 | `/TMD/TMD60_4/33_4M.TMD` |  |
| 28393 | 36608 | `/TMD/TMD60_4/34_4M.TMD` |  |
| 28411 | 34864 | `/TMD/TMD60_4/35_4M.TMD` |  |
| 28429 | 35216 | `/TMD/TMD60_4/36_4M.TMD` |  |
| 28447 | 35008 | `/TMD/TMD60_4/37_4M.TMD` |  |
| 28465 | 34808 | `/TMD/TMD60_4/38_4M.TMD` |  |
| 28482 | 34776 | `/TMD/TMD60_4/39_4M.TMD` |  |
| 28499 | 36696 | `/TMD/TMD60_4/40_4M.TMD` |  |
| 28517 | 34728 | `/TMD/TMD60_4/41_4M.TMD` |  |
| 28534 | 34232 | `/TMD/TMD60_4/42_4M.TMD` |  |
| 28551 | 34976 | `/TMD/TMD60_4/43_4M.TMD` |  |
| 28569 | 35640 | `/TMD/TMD60_4/44_4M.TMD` |  |
| 28587 | 35112 | `/TMD/TMD60_4/45_4M.TMD` |  |
| 28605 | 34656 | `/TMD/TMD60_4/46_4M.TMD` |  |
| 28622 | 35360 | `/TMD/TMD60_4/47_4M.TMD` |  |
| 28640 | 34120 | `/TMD/TMD60_4/48_4M.TMD` |  |
| 28657 | 36352 | `/TMD/TMD60_4/49_4M.TMD` |  |
| 28675 | 35344 | `/TMD/TMD60_4/50_4M.TMD` |  |
| 28693 | 34912 | `/TMD/TMD60_4/51_4M.TMD` |  |
| 28711 | 34888 | `/TMD/TMD60_4/52_4M.TMD` |  |
| 28729 | 34552 | `/TMD/TMD60_4/53_4M.TMD` |  |
| 28746 | 34864 | `/TMD/TMD60_4/54_4M.TMD` |  |
| 28764 | 35288 | `/TMD/TMD60_4/55_4M.TMD` |  |
| 28782 | 35472 | `/TMD/TMD60_4/56_4M.TMD` |  |
| 28800 | 35632 | `/TMD/TMD60_4/57_4M.TMD` |  |
| 28818 | 35800 | `/TMD/TMD60_4/58_4M.TMD` |  |
| 28836 | 35208 | `/TMD/TMD60_4/59_4M.TMD` |  |
| 28854 | 35768 | `/TMD/TMD60_4/60_4M.TMD` |  |
| 28873 | 3127296 | `/MOV/ASLOGO15.STR` |  |
| 30400 | 11685888 | `/MOV/VPW10SON.STR` |  |
| 36106 | 11216896 | `/MOV/VPW12OUT.STR` |  |
| 41583 | 11216896 | `/MOV/VPW12SON.STR` |  |
| 47060 | 33922048 | `/MOV/4BGM06.DA` |  |
| 63925 | 30812160 | `/VPW_DA/OPEN.DA` | zero padding |
| 79120 | 11171840 | `/VPW_DA/6BGM02.DA` | zero padding |
| 84725 | 931840 | `/VPW_DA/2BGM13.DA` | zero padding |
| 85330 | 29538304 | `/VPW_DA/4BGM06.DA` | zero padding |
| 99903 | 30812160 | `/VPW_DA/SINNNICH.DA` | zero padding |
| 115098 | 11280384 | `/VPW_DA/3ENDING.DA` | zero padding |
| 120756 | 10971136 | `/VPW_DA/2BGM11.DA` | zero padding |
| 126263 | 29872128 | `/VPW_DA/1BGM04.DA` | zero padding |
| 140999 | 28850176 | `/VPW_DA/2BGM05.DA` | zero padding |
| 155236 | 1740800 | `/VPW_DA/2BGM14.DA` | zero padding |
| 156236 | 11245568 | `/VPW_DA/3BGM02.DA` | zero padding |
| 161877 | 29857792 | `/VPW_DA/3BGM10.DA` | zero padding |
| 176606 | 29134848 | `/VPW_DA/4BGM09.DA` | zero padding |
| 190982 | 30052352 | `/VPW_DA/5BGM08.DA` | zero padding |
| 205806 | 30128128 | `/VPW_DA/5BGM10.DA` | zero padding |
| 220667 | 28633088 | `/VPW_DA/BGM07.DA` | zero padding |
| 234798 | 30812160 | `/VPW_DA/OPENING.DA` | zero padding |

## Executable and memory

## Archives and compression

## Text
How text is drawn: does the game draw ASCII? fixed or proportional width? which glyphs exist? how
much of the visible text is images? *(answer these first)*

## Images

## Open questions
-

## Prior art
- No English patch for the PlayStation original (SLPS-00449) found (2026-11-04); the only fan patch seen is for the N64 sequel, Virtual Pro Wrestling 2.
- The Western release, WCW vs. the World (1997, same developer AKI), shares the engine; its English text and assets may help as a reference.

## Where the text is (survey 2026-11-04, from the code/scans; not yet verified in game)
- Disc: SLPS_004.49 (boot), MAIN.EXE (loads the others: RESULT, SHINKOU, STAFF, MOV), overlays
  SHINKOU.EXE/BIN (menus, modes, memory card, belts), RESULT.EXE/BIN, STAFF.EXE/BIN (credits - kept),
  MOV.EXE; DAT/ TEX/ TMD/ (30 numbered files each: wrestler data/textures/models), RING/ (rings).
- Shift-JIS text lives in the overlay EXEs as fixed 32-byte lines (16 full-width characters, padded
  with U+3000): SHINKOU.EXE ~0x800-0x4a000 (messages, memory card prompts, belt/title-match text),
  RESULT.EXE 0x8a0-0x34c00 (match-result prompts, "X wins" lines with the fictional wrestlers' names),
  MAIN.EXE and the others hardly any. SHINKOU.EXE 0x46b4c holds a JIS-order kanji chart (a
  code-to-glyph table or name-entry grid): how SJIS is drawn is still to find (font TIM + renderer).
- Most menu and HUD text is images: 8bpp/4bpp TIM atlases inside SHINKOU.BIN (142 TIMs: title,
  menu word atlases, wrestler-name atlases, 90x74 face portraits), RESULT.BIN (5), T0623.DAT (8: ring
  announcements/"TKO!" banners, number fonts, a calligraphy win-text sheet), STAFF.BIN (22). Wrestler names
  are drawn from katakana name atlases, so the real/parody name variants mean redrawn atlases too.
- Wrestlers are fictional (parody) in this game; WCW vs. the World (SLUS-00???) carries the real names.

## WCW vs. the World as a reference (SLUS-00455; extracted to build/work/wcw/, from the code)
- Same engine and file layout (SHINKOU/RESULT/STAFF/MAIN/MOV .EXE+.BIN, DAT/TEX/TMD/RING). KS0704.BIN,
  D0617.DAT and T0623.DAT are byte-identical to the Japanese disc, so WCW did not touch them.
- The overlay messages are English in the same 32-byte slots (SHINKOU.EXE 0x800.., e.g. "Select Save position",
  "Memory Card in Slot 1 not formatted  Format?"), so the JP lines map one-to-one onto WCW's English: a first
  draft for those lines. The code differs only by address shifts.

## Text renderer (SHINKOU.EXE, JP; from the code, not yet seen running)
- A PsyQ-style FntPrint ("%s" at 0x8005c888 fills a stream) and a custom FntFlush at 0x8005c4f0 draw each
  line: cell advance 0x10, bytes 0x81-0x98 lead a two-byte Shift-JIS char (level-1 JIS only), 0x20-0x7e go through
  the glyph function 0x8005be2c -> 0x8005d2bc (ASCII mapping) -> 0x8005cd48 (code to glyph index). A glyph is
  30 bytes (1bpp 16x15-ish bitmap) copied into a buffer at 0x8007efcc + n*32 and uploaded to VRAM; the glyph base
  comes from 0x8005cc88, a stub that jumps through the BIOS vector table (t2=0xb0, t1=0x51). US code has the
  identical functions (0x8005c008, 0x8005ce84), so English goes through the same path - what that stub returns
  and where the glyph bitmaps live is the open question. The BIOS kanji-ROM theory fits (30-byte glyphs) but
  needs checking in an emulator/debugger before building on it.

### Glyph source: the BIOS font ROM (verified in game, DuckStation GDB, 2026-11-04)
- On the memory-card/save screen in DuckStation, a write watch on the glyph buffer (0x8007efd0) stopped inside
  the BIOS (pc 0xbfc01aa8, its memcpy) copying 25-30 bytes from a0=0xbfc689bd to the buffer at 0x8007efcc +
  n*32: the source is the BIOS ROM font (base 0xbfc66000, returned by the stub at 0x8005cc88; the glyph for
  SJIS 0x8381 was being fetched). So the Japanese text is drawn with the console BIOS's built-in kanji ROM,
  30 bytes per 1bpp glyph; the game has no font of its own (the contact-sheet TIMs hold only word pictures).
- SHINKOU.EXE was the resident overlay (0x8001d000; its message lines start at 0x8001d024 = file 0x824).
  Breaking on the stub itself did not fire while the screen was static: glyphs are cached per line.
- Consequence: English drawn through this path would use the ROM's glyphs (full-width Latin 0x8260.. exists in
  the JP ROM; whether the ROM has a half-width ASCII set the code can use, and how WCW's identical code gets
  English through the US BIOS, is still to check). A patch that must not depend on the player's BIOS needs its
  own font and a hook in the glyph function 0x8005be2c.

### What WCW redrew (TIM compare by checksum, 2026-11-04; from the files)
- Same image sizes and positions as the Japanese atlases, so English fits the same slots: SHINKOU.BIN images 0-7
  (title and the menu word atlases: modes, options, rules, numbers, the name atlases), many portraits and others
  (JP 142 TIMs, US 144; 57 identical); RESULT.BIN 0-2,4; STAFF.BIN 0-14,21 (credits: kept); T0623.DAT 4-7 (the TKO /
  rope-break banners, number fonts, the win-text calligraphy sheet).
- The wrestler-name atlases (SHINKOU.BIN 4, 7 and the 6th atlas) carry the same grid in both discs: WCW has the real
  names (HOGAN, SAMOA, PUCHTECA, ...) in the same slots as the Japanese parody names (ガイア, 番場, ...). This is the
  basis for the two name patches: parody names = our own redraw of the Japanese roster in English, real names = the
  WCW roster order as a guide. Redraw the art ourselves (don't ship WCW's pixels in a patch).
- ASCII is drawn through the same ROM-glyph code as Japanese: 0x20-0x7e map to full-width SJIS codes (table at
  0x8006d600 in SHINKOU.EXE) then to ROM glyphs. A 32-byte line is therefore 32 cells; box width decides wrapping.
  How wide a Latin glyph really is on screen is unconfirmed (needs a look at WCW or a patched build).

### Roster: WCW is not a 1:1 copy (portrait check, 2026-11-04; from the files)
- SHINKOU.BIN has 74 face portraits (90x74) in each disc. 57 are byte-identical across the two (same face art),
  but only 30 of those sit at the same index: the order differs. 17 JP portraits have no US twin and 17 US
  portraits are new (replacement wrestlers). JP-only indices: 2 7 10 18 25 29 30 40 43 45 46 47 49 50 51 55 60;
  US-only: 1-13 (part) 26 56 58 60. So name sheet slot n does NOT equal the same wrestler in WCW.
- Rule for names: match by identity (portrait hash, then in-game check), never by position. WCW's English is a
  reference for the 57 matched faces only; the other 17 get names from us.

### Menus (headless run, 2026-11-04; seen headless)
- tools/emu.py boots both discs to the mode menu: `wait 1500`, `mash START 700`, `wait 300`, `shot a` (the title
  needs ~2500 frames from power-on; pressing too early does nothing). The Japanese mode menu (モード選択: 公式戦,
  炎の七番勝負, エキシビション戦, イリミネーション戦, トーナメント戦, リーグ戦, ダブルタイトル戦) is the same screen
  as WCW's Select Mode (League Challenge, Best of Seven, Exhibition Match, Elimination Match, Tournament, League
  Match, Double Title Match): the words are pictures from the SHINKOU.BIN atlases, so menus are image work, no
  renderer needed. Button legend (決定 取消 説明 = Select Cancel Help) is picture too.
- tools/gfx.py: export/import of the TIM pictures in SHINKOU.BIN, RESULT.BIN, T0623.DAT, STAFF.BIN as indexed
  PNGs (ids SHINKOU_003 ...; CLUT 0 shown, only pixel indices are edited, so atlases with several CLUTs keep
  theirs). Round trip of all 177 images is byte-identical (proved 2026-11-04).

### Menu labels are fixed-width sprites (verified headless, 2026-11-04)
- SHINKOU_002 (256x256, 16-px bands) feeds the mode menu: blanking the 公式戦 label in a test build blanked the first
  mode button. Each label is a sprite with its own width (41 px for 公式戦 ... 128 px for ゲーム設定); the button
  around it is drawn separately, so English must fit the label's width (about 5 px per character at 11 px caps,
  squeezed to ~0.64) or the sprite table must be patched (not done). Elimination is two sprites (イリミネ + ーション戦).
- tools: translation/letters/SHINKOU_002.json holds the English and boxes; private/work/img/menu_labels.py draws them in
  palette-index space (button rebuilt from the blank bar, white fill, dark outline). The kit's render/letter tools
  produced too-small text on these textured buttons.

### Label sprite records (SHINKOU.EXE; from the code + RAM dump, 2026-11-04)
- The label sprites are prebuilt GPU sprite packets in SHINKOU.EXE data (20 bytes each, 4-byte aligned): `u v clut(2)
  xx 78 65 00 w(2) h(2)` - u,v = position in the 256x256 atlas (SHINKOU_002), w,h = size in px (h always 16). Each label
  is drawn together with a 128x16 background bar sprite (u0 v0 w128, the blank bar at the atlas top-left), so a label can
  be at most 128 px wide. In RAM the packet is a normal SPRT (0x64/0x65): found with a RAM dump from tools/emu.py.
- 25 label records are in one table around 0x8005d8d4 / 0x8005ec58 / 0x8005f0d0 / 0x8005f198 (file = addr - 0x8001d000 +
  0x800): the mode menu (公式戦 208,0,41; 炎の七番勝負 144,16,78; エキシビション 0,32,100; イリミネ 208,64,48 +
  ーション戦 192,96,64; トーナメント 128,32,90; リーグ戦 0,48,53; ダブルタイトル 56,48,106), 1P vs 2P/COM, 勝ち抜き, 対抗戦,
  the organisation names, ロード, セーブ, ベルトレコード, ゲーム設定, 終了. Exact widths are one px off my run estimates.
  Stereo/Mono, the rule and time labels and the memory-card labels were not found in this format (other tables).
- WCW has the same record format with different rects (e.g. League Challenge 128,0,96; Best of Seven 0,16,72; Exhibition
  Match 72,16,90; Elimination Match 0,32,96), re-ordered, so its layout is a proven packing of wider English labels, but
  records can't be copied one to one (order and cluts differ).
- Widening the English labels therefore means: new rects for these records + a repacked atlas image drawn to match.

### Label records: layout and patch (done for 21 labels; mode menu seen headless 2026-11-04)
- Record layout (from the code): `u v x_field 0x78 | .. 0x78 0x65 0 | w(2) h(2) | ...`; on-screen x = x_field + 32 (the game
  does NOT re-centre when w changes: the first test widened a label to 80 px and it stayed left-anchored). Labels are centred on
  the 128-px button, so x_field = centre - w/2 - 32. The two halves of Elimination are placed side by side (second x = first x + first w).
- private/work/img/label_layout.py measures the English, packs the 21 moved labels into the atlas' free space, redraws
  translation/images-handmade/SHINKOU_002.png and writes translation/label_records.json; build.py turns that file into CODE_PATCHES
  (group 'labels', always on; SHINKOU.EXE, address -> offset = addr - 0x8001d000 + 0x800). Kept as they are: the English 1P vs 2P, 1P vs COM,
  SUPER HEAVY, SUPER Jr. records and the non-record labels (Stereo/Mono, rule/time/memory card, Yes/No), whose tables are not found yet.
- Seen headless: the mode menu now reads Official Match / Seven-Bout Blaze / Exhibition Match / Elimination Match / Tournament /
  League Match / Double Title Match, all centred. Not yet seen: Load/Save, Game Settings, Belt Record, End, the organisation names,
  Winner Stays, Team Match (other screens).

### Label backgrounds: use the bar's own pixels (2026-11-04, after the first owner screenshots)
- Each label record is followed by a background-bar record (u0 v0 w128, x = 96 on screen; option rows use a 64-px bar at 0,192).
  The Japanese label's background equals the bar's pixels at the same on-screen offset (verified by pixel match for 12 labels,
  offset = label x - bar x). The first English build tiled its own background, which showed as seams and end caps on the buttons
  (options screen). label_layout.py now copies the bar's pixels at the label's offset, so the label is invisible against the button.
- 58 label records found (49 distinct rects, 14 with a normal/selected copy); the copies are all patched. Yes/No and Stereo/Mono
  have no record in this format yet (drawn on the assumption they are centred on the bar). Game Settings (0,224,128) is a full-width
  label with no bar pair and stays at 128 px.

### Label font (2026-11-04, after owner feedback: M in "Match" smashed)
- The first lettering (Barlow Condensed Bold drawn large, squeezed down and thresholded) fused narrow letters. Now each
  letter is drawn 1-bit at its real pixel size from Ubuntu Sans, instance "Condensed ExtraBold" (tools/fonts/UbuntuSans-wdth-wght.ttf,
  variable font, Ubuntu Font License - note the licence file before a public release), and placed with an even 1 px gap
  (3 px between words): letters stay open, the M reads at cap heights 8-10. Compared in a sheet against DejaVu Sans Bold, Ubuntu Sans
  Bold, Barlow Condensed (SemiBold/ExtraBold): DejaVu was clear but too wide, Barlow thin.
- To fit, some English was shortened toward WCW's wording: Neo Strong (WCW: Neo Strong), Empire Pro, Rules (WCW: Match Options),
  Bet a New Belt (WCW: Bet a New Belt), Bet a Saved Belt. Tiny labels (30/60 Min, 1 Fall, 3 Falls, Unlimited, 8-9 px caps) stay
  small because their sprite slots are 23-41 px wide; widening them needs their option-row layout checked.
- Letter heights (owner: t and h of "Match" sat high): each glyph is now drawn on one shared baseline (anchor 'ls'), not placed by its
  bounding box (hinted boxes round differently per letter), and the ascenders b d f h k l t are trimmed to the capital height (this font's
  ascenders stand 1-2 px above the caps). Lettering sits on one line and one cap height.
- Real cause of the "high" letters (found from the glyph rasters, 2026-11-04): this variable font's hinting leaves the bottoms of
  d, h, b, t (and k) one row above the baseline at sizes 14-15, so those letters floated a pixel; the earlier fixes (shared baseline,
  ascender trim) did not touch that. label_layout.py now shifts every letter and digit down to the baseline (descenders g j p q y
  excepted, punctuation left alone), trims ascenders b d f h k l to the cap height and stretches t to it.

### SHINKOU_003 / SHINKOU_006 labels (2026-11-04)
- SHINKOU_003 (screen headers, rule/option labels, button legend) and SHINKOU_006 (Game Settings screen) are not drawn by the
  20-byte label records of SHINKOU_002 (checked: every record in SHINKOU.EXE is in the 002 atlas); no table for them was found, so
  the English is drawn in place inside each Japanese label's pixel extents (private/work/img/atlas003.py, atlas006.py; shared
  lettering in private/work/img/lettering.py). Seen headless: Mode Select header and the Select/Cancel/Help legend (mode menu).
- Styles (from the pixel indices): header bars bg 7 / outline 6 / fill 2,0,0,0,3,3; cream option labels bg 13, outline rings 6 then 7;
  legend text is 1-px strokes of index 12 (dark on the cream box in game; CLUT 0 shows it grey). Band 0 of 003 = legend (決定 取消 説明
  入力 見る 飛ばす 交換); band 16 has スロット / 情報 and the 制限時間 / 勝負本数 labels.
- 006 value labels (Mono/Stereo, Easy/Normal/Hard) sit on 64-px textured bars: the old text is painted over with each row's dominant bar
  colour, then the English is drawn. Not seen in game yet.
- Text: the overlay strings are 32-byte Shift-JIS lines (16 full-width chars) in SHINKOU.EXE (0x800..0x2100 messages: memory card,
  belts, Yes/No prompts; 0x457f4.. mode descriptions), RESULT.EXE (176 runs) and the BIN data; MAIN.EXE has none. English needs a
  narrower font path (not done).

### Rule Settings field-name records (2026-11-04, *from the code*, checked headless)
The six field names of SHINKOU_003 (Mat Select, Time Limit, Falls, Ringout Count, Rope Break, TKO) are 24-byte records in SHINKOU.EXE at 0x8005fa34 + 0x18*n: `u v x y | clut(4) | w(2) h(2) | ...`, u/v = atlas position, w = width (byte +8). The label is drawn left-aligned at a fixed x; changing w widens it to the right with no re-centring. The other SHINKOU_003 headers have 24-byte records too (0x8005dacc, 0x8005ec40 ...).

## English text path: two letters per cell (2026-11-04; seen headless in the mode/options help boxes, *not yet verified by the owner*)
- Problem: the renderer draws every character in a 16-px cell from the BIOS ROM font, and ASCII goes through the full-width
  glyphs, so English would get 16 letters per line instead of 32.
- Fix (translation/text_hook.json, written by private/work/text/hook.py, applied as group `texthook`, in SHINKOU.EXE and
  RESULT.EXE): the glyph function's ASCII path jumps to HOOK, which builds ONE 16x15 glyph from two bytes of the string
  (left 8 columns = first letter, right 8 = second) out of an 8x15 font (DejaVu Sans Mono 13, baseline row 12; 1425 bytes)
  and joins the original code after the ROM-glyph copy. A wrapper (WRAP) around the glyph call advances the string pointer by
  one extra byte when the second byte is printable ASCII (0x20-0x7e); a space now starts a pair too (the flush's
  "space = skip" branch was retargeted to the glyph call). Kanji and full-width characters (○ ×) are untouched.
- Code and font live in an unused function (no callers or references): SHINKOU.EXE 0x8005b6fc-0x8005c1bc (an older copy of
  the flush), RESULT.EXE 0x80047848 (+1808 bytes). The zero runs in the files are NOT free: they are written at run time.
- R3000 load delay: a loaded byte can't be used by the next instruction (this cost a debugging round: the second letter
  of every pair came out blank).
- Text format: `translation/text/shinkou.txt`, `result.txt`: one block per message, meta `FILE FILE-OFFSET LINES`, line i at
  offset + 0x21*i, 32 bytes each, English padded with spaces to 32 bytes (build.py messages_step). Limit: 32 characters
  per line, as many lines as the Japanese had. Written with private/work/text/setten.py from private/work/text/en_*.tsv.
- Not translated yet: the RESULT "「レスラー０」" prompts (digit patched into the string by code at 0x8002ca30), the
  winner lines "「name」の優勝です" (need the wrestler names), the belt-holder counter lines "第　代" (number drawn over the
  gap; English "# ... Champion" is a guess), the kana grid of the name entry, and the 8-byte "初代" line.
- Box widths (verified in game): the help box on the entrants screen is 12 cells wide: messages whose Japanese lines are <= 12 characters need <= 22 English letters per line; the wide boxes take 32.

## Moves and the bio-box star (from the code / from the data; details in private/work/moves_notes.md)
- The star on the select-screen bio box is only part of the picture; no data or code marks a "star" move.
- DAnn.DAT (DAT/D30, D60) is the wrestler of bio box nn (SHINKOU_068+nn; Benoit = DA02). Layout: 42 action records of 13 bytes at 0x000 (records 38/39 = the 6 offence + 6 defence stats), 102 animation headers of 32 bytes at 0x224, data offsets at 0xEE4. P1 file loads at 0x80142000, P2 at 0x801A1000.
- Hit routine MAIN.EXE 0x8002DB98: record byte [0] = power P, [5]/[6] = attacker/defender spirit change, [7]/[8] stat picks, [9] body-part wear.
- Diving Headbutt = record 34 (*seen in frames*, 2026-11-05; an earlier note wrongly said record 41): the corner top-rope attack on a LYING opponent (record 35 = on a standing one; P=18 / 12, same numbers for every wrestler who has the slot). To trigger it the wrestler touches the ropes within 17 units of a corner, then holds the diagonal toward it plus Cross. No spirit check, no extra damage. Records 40 and 41 are not corner attacks: 40 = running dive through the ropes (Triangle + direction, then Circle held), 41 = spring off the ropes onto an opponent on the floor; both need the opponent outside the ring and a wrestler whose DA record 38/39 dive flag is set (40 of 60 have none; the flag, not the weight class, decides: Fujinami, Misawa, Muta and Sting have both).
- The real finisher is the SPECIAL move: spirit >= 100 sets flag 0x200 (+0x200) for a 30 s clock (MAIN 0x8003B608, then spirit resets to 50); in SPECIAL hold Circle until the hold counter (+0x234) reaches 31, release = record 13 (P=30 for 54 of 60 wrestlers). Spirit loss and the KO roll are skipped during SPECIAL. Per-wrestler identity of record 13 and repeatability within the 30 s: not checked (guess).
- Action record byte [11] is the move type (from the data/code): 0 plain hit, 1 hit that sets defender flag 0x800 (KO check), 2 throw (sets victim +0x250 bit 0x20), 3 hold/submission (give-up check, no count), 4/5 hold variants. No move names exist in the data or code.
- A type-2 action whose animation has a throw number n (header +0x1C, nonzero; true for all 149 type-2 records) puts victim/attacker into pin states 0x25/0x24 with a referee count: the throw itself pins. Pressing the pin button on a downed opponent (states 0x19/0x1A) is a separate path. Kickout timer T = pinner spirit/4 + 110 - victim HP (min -100) - victim spirit, capped at 80 if victim spirit >= 90, minus 1/tick and 1 per 3 presses; pinfall at count 3. Owner play-tested Benoit: records 11 (type 0) no pin, 12 and 13 (type 2) pin (verified in game, 2026-11-05).
- Grapple selector (from the code, MAIN 0x80032BF0-0x800332C8; *verified in game* for Benoit, debugger log 2026-11-05): only pad Up (0x1000) and Down (0x4000) are read; Left/Right act as no direction. Circle tap (<15 counter) vs hold. Close tap (distance +0x14 < 0x74, flag 0x800) none/up/down = records 7/8/9 (Benoit: Gut Wrench, Suplex, Tombstone Piledriver), each with a follow-up 14/15/16; tap from further away = 4/5/6 (Elbow to the Back of the Head, Snapmare, Body Slam); close hold = 10/11/12 (Butterfly DDT, Snap Suplex, Powerbomb + pin); behind: tap 17 / 18, hold 19 / 20; max-spirit hold = 13. Records 12 and 13 are type 2 (pin), the rest type 0. Full per-wrestler table: private/work/moves_table.tsv.
- Records 14/15/16 are the DEFENDER's counter to a close tap (7/8/9) or a tap from behind, played through the attacker's struct (*verified in game*, forced with the debugger: close tap + Down, the opponent reversed into a small package and pinned Benoit). The victim must press a face button within 3 frames of the grab, spirit >= 36, chance = spirit %. P=0. If the counter animation has a throw number (record 16 is type 2 for 23 of 60 wrestlers, incl. Benoit) the attacker goes to the pinned state 0x25 and the defender to the pinner state 0x24 with a referee count; without a throw number it is just a counter. Holds and far taps can't be countered. Whether the COM does this unforced was not seen.

### Round 14 findings (owner screenshots 2026-11-06; checked headless with tools/emu.py, 2026-11-06)
- **Screen headers are separate sprites** (*seen in a RAM dump of the One Night Tournament screen*): ワンナイト = atlas SHINKOU_003 (0,160) w72 at screen x80; トーナメント = (48,144) w88 at screen x152; リーグ = (0,144) w48; ベルト争奪 = (90,128). One English run 'League Tournament' over 0-134 was therefore cut mid-word on screen ('Belt Contest e Tournament', 'Leagu'). Draw each word inside its own sprite rect.
- **第 / 最終 / 戦** (match number 第N戦 and 最終戦) are three 24x24 cells at (160|184|208|232, 192) of SHINKOU_003/RESULT_000 with bg index 15; 戦 is shared by both phrases, so the English is 'No.' + digit + 'Bout' and 'Final' + 'Bout' (*from the pixels; seen only as the atlas, not in game*).
- **SHINKOU_005** (CLUT rows 3/11 are the gold and orange ones): the Elimination order chips 先鋒 次鋒 中堅 副将 大将 are 32x16 at (64+32i, 40) with a shaded plate (rows: rim, then indices 2/3, bottom rim 6/9) and cream text with dark ring; 選び直し is the 48x16 chip at (208,56); 優 / 勝 are two 30x30 glyphs at (2,40) and (33,40) (index 14 = outline, 15 = transparent, fill gradient 0 1 2 3 4 6). A tiny '制!' decoration at (97-130, 57-66) was left alone.
- **SHINKOU_007** is the 60-name list drawn on the belt chips (Belt Input / Belt Record): 4 columns x 16 rows of 48x16 cells in the game's own katakana names, same order as the select tiles (SHINKOU_004). Bg index 7, ring 6, fill 0. Real names: private/work/img/atlas007.py; parody variant: `VPW_NAMES=parody` (translation/images-parody).
- **T0623_007 headline phrases**: background index 15 and outline index 14 are the game's transparent / outline entries; fill 1. Painting the box with index 7 (transparent in the file's CLUT 0) showed as an opaque yellow box in game, so use the original's own indices, never 'what the exported PNG shows transparent'.
- **T0623_004 time digits**: the 分 / 秒 cells (x161-191, y161-175 shaded set; x224-255, y238-255 thin set) became ':' and blank.
- **Finish-name plate (Pin Fall, Ring Out, Time Up Draw ...)**: the black plate is index 15 of CLUT 0 (0x8000), but patching CLUT 0 entry 15 had no effect in game while entry 6 did (then the plate showed as an opaque light grey box, i.e. the game draws something under the plate). The plate was left black as in the original; making it vanish needs the drawing code (not found).
- **Pause buttons** (T0623_005 at (64..213, 160..191)): the plate is a shaded gradient (index 1-4 per row) between rim columns; a flat index 10 showed as grey in game. Redrawn from the original's own gradient (private/work/img/t0623_005.py `button`). Seen headless: Resume / Skip Match.
- Headless route to these screens: private/work/nav_tournament.steps + extra presses (see build/work/nt*.steps recipe in playtest.md round 14): Tournament -> entrants -> No Belt Bet -> two picks -> bracket; CIRCLE starts the match; START pauses; DOWN + CIRCLE = Skip Match -> result screen.
- **Maeda's champion line (fixed 2026-11-06, *seen headless* with the owner's savestate `screenshots/akira-champion.sav`)**: the missing first kanji of his parody name (薫) is a 16x16 glyph stored in the RESULT_001 atlas at (240,16) (x241-253, y16-29, index 0 strokes on 15). RESULT.EXE draws it as a separate sprite (screen x64 y184, u240 v16, tpage 0x21d = VRAM (832,256), CLUT (304,490)) over cell 2 of the line whatever the text says; the Japanese line has a plain space there. Blanking the block in RESULT_001 removes it. DuckStation `.sav` layout: zstd frame 2 = RAM at +0x1a62 (2 MB), VRAM (1024x512x16) at +0x201ddb (found by the CLUT pattern); primitives are in RAM (SPRT 0x64 preceded by an e1 draw-mode word that gives the tpage).
- **T0623_006 (traced 2026-11-06)**: TIM 6 of T0623.DAT (256x120, VRAM 576,384, tpage 0x19, v 128-247), loaded by MAIN.EXE. Row 5 'Now Loading...' is the match loading strip (sprite set up at MAIN 0x80022ca8: x-24 y72 160x24, v224, CLUT (32,493)) and is already English. Rows 1-4 (promotion tags, 'ILW 無惨! KO負け!', 'Super HEAVY vs', '熱戦に終止符! KO負け!') are drawn by an index-driven routine around MAIN 0x8002a6d0-0x8002abc8 (uses rand, a width/tpage table at 0x8001d528 and v 152/176/200), next to leftover debug strings ('pat1 = %d'). Never seen running; rows 2 and 4 were translated as insurance (private/work/img/t0623_006.py).

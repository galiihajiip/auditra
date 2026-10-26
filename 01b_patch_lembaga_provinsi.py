"""
Auditra - Patch: Hapus baris dengan lembaga = nama provinsi murni
Data quality issue dari SIRUP: sebagian baris kolom 'lembaga' keisi nama
provinsi polos (bukan nama instansi), sehingga mencemari dropdown filter
'Lembaga' di dashboard dengan entri yang seharusnya cuma ada di filter
'Provinsi'.

Jalankan SETELAH 01_cleaning.py tapi SEBELUM 02_scoring.py jika kamu sudah
punya data_clean.csv dari run sebelumnya dan tidak mau cleaning ulang dari awal.

Bisa juga dijalankan di tahap manapun (data_scored.csv, data_network.csv)
karena hanya filter baris, tidak mengubah kolom.
"""


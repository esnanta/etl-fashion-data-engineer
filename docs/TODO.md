1. **Penyempurnaan Storage.py:**
   - Implementasi: Kompresi Parquet, checksum, metadata, versioning.
   - Tambahkan dukungan backend: S3, GCS, MinIO.
   - Buat custom exception.

2. **Jadikan CSV sebagai Artefak Berversi:**
   - **Masalah:** `save_to_csv` saat ini menimpa output (misal: `products.csv`).
   - **Solusi:** Ubah `save_to_csv` untuk menyimpan output ke path unik dengan timestamp (contoh: `.../products_YYYYMMDDTHHMMSSZ.csv`) untuk mencegah data hilang.

3. **Validation.py:**
   - *Business Validation* (misalnya: title tidak boleh kosong, price harus numerik) akan diimplementasikan di tahap selanjutnya.
from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

try:
    csv_path = os.path.join(os.path.dirname(__file__), 'data_balita.csv')
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
except Exception as e:
    print(f"Gagal memuat CSV: {e}")

def modus_ponens_logic(gender, umur, tinggi):
  
    gender_map = {'male': 'laki-laki', 'female': 'perempuan'}
    g_fakta = gender_map.get(gender, gender).lower()

    # Cari data CSV
    match = df[(df['Jenis Kelamin'].str.lower() == g_fakta) & 
               (df['Umur (bulan)'] == umur) & 
               (df['Tinggi Badan (cm)'] == tinggi)]
    
    if not match.empty:
        return match.iloc[0]['Status Gizi']
    
    # Cari yang terdekat
    sub_df = df[(df['Jenis Kelamin'].str.lower() == g_fakta) & (df['Umur (bulan)'] == umur)]
    if not sub_df.empty:
        idx = (sub_df['Tinggi Badan (cm)'] - tinggi).abs().idxmin()
        return sub_df.loc[idx, 'Status Gizi']
    
    return "Data Tidak Ditemukan"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/deteksi', methods=['POST'])
def deteksi():
    try:
        data = request.json
        hasil = modus_ponens_logic(data['gender'], int(data['umur']), float(data['tinggi']))
    
        status_cek = hasil.strip()

        if status_cek == "normal":
            saran = "Kondisi anak baik, pertahankan pola makan seimbang."
        elif status_cek == "stunted":
            saran = "Anak terindikasi pendek. Tingkatkan asupan gizi yang lebih baik."
        elif status_cek == "severely stunted":
            saran = "Anak sangat pendek. Segera konsultasikan ke dokter spesialis anak."
        elif status_cek == "tinggi":
            saran = "Pertumbuhan anak sangat baik."
        else:
            saran = "Lakukan pemeriksaan rutin di Posyandu terdekat."
        
        return jsonify({
            'status': hasil,
            'saran': saran
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
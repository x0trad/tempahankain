// Johor ADUN DUN Boundaries (56 kawasan)
// Represented as approximate polygon coordinates on Leaflet map
// Coordinates approximate for visualization purposes
// Sumber: Suruhanjaya Pilihan Raya Malaysia (SPR)
const JOHOR_CENTER = [1.95, 103.35];
const JOHOR_ZOOM = 9;

const JOHOR_ADUN = [
  // KOTA TINGGI - 4 ADUN
  { id: "n01", name: "Pengerang", parlimen: "P.156 Kota Tinggi", color: "#4CAF50", state: "Johor", coords: [[1.38,104.18],[1.38,104.32],[1.32,104.35],[1.28,104.35],[1.22,104.28],[1.22,104.18],[1.26,104.12],[1.32,104.12]] },
  { id: "n02", name: "Tanjung Surat", parlimen: "P.157 Kota Tinggi", color: "#66BB6A", state: "Johor", coords: [[1.42,104.08],[1.44,104.22],[1.38,104.28],[1.32,104.26],[1.32,104.18],[1.36,104.12]] },
  { id: "n03", name: "Tiwram Island", parlimen: "P.157 Kota Tinggi", color: "#81C784", state: "Johor", coords: [[1.48,104.02],[1.50,104.14],[1.44,104.16],[1.42,104.08],[1.44,104.00]] },
  { id: "n04", name: "Tenggara", parlimen: "P.158 Kota Tinggi", color: "#A5D6A7", state: "Johor", coords: [[1.52,103.96],[1.54,104.08],[1.48,104.10],[1.46,104.02],[1.48,103.94]] },

  // JOHOR BAHRU - 8 ADUN
  { id: "n05", name: "Johor Jaya", parlimen: "P.159 Johor Bahru", color: "#2196F3", state: "Johor", coords: [[1.54,103.86],[1.56,103.94],[1.52,103.98],[1.48,103.96],[1.48,103.88],[1.50,103.84]] },
  { id: "n06", name: "Permas", parlimen: "P.159 Johor Bahru", color: "#42A5F5", state: "Johor", coords: [[1.48,103.84],[1.50,103.92],[1.44,103.94],[1.42,103.88],[1.44,103.82]] },
  { id: "n07", name: "Larkin", parlimen: "P.160 Johor Bahru", color: "#64B5F6", state: "Johor", coords: [[1.50,103.78],[1.52,103.84],[1.48,103.86],[1.46,103.84],[1.46,103.78]] },
  { id: "n08", name: "Stulang", parlimen: "P.160 Johor Bahru", color: "#90CAF9", state: "Johor", coords: [[1.54,103.78],[1.56,103.82],[1.52,103.84],[1.50,103.82],[1.50,103.78]] },
  { id: "n09", name: "Tanjung Puteri", parlimen: "P.161 Johor Bahru", color: "#1976D2", state: "Johor", coords: [[1.56,103.74],[1.58,103.80],[1.54,103.80],[1.52,103.76],[1.54,103.72]] },
  { id: "n10", name: "Pasir Gudang", parlimen: "P.161 Johor Bahru", color: "#1565C0", state: "Johor", coords: [[1.46,103.96],[1.48,104.04],[1.44,104.06],[1.42,104.00],[1.42,103.94]] },
  { id: "n11", name: "Tebrau", parlimen: "P.162 Johor Bahru", color: "#0D47A1", state: "Johor", coords: [[1.50,103.92],[1.52,103.98],[1.48,104.00],[1.46,103.96],[1.46,103.90]] },
  { id: "n12", name: "Pulai", parlimen: "P.162 Johor Bahru", color: "#1A237E", state: "Johor", coords: [[1.44,103.72],[1.48,103.78],[1.46,103.82],[1.42,103.80],[1.40,103.74]] },

  // PONTIAN - 4 ADUN
  { id: "n13", name: "Kukup", parlimen: "P.163 Pontian", color: "#FF9800", state: "Johor", coords: [[1.32,103.46],[1.34,103.56],[1.30,103.58],[1.28,103.52],[1.28,103.46]] },
  { id: "n14", name: "Pekan Nenas", parlimen: "P.163 Pontian", color: "#FFA726", state: "Johor", coords: [[1.38,103.52],[1.40,103.62],[1.36,103.64],[1.34,103.58],[1.34,103.52]] },
  { id: "n15", name: "Ayer Baloi", parlimen: "P.164 Pontian", color: "#FFB74D", state: "Johor", coords: [[1.34,103.36],[1.36,103.46],[1.32,103.48],[1.30,103.42],[1.30,103.36]] },
  { id: "n16", name: "Benut", parlimen: "P.164 Pontian", color: "#FFCC80", state: "Johor", coords: [[1.28,103.32],[1.30,103.38],[1.26,103.40],[1.24,103.36],[1.24,103.30]] },

  // BATU PAHAT - 8 ADUN
  { id: "n17", name: "Serom", parlimen: "P.165 Batu Pahat", color: "#9C27B0", state: "Johor", coords: [[1.38,103.22],[1.40,103.32],[1.36,103.34],[1.34,103.28],[1.34,103.22]] },
  { id: "n18", name: "Semerah", parlimen: "P.165 Batu Pahat", color: "#AB47BC", state: "Johor", coords: [[1.42,103.20],[1.44,103.30],[1.40,103.32],[1.38,103.28],[1.38,103.20]] },
  { id: "n19", name: "Sri Medan", parlimen: "P.166 Batu Pahat", color: "#CE93D8", state: "Johor", coords: [[1.46,103.18],[1.48,103.26],[1.44,103.28],[1.42,103.24],[1.42,103.18]] },
  { id: "n20", name: "Yong Peng", parlimen: "P.166 Batu Pahat", color: "#BA68C8", state: "Johor", coords: [[1.50,103.14],[1.52,103.22],[1.48,103.24],[1.46,103.20],[1.46,103.14]] },
  { id: "n21", name: "Rengit", parlimen: "P.167 Batu Pahat", color: "#7B1FA2", state: "Johor", coords: [[1.36,103.14],[1.38,103.22],[1.34,103.24],[1.32,103.18],[1.32,103.14]] },
  { id: "n22", name: "Parit Yani", parlimen: "P.167 Batu Pahat", color: "#6A1B9A", state: "Johor", coords: [[1.40,103.10],[1.42,103.18],[1.38,103.20],[1.36,103.16],[1.36,103.10]] },
  { id: "n23", name: "Parit Raja", parlimen: "P.168 Batu Pahat", color: "#4A148C", state: "Johor", coords: [[1.44,103.08],[1.46,103.16],[1.42,103.18],[1.40,103.14],[1.40,103.08]] },
  { id: "n24", name: "Penggaram", parlimen: "P.168 Batu Pahat", color: "#E040FB", state: "Johor", coords: [[1.48,103.06],[1.50,103.14],[1.46,103.16],[1.44,103.12],[1.44,103.06]] },

  // KLUANG - 4 ADUN
  { id: "n25", name: "Mengkibol", parlimen: "P.169 Kluang", color: "#E91E63", state: "Johor", coords: [[1.54,103.38],[1.56,103.48],[1.52,103.50],[1.50,103.44],[1.50,103.38]] },
  { id: "n26", name: "Mahkota", parlimen: "P.169 Kluang", color: "#F06292", state: "Johor", coords: [[1.56,103.34],[1.58,103.42],[1.54,103.44],[1.52,103.40],[1.52,103.34]] },
  { id: "n27", name: "Paloh", parlimen: "P.170 Kluang", color: "#F48FB1", state: "Johor", coords: [[1.52,103.44],[1.54,103.54],[1.50,103.56],[1.48,103.50],[1.48,103.44]] },
  { id: "n28", name: "Kahang", parlimen: "P.170 Kluang", color: "#F8BBD0", state: "Johor", coords: [[1.48,103.52],[1.50,103.64],[1.46,103.66],[1.44,103.58],[1.44,103.52]] },

  // MERSING - 4 ADUN
  { id: "n29", name: "Endau", parlimen: "P.171 Mersing", color: "#00BCD4", state: "Johor", coords: [[1.56,103.62],[1.58,103.74],[1.54,103.76],[1.52,103.70],[1.52,103.62]] },
  { id: "n30", name: "Tenggaroh", parlimen: "P.171 Mersing", color: "#26C6DA", state: "Johor", coords: [[1.52,103.72],[1.54,103.84],[1.50,103.86],[1.48,103.80],[1.48,103.72]] },
  { id: "n31", name: "Panti", parlimen: "P.172 Mersing", color: "#4DD0E1", state: "Johor", coords: [[1.48,103.84],[1.50,103.94],[1.46,103.96],[1.44,103.90],[1.44,103.84]] },
  { id: "n32", name: "Pasir Raja", parlimen: "P.172 Mersing", color: "#80DEEA", state: "Johor", coords: [[1.44,103.94],[1.46,104.04],[1.42,104.06],[1.40,104.00],[1.40,103.94]] },

  // SEGAMAT - 6 ADUN
  { id: "n33", name: "Tenang", parlimen: "P.173 Segamat", color: "#FF5722", state: "Johor", coords: [[1.56,103.00],[1.58,103.10],[1.54,103.12],[1.52,103.06],[1.52,103.00]] },
  { id: "n34", name: "Labis", parlimen: "P.173 Segamat", color: "#FF7043", state: "Johor", coords: [[1.52,103.08],[1.54,103.18],[1.50,103.20],[1.48,103.14],[1.48,103.08]] },
  { id: "n35", name: "Bekok", parlimen: "P.174 Segamat", color: "#FF8A65", state: "Johor", coords: [[1.48,103.16],[1.50,103.28],[1.46,103.30],[1.44,103.22],[1.44,103.16]] },
  { id: "n36", name: "Jementah", parlimen: "P.174 Segamat", color: "#FFAB91", state: "Johor", coords: [[1.44,103.26],[1.46,103.36],[1.42,103.38],[1.40,103.32],[1.40,103.26]] },
  { id: "n37", name: "Kemas", parlimen: "P.175 Segamat", color: "#FFCCBC", state: "Johor", coords: [[1.50,103.30],[1.52,103.40],[1.48,103.42],[1.46,103.36],[1.46,103.30]] },
  { id: "n38", name: "Bukit Kepong", parlimen: "P.175 Segamat", color: "#FFE0B2", state: "Johor", coords: [[1.46,103.38],[1.48,103.48],[1.44,103.50],[1.42,103.44],[1.42,103.38]] },

  // TANGKAK / MUAR - 6 ADUN
  { id: "n39", name: "Sungai Balang", parlimen: "P.176 Tangkak", color: "#3F51B5", state: "Johor", coords: [[1.36,102.92],[1.38,103.00],[1.34,103.02],[1.32,102.98],[1.32,102.92]] },
  { id: "n40", name: "Serkat", parlimen: "P.176 Tangkak", color: "#5C6BC0", state: "Johor", coords: [[1.40,102.96],[1.42,103.04],[1.38,103.06],[1.36,103.02],[1.36,102.96]] },
  { id: "n41", name: "Bukit Serampang", parlimen: "P.177 Tangkak", color: "#7986CB", state: "Johor", coords: [[1.42,103.04],[1.44,103.12],[1.40,103.14],[1.38,103.10],[1.38,103.04]] },
  { id: "n42", name: "Jorak", parlimen: "P.177 Tangkak", color: "#9FA8DA", state: "Johor", coords: [[1.38,103.12],[1.40,103.20],[1.36,103.22],[1.34,103.18],[1.34,103.12]] },

  // MUAR - 4 ADUN
  { id: "n43", name: "Maharani", parlimen: "P.178 Muar", color: "#607D8B", state: "Johor", coords: [[1.34,103.04],[1.36,103.12],[1.32,103.14],[1.30,103.10],[1.30,103.04]] },
  { id: "n44", name: "Sungai Terap", parlimen: "P.178 Muar", color: "#78909C", state: "Johor", coords: [[1.30,103.00],[1.32,103.08],[1.28,103.10],[1.26,103.06],[1.26,103.00]] },
  { id: "n45", name: "Simpang Jeram", parlimen: "P.179 Muar", color: "#90A4AE", state: "Johor", coords: [[1.26,103.04],[1.28,103.14],[1.24,103.16],[1.22,103.10],[1.22,103.04]] },
  { id: "n46", name: "Bukit Pasir", parlimen: "P.179 Muar", color: "#B0BEC5", state: "Johor", coords: [[1.22,103.08],[1.24,103.18],[1.20,103.20],[1.18,103.14],[1.18,103.08]] },

  // LEDANG - 4 ADUN
  { id: "n47", name: "Gambir", parlimen: "P.180 Ledang", color: "#CDDC39", state: "Johor", coords: [[1.38,102.84],[1.40,102.92],[1.36,102.94],[1.34,102.90],[1.34,102.84]] },
  { id: "n48", name: "Tangkak", parlimen: "P.180 Ledang", color: "#D4E157", state: "Johor", coords: [[1.42,102.86],[1.44,102.94],[1.40,102.96],[1.38,102.92],[1.38,102.86]] },
  { id: "n49", name: "Seri Menanti", parlimen: "P.181 Ledang", color: "#DCE775", state: "Johor", coords: [[1.44,102.94],[1.46,103.02],[1.42,103.04],[1.40,103.00],[1.40,102.94]] },
  { id: "n50", name: "Bukit Baling", parlimen: "P.181 Ledang", color: "#E6EE9C", state: "Johor", coords: [[1.42,103.02],[1.44,103.10],[1.40,103.12],[1.38,103.08],[1.38,103.02]] },

  // PAGOH - 4 ADUN
  { id: "n51", name: "Kundang", parlimen: "P.182 Pagoh", color: "#795548", state: "Johor", coords: [[1.36,102.76],[1.38,102.84],[1.34,102.86],[1.32,102.82],[1.32,102.76]] },
  { id: "n52", name: "Bukit Pelanduk", parlimen: "P.182 Pagoh", color: "#8D6E63", state: "Johor", coords: [[1.40,102.78],[1.42,102.86],[1.38,102.88],[1.36,102.84],[1.36,102.78]] },
  { id: "n53", name: "Jasin", parlimen: "P.183 Pagoh", color: "#A1887F", state: "Johor", coords: [[1.42,102.86],[1.44,102.94],[1.40,102.96],[1.38,102.92],[1.38,102.86]] },
  { id: "n54", name: "Lenga", parlimen: "P.183 Pagoh", color: "#BCAAA4", state: "Johor", coords: [[1.38,102.94],[1.40,103.02],[1.36,103.04],[1.34,103.00],[1.34,102.94]] },

  // EXTRA: Kawasan yang tertinggal (based on SPR 56 DUN)
  { id: "n55", name: "Kota Iskandar", parlimen: "P.163 Pontian", color: "#FF5722", state: "Johor", coords: [[1.36,103.46],[1.38,103.54],[1.34,103.56],[1.32,103.52],[1.32,103.46]] },
  { id: "n56", name: "Puteri Wangsa", parlimen: "P.161 Johor Bahru", color: "#00BFA5", state: "Johor", coords: [[1.52,103.82],[1.54,103.88],[1.50,103.90],[1.48,103.86],[1.48,103.82]] }
];

// Party colors for legend
const PARTIES = {
  "BN": "#0000FF",
  "PH": "#E91E63",
  "PN": "#4CAF50",
  "BEBAS": "#9E9E9E",
  "MUDA": "#FF5722",
  "WARISAN": "#2196F3"
};

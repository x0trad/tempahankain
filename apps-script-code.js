function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // Ensure headers exist
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Tarikh', 'Nama', 'Telefon', 'Kawasan', 'Items', 'Jumlah', 'Slip Image']);
    sheet.getRange(1, 1, 1, 7).setFontWeight('bold').setBackground('#c8a97e');
  }

  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (err) {
    // Fallback: form-data
    data = e.parameter;
  }

  var tarikh = data.tarikh || new Date().toLocaleString('ms-MY');
  var nama = data.nama || '';
  var telefon = data.telefon || '';
  var kawasan = data.kawasan || '';
  var items = data.items || '';
  var jumlah = data.jumlah || '';
  var slipImage = data.slipImage || '';

  sheet.appendRow([tarikh, nama, telefon, kawasan, items, jumlah, slipImage]);

  // If slip image exists, insert it
  if (slipImage && slipImage.length > 100) {
    try {
      var imageBlob = Utilities.newBlob(Utilities.base64Decode(slipImage.split(',')[1] || slipImage), 'image/png', 'Slip ' + nama);
      var lastRow = sheet.getLastRow();
      sheet.insertImage(imageBlob, 7, lastRow);
    } catch (imgErr) {
      // Skip image if fails
    }
  }

  // Auto-resize columns
  sheet.autoResizeColumns(1, 6);

  return ContentService.createTextOutput(JSON.stringify({
    status: 'success',
    message: 'Pesanan diterima!',
    row: sheet.getLastRow()
  })).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'online',
    message: 'JARVIS Kain Order Form API'
  })).setMimeType(ContentService.MimeType.JSON);
}

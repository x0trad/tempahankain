// ============================================
// Google Apps Script — Tempahan Kain
// Deployed as Web App → Exec
// ============================================

// The sheet MUST have these columns:
// Order ID | Tarikh | Nama | Telefon | Kawasan | Item | Saiz | Jumlah Item | Jumlah Total | Slip | Status
//      A   |   B    |   C  |    D    |    E    |   F  |   G  |      H      |      I       |  J   |   K

function doGet(e) {
  const action = e?.parameter?.action || '';
  
  if (action === 'getOrders') {
    return getOrdersAsJson();
  }
  
  return ContentService.createTextOutput(
    JSON.stringify({ error: 'Unknown action. Use ?action=getOrders' })
  ).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const body = e.postData?.contents || '{}';
    Logger.log('Raw body: ' + body);
    
    // Handle JSONP callback wrapper
    let data;
    if (body.startsWith('{')) {
      data = JSON.parse(body);
    } else {
      // Try to extract JSON from callback
      const match = body.match(/\{[\s\S]*\}/);
      if (match) data = JSON.parse(match[0]);
      else throw new Error('Invalid JSON body');
    }
    
    Logger.log('Parsed: ' + JSON.stringify(data));
    
    // Check if this is an admin action
    if (data.action === 'updateStatus') {
      return updateOrderStatus(data);
    }
    
    // Otherwise, it's a new order submission
    const ss = SpreadsheetApp.openById('1wgXM33U_-9moC1qyrJpEoeWdlU4XEwaN0tB9UlPFt1g');
    const sheet = ss.getSheets()[0];
    const items = data.items || [];
    const hasilRows = [];
    const now = new Date();
    // Malaysian timezone
    const tarikh = Utilities.formatDate(now, 'Asia/Kuala_Lumpur', 'dd/MM/yyyy HH:mm');
    
    items.forEach(item => {
      hasilRows.push([
        data.orderId,         // A: Order ID
        tarikh,               // B: Tarikh
        data.nama,            // C: Nama
        data.telefon,         // D: Telefon
        data.kawasan,         // E: Kawasan
        item.typeLabel,       // F: Item
        item.sizeInfo || '',  // G: Saiz
        item.quantity || 1,   // H: Jumlah Item
        item.total.toFixed(2),// I: Jumlah Total (per item)
        data.slip || '',      // J: Slip
        'Menunggu'            // K: Status
      ]);
    });
    
    // Get next empty row
    const startRow = sheet.getLastRow() + 1;
    if (hasilRows.length > 0) {
      sheet.getRange(startRow, 1, hasilRows.length, hasilRows[0].length).setValues(hasilRows);
    }
    
    Logger.log(`Inserted ${hasilRows.length} rows starting at row ${startRow}`);
    
    // Return success via redirect
    const output = ContentService.createTextOutput(JSON.stringify({ status: 'ok', rows: hasilRows.length }));
    return output.setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log('ERROR: ' + error.message);
    
    // Return error as JSON
    const output = ContentService.createTextOutput(JSON.stringify({ status: 'error', message: error.message }));
    return output.setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrdersAsJson() {
  try {
    const ss = SpreadsheetApp.openById('1wgXM33U_-9moC1qyrJpEoeWdlU4XEwaN0tB9UlPFt1g');
    const sheet = ss.getSheets()[0];
    const lastRow = sheet.getLastRow();
    
    if (lastRow < 2) {
      return ContentService.createTextOutput(
        JSON.stringify({ orders: [] })
      ).setMimeType(ContentService.MimeType.JSON);
    }
    
    const data = sheet.getRange(2, 1, lastRow - 1, 11).getValues(); // 11 columns
    
    const orders = data.map((row, i) => ({
      rowIndex: i + 2,  // Actual sheet row number
      orderId: row[0] || '',
      tarikh: row[1] || '',
      nama: row[2] || '',
      telefon: row[3] || '',
      kawasan: row[4] || '',
      item: row[5] || '',
      saiz: row[6] || '',
      jumlahItem: row[7] || '',
      jumlahTotal: row[8] || '',
      slip: row[9] || '',
      status: row[10] || 'Menunggu'
    }));
    
    // Sort by row descending (newest first)
    orders.reverse();
    
    return ContentService.createTextOutput(
      JSON.stringify({ orders })
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log('getOrders ERROR: ' + error.message);
    return ContentService.createTextOutput(
      JSON.stringify({ error: error.message, orders: [] })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function updateOrderStatus(data) {
  try {
    const ss = SpreadsheetApp.openById('1wgXM33U_-9moC1qyrJpEoeWdlU4XEwaN0tB9UlPFt1g');
    const sheet = ss.getSheets()[0];
    const rowIndex = parseInt(data.rowKey);
    const newStatus = data.status;
    
    // Column 11 (K) = Status
    sheet.getRange(rowIndex, 11).setValue(newStatus);
    
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'ok', row: rowIndex, newStatus: newStatus })
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log('updateStatus ERROR: ' + error.message);
    return ContentService.createTextOutput(
      JSON.stringify({ status: 'error', message: error.message })
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

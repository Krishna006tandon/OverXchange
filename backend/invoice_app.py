from flask import Flask, render_template, send_file, request, jsonify
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/invoices'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def invoice():
    """Main invoice page"""
    return render_template("invoice.html")

@app.route("/api/generate-invoice", methods=["POST"])
def generate_invoice():
    """Generate invoice with provided data"""
    try:
        data = request.json
        
        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        
        # Create invoice data
        invoice_data = {
            'invoice_number': invoice_number,
            'date': datetime.now().strftime('%d %B, %Y'),
            'from_name': data.get('from_name', 'Your Company'),
            'from_address': data.get('from_address', '123 Business St.'),
            'from_email': data.get('from_email', 'contact@company.com'),
            'to_name': data.get('to_name', 'Client Name'),
            'to_address': data.get('to_address', 'Client Address'),
            'to_email': data.get('to_email', 'client@email.com'),
            'items': data.get('items', []),
            'payment_method': data.get('payment_method', 'Cash'),
            'total': data.get('total', 0)
        }
        
        return jsonify({
            'success': True,
            'invoice_data': invoice_data,
            'message': 'Invoice generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating invoice: {str(e)}'
        }), 500

@app.route("/api/save-invoice", methods=["POST"])
def save_invoice():
    """Save invoice data to file"""
    try:
        data = request.json
        
        # Create invoice HTML
        invoice_html = create_invoice_html(data)
        
        # Save to file
        filename = f"invoice_{data['invoice_number']}.html"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(invoice_html)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'Invoice saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving invoice: {str(e)}'
        }), 500

@app.route("/download/<filename>")
def download_invoice(filename):
    """Download invoice file"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_invoice_html(data):
    """Create HTML content for invoice"""
    items_html = ''
    for item in data.get('items', []):
        items_html += f'''
        <tr>
            <td>{item.get('name', '')}</td>
            <td>{item.get('quantity', '')}</td>
            <td>${item.get('price', '0')}</td>
            <td>${item.get('amount', '0')}</td>
        </tr>
        '''
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice - {data.get('invoice_number', '')}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: white;
            }}
            .invoice-box {{
                max-width: 800px;
                margin: auto;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            header {{
                display: flex;
                justify-content: space-between;
                border-bottom: 2px solid #ccc;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .logo {{
                font-weight: bold;
                font-size: 24px;
            }}
            .address-section {{
                display: flex;
                justify-content: space-between;
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background: #f5f5f5;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            .summary {{
                margin-top: 20px;
                text-align: right;
                font-size: 16px;
                border-top: 2px solid #eee;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <header>
                <div class="logo">YOUR LOGO</div>
                <div class="invoice-details">
                    <p><strong>Invoice No:</strong> {data.get('invoice_number', '')}</p>
                    <p><strong>Date:</strong> {data.get('date', '')}</p>
                </div>
            </header>

            <section class="address-section">
                <div>
                    <h3>From:</h3>
                    <p>{data.get('from_name', '')}</p>
                    <p>{data.get('from_address', '')}</p>
                    <p>{data.get('from_email', '')}</p>
                </div>
                <div>
                    <h3>Billed to:</h3>
                    <p>{data.get('to_name', '')}</p>
                    <p>{data.get('to_address', '')}</p>
                    <p>{data.get('to_email', '')}</p>
                </div>
            </section>

            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <div class="summary">
                <p><strong>Total:</strong> ${data.get('total', '0')}</p>
                <p><strong>Payment Method:</strong> {data.get('payment_method', '')}</p>
                <p><em>Thank you for choosing us!</em></p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html_content

@app.route("/api/invoices")
def list_invoices():
    """List all saved invoices"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.endswith('.html'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': stat.st_size
                })
        
        return jsonify({
            'success': True,
            'invoices': files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing invoices: {str(e)}'
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001) 
from flask import Flask, render_template, request, jsonify, send_file, url_for
import pandas as pd
from pathlib import Path
from .file_handlers import read_file, write_file
from .data_merger import DataMerger
import tempfile
import os
from waitress import serve
from paste.translogger import TransLogger
import logging
import socket
# Import ColumnMapping
from file_processor import FileProcessor, ColumnMapping
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('waitress')

app = Flask(__name__, 
           template_folder=str(Path(__file__).parent / 'templates'),
           static_folder=str(Path(__file__).parent / 'static'))

@app.route('/')
def index():
    """Render main interface"""
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview_file():
    """Preview CSV/Excel file contents"""
    file = request.files['file']
    sheet_name = request.form.get('sheet')
    is_focus = request.form.get('focus') == 'true'  # Check if focus view
    
    if not file:
        return jsonify({'error': 'No file provided'})
        
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)
    
    try:
        # Read file using pandas with explicit sheet handling
        if file.filename.endswith('.xlsx'):
            # Get sheet name - either from form or first sheet
            xls = pd.ExcelFile(temp_path)
            available_sheets = xls.sheet_names
            
            if not sheet_name:
                sheet_name = available_sheets[0]
            elif sheet_name not in available_sheets:
                return jsonify({'error': f'Sheet "{sheet_name}" not found. Available sheets: {", ".join(available_sheets)}'})
                
            # Read specified sheet
            df = pd.read_excel(temp_path, sheet_name=sheet_name)
            excel_info = {
                'is_excel': True,
                'current_sheet': sheet_name,
                'available_sheets': available_sheets
            }
        else:
            df = pd.read_csv(temp_path)
            excel_info = {'is_excel': False}
            
        # Get preview data based on view type
        preview_rows = 1000 if is_focus else 5
            
        # Convert to dict after taking head rows
        preview_data = df.head(preview_rows).fillna('').to_dict('records')
        
        return jsonify({
            'columns': list(df.columns),
            'preview': preview_data,
            'total_rows': len(df),
            'file_type': request.form.get('type', 'source'),
            **excel_info  # Include Excel information in response
        })
    except Exception as e:
        logger.error(f"Error previewing file: {str(e)}")
        return jsonify({'error': str(e)})
    finally:
        # Clean up temp files
        os.remove(temp_path)
        os.rmdir(temp_dir)

@app.route('/merge', methods=['POST'])
def merge_files():
    """Perform file merge operation"""
    try:
        logger.info("Starting merge operation")
        source = request.files['source']
        dest = request.files['destination']

        # Log input parameters
        logger.info(f"Source file: {source.filename}")
        logger.info(f"Destination file: {dest.filename}")
        logger.info(f"Match column: {request.form['match_column']}")
        logger.info(f"Columns to copy: {request.form.getlist('columns[]')}")

        # Get merge parameters
        match_column = request.form['match_column']
        columns = request.form.getlist('columns[]')
        join_type = request.form.get('join_type', 'left')
        ignore_case = request.form.get('ignore_case') == 'true'

        # Read files with sheet handling
        source_sheet = request.form.get('source_sheet') or 0
        dest_sheet = request.form.get('dest_sheet') or 0

        logger.info(f"Reading source file with sheet: {source_sheet}")
        if source.filename.endswith('.xlsx'):
            source_df = pd.read_excel(source, sheet_name=source_sheet)
        else:
            source_df = pd.read_csv(source)

        logger.info(f"Reading destination file with sheet: {dest_sheet}")
        if dest.filename.endswith('.xlsx'):
            dest_df = pd.read_excel(dest, sheet_name=dest_sheet)
        else:
            dest_df = pd.read_csv(dest)

        # Initialize merger and process files
        merger = DataMerger(source_df, dest_df)
        result_df = merger.merge(
            match_column=match_column,
            columns_to_copy=columns,
            ignore_case=ignore_case,
            join_type=join_type
        )

        # Save the merged file to the default temporary directory
        temp_dir = tempfile.gettempdir()
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{dest.filename}"
        temp_file_path = os.path.join(temp_dir, unique_filename)
        logger.info(f"Writing merged file to: {temp_file_path}")

        if dest.filename.endswith('.xlsx'):
            result_df.to_excel(temp_file_path, index=False)
        else:
            result_df.to_csv(temp_file_path, index=False)

        logger.info("Write operation successful")

        # Return success response with stats and download link
        stats = {
            'rows_before': len(dest_df),
            'rows_after': len(result_df),
            'rows_changed': len(result_df) - len(dest_df),
            'new_columns': list(set(columns) - set(dest_df.columns)),
            'matched_rows': len(result_df[result_df[match_column].notna()]) if match_column in result_df else 0
        }
        logger.info(f"Operation stats: {stats}")

        # Return the unique filename in the download URL
        return jsonify({
            'success': True,
            'stats': stats,
            'download_url': f"/download/{unique_filename}"
        })

    except Exception as e:
        logger.error(f"Error during merge: {str(e)}")
        return jsonify({'error': str(e)})

@app.route('/getsheets', methods=['POST'])
def get_sheets():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'No file provided'})
    
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)
    
    try:
        if file.filename.endswith('.xlsx'):
            xls = pd.ExcelFile(temp_path)
            sheets = xls.sheet_names
            return jsonify({'sheets': sheets})
        else:
            return jsonify({'error': 'Not an Excel file'})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        os.remove(temp_path)
        os.rmdir(temp_dir)

@app.route('/download/<filename>')
def download_file(filename):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

def find_free_port(start_port=5000, max_port=5100):
    """Find first available port in range"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found between {start_port} and {max_port}")

def start_web_interface(host='0.0.0.0', port=5000, debug=False):
    """Start the web interface with automatic port finding"""
    try:
        if port is None:
            port = find_free_port()
            
        logger.info(f'Starting server on http://{host}:{port}')
        
        if debug:
            app.run(host=host, port=port, debug=True)
        else:
            serve(TransLogger(app), host=host, port=port)
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            new_port = find_free_port(port + 1)
            logger.info(f'Port {port} in use, trying port {new_port}')
            start_web_interface(host=host, port=new_port, debug=debug)
        else:
            raise

# Remove or comment out this function in web_interface.py
# def read_file(file_path, sheet_name=None):
#     # Function body
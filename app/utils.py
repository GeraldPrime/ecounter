# utils.py - Helper functions
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

def validate_excel_columns(df):
    """Validate that the Excel file has required columns"""
    required_columns = [
        'S/NO', 'STATE', 'LGA', 'RA', 'DELIM',
        'REGISTER VOTER AS AT 2023', 'REGISTERED VOTER AS AT 2024',
        'NO OF PVC COLLECTED ', 'BALANCE OF UNCOLECTED PVCs',
        '45% PVC COLLECTION'
    ]
    
    missing_columns = []
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    return missing_columns

def clean_excel_data(df):
    """Clean and prepare Excel data for import"""
    # Fill NaN values
    df = df.fillna(0)
    
    # Convert numeric columns
    numeric_cols = [
        'REGISTERED VOTER AS AT 2024', 'NO OF PVC COLLECTED ',
        'BALANCE OF UNCOLECTED PVCs', '45% PVC COLLECTION',
        'AA', 'AD', 'ADC', 'APC', 'LP', 'PDP'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

def export_allocation_to_excel(allocation, results):
    """Export allocation results to Excel with formatting"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Vote Allocation Results"
    
    # Headers
    headers = [
        'S/NO', 'STATE', 'LGA', 'RA', 'DELIM', 'REGISTER VOTER AS AT 2023',
        'REGISTERED VOTER AS AT 2024', 'NO OF PVC COLLECTED', 'BALANCE OF UNCOLLECTED PVCs',
        '45% PVC COLLECTION', 'AA', 'AD', 'ADC', 'APC', 'LP', 'PDP', 'TOTAL'
    ]
    
    # Style headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    
    # Add allocation info as a comment or separate sheet
    ws.cell(row=1, column=len(headers) + 2, value=f"Allocation: {allocation.name}")
    ws.cell(row=2, column=len(headers) + 2, value=f"APC: {allocation.apc_percentage}%")
    ws.cell(row=3, column=len(headers) + 2, value=f"LP: {allocation.lp_percentage}%")
    ws.cell(row=4, column=len(headers) + 2, value=f"PDP: {allocation.pdp_percentage}%")
    
    return wb

#
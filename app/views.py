from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Sum, Q
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
import json
import random
import math

# PDF imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .models import PollingUnit, VoteAllocation, AllocatedResult

def dashboard(request):
    """Main dashboard view"""
    total_units = PollingUnit.objects.count()
    total_allocations = VoteAllocation.objects.count()
    total_pvc_45 = PollingUnit.objects.aggregate(
        total=Sum('pvc_45_percent')
    )['total'] or 0

    # Calculate average PVC per unit
    average_pvc_per_unit = 0
    if total_units > 0:
        average_pvc_per_unit = total_pvc_45 / total_units

    recent_allocations = VoteAllocation.objects.order_by('-created_at')[:5]

    context = {
        'total_units': total_units,
        'total_allocations': total_allocations,
        'total_pvc_45': total_pvc_45,
        'average_pvc_per_unit': average_pvc_per_unit,
        'recent_allocations': recent_allocations,
    }
    return render(request, 'vote_allocation/dashboard.html', context)

# def upload_data(request):
#     """Handle Excel file upload"""
#     if request.method == 'POST' and request.FILES.get('excel_file'):
#         excel_file = request.FILES['excel_file']
        
#         try:
#             # Read Excel file
#             df = pd.read_excel(excel_file)
            
#             # Debug: print column names and first few rows
#             print("Excel columns:", df.columns.tolist())
#             print("Data shape:", df.shape)
#             print("First row data:", df.iloc[0].to_dict() if len(df) > 0 else "No data")
            
#             # Clear existing data
#             PollingUnit.objects.all().delete()
            
#             # Import data
#             created_count = 0
#             errors = []
            
#             for index, row in df.iterrows():
#                 try:
#                     # Skip empty rows
#                     if pd.isna(row.get('S/NO')) or row.get('S/NO') == '':
#                         continue
                    
#                     # Create polling unit with just the basic data
#                     polling_unit = PollingUnit.objects.create(
#                         sno=int(float(str(row.get('S/NO', 0)).replace(',', ''))),
#                         state=str(row.get('STATE', '')).strip(),
#                         lga=str(row.get('LGA', '')).strip(),
#                         ra=str(row.get('RA', '')).strip(),
#                         delim=str(row.get('DELIM', '')).strip(),
#                         register_voter_2023=str(row.get('REGISTER VOTER AS AT 2023', '')).strip(),
#                         registered_voter_2024=int(float(str(row.get('REGISTERED VOTER AS AT 2024', 0)).replace(',', ''))),
#                         pvc_collected=int(float(str(row.get('NO OF PVC COLLECTED ', 0)).replace(',', ''))),
#                         balance_uncollected=int(float(str(row.get('BALANCE OF UNCOLECTED PVCs', 0)).replace(',', ''))),
#                         pvc_45_percent=float(str(row.get('45% PVC COLLECTION', 0)).replace(',', '')),
#                         # Set party fields to 0 for now - they'll be calculated during allocation
#                         aa_original=0,
#                         ad_original=0,
#                         adc_original=0,
#                         apc_original=0,
#                         lp_original=0,
#                         pdp_original=0,
#                     )
#                     created_count += 1
                    
#                     # Print progress every 100 records
#                     if created_count % 100 == 0:
#                         print(f"Imported {created_count} records...")
                        
#                 except Exception as row_error:
#                     error_msg = f"Error in row {index + 2}: {str(row_error)}"
#                     print(error_msg)
#                     errors.append(error_msg)
#                     continue
            
#             if created_count > 0:
#                 messages.success(request, f'Successfully imported {created_count} polling units.')
#                 if errors:
#                     messages.warning(request, f'Encountered {len(errors)} errors during import.')
#             else:
#                 messages.error(request, 'No valid data was imported. Please check your Excel file format.')
            
#             return redirect('dashboard')
            
#         except Exception as e:
#             error_msg = f'Error importing data: {str(e)}'
#             print(error_msg)
#             messages.error(request, error_msg)

#     elif request.method == 'POST':
#         messages.error(request, 'No file was selected. Please choose an Excel file.')
    
#     return render(request, 'vote_allocation/upload.html')


def upload_data(request):
    """Handle Excel file upload"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        
        try:
            df = pd.read_excel(excel_file)
            PollingUnit.objects.all().delete()
            AllocatedResult.objects.all().delete()
            
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    if pd.isna(row.get('S/NO')) or row.get('S/NO') == '':
                        continue
                    
                    # Round the 45% PVC to whole number
                    pvc_45_raw = float(str(row.get('45% PVC COLLECTION', 0)).replace(',', ''))
                    pvc_45_rounded = round(pvc_45_raw)
                    
                    polling_unit = PollingUnit.objects.create(
                        sno=int(float(str(row.get('S/NO', 0)).replace(',', ''))),
                        state=str(row.get('STATE', '')).strip(),
                        lga=str(row.get('LGA', '')).strip(),
                        ra=str(row.get('RA', '')).strip(),
                        delim=str(row.get('DELIM', '')).strip(),
                        register_voter_2023=str(row.get('REGISTER VOTER AS AT 2023', '')).strip(),
                        registered_voter_2024=int(float(str(row.get('REGISTERED VOTER AS AT 2024', 0)).replace(',', ''))),
                        pvc_collected=int(float(str(row.get('NO OF PVC COLLECTED ', 0)).replace(',', ''))),
                        balance_uncollected=int(float(str(row.get('BALANCE OF UNCOLECTED PVCs', 0)).replace(',', ''))),
                        pvc_45_percent=pvc_45_rounded,  # Now rounded to whole number
                        aa_original=0,
                        ad_original=0,
                        adc_original=0,
                        apc_original=0,
                        lp_original=0,
                        pdp_original=0,
                    )
                    created_count += 1
                    
                    if created_count % 100 == 0:
                        print(f"Imported {created_count} records...")
                        
                except Exception as row_error:
                    error_msg = f"Error in row {index + 2}: {str(row_error)}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue
            
            if created_count > 0:
                messages.success(request, f'Successfully imported {created_count} polling units.')
                if errors:
                    messages.warning(request, f'Encountered {len(errors)} errors during import.')
            else:
                messages.error(request, 'No valid data was imported. Please check your Excel file format.')
            
            return redirect('dashboard')
            
        except Exception as e:
            error_msg = f'Error importing data: {str(e)}'
            print(error_msg)
            messages.error(request, error_msg)
    
    elif request.method == 'POST':
        messages.error(request, 'No file was selected. Please choose an Excel file.')

    return render(request, 'vote_allocation/upload.html')

def polling_units_list(request):
    """List all polling units with pagination"""
    units = PollingUnit.objects.all()

    # Search functionality
    search = request.GET.get('search')
    if search:
        units = units.filter(
            Q(state__icontains=search) |
            Q(lga__icontains=search) |
            Q(delim__icontains=search)
        )

    paginator = Paginator(units, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'vote_allocation/polling_units.html', context)

# def create_allocation(request):
#     """Create new vote allocation"""
#     if request.method == 'POST':
#         try:
#             allocation = VoteAllocation.objects.create(
#                 name=request.POST['name'],
#                 description=request.POST.get('description', ''),
#                 aa_percentage=float(request.POST.get('aa_percentage', 0)),
#                 ad_percentage=float(request.POST.get('ad_percentage', 0)),
#                 adc_percentage=float(request.POST.get('adc_percentage', 0)),
#                 apc_percentage=float(request.POST.get('apc_percentage', 0)),
#                 lp_percentage=float(request.POST.get('lp_percentage', 0)),
#                 pdp_percentage=float(request.POST.get('pdp_percentage', 0)),
#             )
            
#             if not allocation.is_valid_allocation():
#                 messages.warning(request, 
#                     f'Total percentage is {allocation.total_percentage():.1f}%. Should be 100%.')
            
#             # Calculate allocated results
#             calculate_allocated_results(allocation)

#             messages.success(request, 'Vote allocation created successfully!')
#             return redirect('view_allocation_results', allocation_id=allocation.id)

#         except Exception as e:
#             messages.error(request, f'Error creating allocation: {str(e)}')

#     return render(request, 'vote_allocation/create_allocation.html')


# def create_allocation(request):
#     """Create new vote allocation"""
#     if request.method == 'POST':
#         try:
#             # Check if we have polling units
#             units_count = PollingUnit.objects.count()
#             if units_count == 0:
#                 messages.error(request, 'No polling units found. Please upload data first.')
#                 return redirect('upload_data')
            
#             allocation = VoteAllocation.objects.create(
#                 name=request.POST['name'],
#                 description=request.POST.get('description', ''),
#                 aa_percentage=float(request.POST.get('aa_percentage', 0)),
#                 ad_percentage=float(request.POST.get('ad_percentage', 0)),
#                 adc_percentage=float(request.POST.get('adc_percentage', 0)),
#                 apc_percentage=float(request.POST.get('apc_percentage', 0)),
#                 lp_percentage=float(request.POST.get('lp_percentage', 0)),
#                 pdp_percentage=float(request.POST.get('pdp_percentage', 0)),
#             )
            
#             if not allocation.is_valid_allocation():
#                 messages.warning(request, 
#                     f'Total percentage is {allocation.total_percentage():.1f}%. Should be 100%.')
            
#             # SIMPLE RELIABLE CALCULATION - Create results for all polling units
#             polling_units = PollingUnit.objects.all()
#             results = []
            
#             for unit in polling_units:
#                 if unit.pvc_collected > 0:  # Only process units with votes
#                     # Simple calculation without randomization
#                     aa_votes = int(unit.pvc_collected * (allocation.aa_percentage / 100))
#                     ad_votes = int(unit.pvc_collected * (allocation.ad_percentage / 100))
#                     adc_votes = int(unit.pvc_collected * (allocation.adc_percentage / 100))
#                     apc_votes = int(unit.pvc_collected * (allocation.apc_percentage / 100))
#                     lp_votes = int(unit.pvc_collected * (allocation.lp_percentage / 100))
#                     pdp_votes = int(unit.pvc_collected * (allocation.pdp_percentage / 100))
#                     total_votes = aa_votes + ad_votes + adc_votes + apc_votes + lp_votes + pdp_votes
                    
#                     results.append(AllocatedResult(
#                         polling_unit=unit,
#                         vote_allocation=allocation,
#                         aa_votes=aa_votes,
#                         ad_votes=ad_votes,
#                         adc_votes=adc_votes,
#                         apc_votes=apc_votes,
#                         lp_votes=lp_votes,
#                         pdp_votes=pdp_votes,
#                         total_votes=total_votes,
#                     ))
            
#             # Create all results at once
#             AllocatedResult.objects.bulk_create(results)
            
#             messages.success(request, f'Vote allocation created successfully! Generated {len(results)} results.')
#             return redirect('view_allocation_results', allocation_id=allocation.id)
            
#         except Exception as e:
#             messages.error(request, f'Error creating allocation: {str(e)}')

#     return render(request, 'vote_allocation/create_allocation.html')


def create_allocation(request):
    """Create new vote allocation"""
    if request.method == 'POST':
        try:
            units_count = PollingUnit.objects.count()
            if units_count == 0:
                messages.error(request, 'No polling units found. Please upload data first.')
                return redirect('upload_data')
            
            allocation = VoteAllocation.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
                aa_percentage=float(request.POST.get('aa_percentage', 0)),
                ad_percentage=float(request.POST.get('ad_percentage', 0)),
                adc_percentage=float(request.POST.get('adc_percentage', 0)),
                apc_percentage=float(request.POST.get('apc_percentage', 0)),
                lp_percentage=float(request.POST.get('lp_percentage', 0)),
                pdp_percentage=float(request.POST.get('pdp_percentage', 0)),
            )
            
            if not allocation.is_valid_allocation():
                messages.warning(request, 
                    f'Total percentage is {allocation.total_percentage():.1f}%. Should be 100%.')
            
            # Use 45% PVC instead of PVC collected
            polling_units = PollingUnit.objects.all()
            results = []
            
            for unit in polling_units:
                if unit.pvc_45_percent > 0:  # Use 45% PVC instead of pvc_collected
                    base_votes = unit.pvc_45_percent  # Changed from pvc_collected
                    
                    aa_votes = int(base_votes * (allocation.aa_percentage / 100))
                    ad_votes = int(base_votes * (allocation.ad_percentage / 100))
                    adc_votes = int(base_votes * (allocation.adc_percentage / 100))
                    apc_votes = int(base_votes * (allocation.apc_percentage / 100))
                    lp_votes = int(base_votes * (allocation.lp_percentage / 100))
                    pdp_votes = int(base_votes * (allocation.pdp_percentage / 100))
                    total_votes = aa_votes + ad_votes + adc_votes + apc_votes + lp_votes + pdp_votes
                    
                    results.append(AllocatedResult(
                        polling_unit=unit,
                        vote_allocation=allocation,
                        aa_votes=aa_votes,
                        ad_votes=ad_votes,
                        adc_votes=adc_votes,
                        apc_votes=apc_votes,
                        lp_votes=lp_votes,
                        pdp_votes=pdp_votes,
                        total_votes=total_votes,
                    ))
            
            AllocatedResult.objects.bulk_create(results)
            
            messages.success(request, f'Vote allocation created successfully! Generated {len(results)} results.')
            return redirect('view_allocation_results', allocation_id=allocation.id)
            
        except Exception as e:
            messages.error(request, f'Error creating allocation: {str(e)}')

    return render(request, 'vote_allocation/create_allocation.html')


def allocations_list(request):
    """List all vote allocations"""
    allocations = VoteAllocation.objects.order_by('-created_at')

    context = {
        'allocations': allocations,
    }
    return render(request, 'vote_allocation/allocations_list.html', context)

def calculate_allocated_results(allocation):
    """Calculate and save realistic allocated results for all polling units"""
    # Clear existing results for this allocation
    AllocatedResult.objects.filter(vote_allocation=allocation).delete()
    
    # Get all polling units
    polling_units = PollingUnit.objects.all()
    
    # Calculate for each unit
    results = []
    for unit in polling_units:
        # Use the actual PVC collected as the base for vote distribution
        base_votes = unit.pvc_collected
        
        # Add some realism - not everyone votes, typically 70-95% turnout
        turnout_rate = random.uniform(0.75, 0.95)
        actual_votes = int(base_votes * turnout_rate)
        
        # Calculate target votes for each party based on allocation percentages
        target_aa = (allocation.aa_percentage / 100) * actual_votes
        target_ad = (allocation.ad_percentage / 100) * actual_votes
        target_adc = (allocation.adc_percentage / 100) * actual_votes
        target_apc = (allocation.apc_percentage / 100) * actual_votes
        target_lp = (allocation.lp_percentage / 100) * actual_votes
        target_pdp = (allocation.pdp_percentage / 100) * actual_votes
        
        # Add realistic variation (±5-15% from target to simulate real voting patterns)
        def add_realistic_variation(target_votes, variation_range=0.10):
            if target_votes == 0:
                return 0
            variation = random.uniform(-variation_range, variation_range)
            result = target_votes * (1 + variation)
            return max(0, int(round(result)))
        
        # Calculate actual votes with variation
        aa_votes = add_realistic_variation(target_aa)
        ad_votes = add_realistic_variation(target_ad)
        adc_votes = add_realistic_variation(target_adc)
        apc_votes = add_realistic_variation(target_apc)
        lp_votes = add_realistic_variation(target_lp)
        pdp_votes = add_realistic_variation(target_pdp)
        
        # Calculate total and adjust if necessary to match actual votes
        calculated_total = aa_votes + ad_votes + adc_votes + apc_votes + lp_votes + pdp_votes
        
        # Adjust the largest party's votes to match the actual vote count
        if calculated_total != actual_votes:
            difference = actual_votes - calculated_total
            # Find the party with the highest allocation to adjust
            party_votes = [
                ('aa', aa_votes), ('ad', ad_votes), ('adc', adc_votes),
                ('apc', apc_votes), ('lp', lp_votes), ('pdp', pdp_votes)
            ]
            party_votes.sort(key=lambda x: x[1], reverse=True)
            
            # Adjust the largest party
            if party_votes[0][0] == 'aa':
                aa_votes += difference
            elif party_votes[0][0] == 'ad':
                ad_votes += difference
            elif party_votes[0][0] == 'adc':
                adc_votes += difference
            elif party_votes[0][0] == 'apc':
                apc_votes += difference
            elif party_votes[0][0] == 'lp':
                lp_votes += difference
            elif party_votes[0][0] == 'pdp':
                pdp_votes += difference
        
        # Ensure no negative votes
        aa_votes = max(0, aa_votes)
        ad_votes = max(0, ad_votes)
        adc_votes = max(0, adc_votes)
        apc_votes = max(0, apc_votes)
        lp_votes = max(0, lp_votes)
        pdp_votes = max(0, pdp_votes)
        
        total_votes = aa_votes + ad_votes + adc_votes + apc_votes + lp_votes + pdp_votes
        
        results.append(AllocatedResult(
            polling_unit=unit,
            vote_allocation=allocation,
            aa_votes=aa_votes,
            ad_votes=ad_votes,
            adc_votes=adc_votes,
            apc_votes=apc_votes,
            lp_votes=lp_votes,
            pdp_votes=pdp_votes,
            total_votes=total_votes,
        ))
    
    # Bulk create results
    AllocatedResult.objects.bulk_create(results)
    print(f"Created realistic allocation results for {len(results)} polling units")

# FIXED - Single view_allocation_results function
def view_allocation_results(request, allocation_id):
    """View allocation details and results with party percentages displayed"""
    allocation = get_object_or_404(VoteAllocation, id=allocation_id)
    results = AllocatedResult.objects.filter(vote_allocation=allocation).select_related('polling_unit')
    
    # Pagination for results
    paginator = Paginator(results, 50)  # Show more results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate totals and verify percentages
    totals = results.aggregate(
        total_aa=Sum('aa_votes'),
        total_ad=Sum('ad_votes'),
        total_adc=Sum('adc_votes'),
        total_apc=Sum('apc_votes'),
        total_lp=Sum('lp_votes'),
        total_pdp=Sum('pdp_votes'),
        grand_total=Sum('total_votes'),
    )
    
    # Calculate actual percentages achieved
    grand_total = totals['grand_total'] or 1  # Avoid division by zero
    actual_percentages = {
        'aa': (totals['total_aa'] or 0) / grand_total * 100,
        'ad': (totals['total_ad'] or 0) / grand_total * 100,
        'adc': (totals['total_adc'] or 0) / grand_total * 100,
        'apc': (totals['total_apc'] or 0) / grand_total * 100,
        'lp': (totals['total_lp'] or 0) / grand_total * 100,
        'pdp': (totals['total_pdp'] or 0) / grand_total * 100,
    }

    context = {
        'allocation': allocation,
        'page_obj': page_obj,
        'totals': totals,
        'actual_percentages': actual_percentages,
    }
    return render(request, 'vote_allocation/view_allocation_results.html', context)

# NEW - Full data view like polling units but with party allocations
def view_allocation_full_data(request, allocation_id):
    """View all allocated results in a table format like polling units"""
    allocation = get_object_or_404(VoteAllocation, id=allocation_id)
    results = AllocatedResult.objects.filter(vote_allocation=allocation).select_related('polling_unit')

    # Search functionality
    search = request.GET.get('search')
    if search:
        results = results.filter(
            Q(polling_unit__state__icontains=search) |
            Q(polling_unit__lga__icontains=search) |
            Q(polling_unit__delim__icontains=search)
        )

    paginator = Paginator(results, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    totals = results.aggregate(
        total_aa=Sum('aa_votes'),
        total_ad=Sum('ad_votes'),
        total_adc=Sum('adc_votes'),
        total_apc=Sum('apc_votes'),
        total_lp=Sum('lp_votes'),
        total_pdp=Sum('pdp_votes'),
        grand_total=Sum('total_votes'),
    )
    
    context = {
        'allocation': allocation,
        'page_obj': page_obj,
        'search': search,
        'totals': totals,
    }
    return render(request, 'vote_allocation/allocation_full_data.html', context)

# def download_allocation_excel(request, allocation_id):
#     """Download allocation results as Excel file with complete data"""
#     allocation = get_object_or_404(VoteAllocation, id=allocation_id)
#     results = AllocatedResult.objects.filter(vote_allocation=allocation).select_related('polling_unit').order_by('polling_unit__sno')
    
#     # Create workbook
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Vote Allocation Results"
    
#     # Headers with allocation percentages
#     headers = [
#         'S/NO', 'STATE', 'LGA', 'RA', 'DELIM', 'REGISTER VOTER AS AT 2023',
#         'REGISTERED VOTER AS AT 2024', 'NO OF PVC COLLECTED', 'BALANCE OF UNCOLLECTED PVCs',
#         f'AA ({allocation.aa_percentage}%)', 
#         f'AD ({allocation.ad_percentage}%)', 
#         f'ADC ({allocation.adc_percentage}%)', 
#         f'APC ({allocation.apc_percentage}%)', 
#         f'LP ({allocation.lp_percentage}%)', 
#         f'PDP ({allocation.pdp_percentage}%)', 
#         'TOTAL'
#     ]
    
#     # Style headers
#     header_font = Font(bold=True, color="FFFFFF")
#     header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
#     for col, header in enumerate(headers, 1):
#         cell = ws.cell(row=1, column=col, value=header)
#         cell.font = header_font
#         cell.fill = header_fill
#         cell.alignment = Alignment(horizontal="center")
    
#     # Add allocation summary in the top right
#     ws.cell(row=1, column=len(headers) + 2, value=f"Allocation: {allocation.name}")
#     ws.cell(row=2, column=len(headers) + 2, value=f"Created: {allocation.created_at.strftime('%Y-%m-%d')}")
    
#     # Data rows
#     for row_num, result in enumerate(results, 2):
#         unit = result.polling_unit
#         ws.cell(row=row_num, column=1, value=unit.sno)
#         ws.cell(row=row_num, column=2, value=unit.state)
#         ws.cell(row=row_num, column=3, value=unit.lga)
#         ws.cell(row=row_num, column=4, value=unit.ra)
#         ws.cell(row=row_num, column=5, value=unit.delim)
#         ws.cell(row=row_num, column=6, value=unit.register_voter_2023)
#         ws.cell(row=row_num, column=7, value=unit.registered_voter_2024)
#         ws.cell(row=row_num, column=8, value=unit.pvc_collected)
#         ws.cell(row=row_num, column=9, value=unit.balance_uncollected)
#         ws.cell(row=row_num, column=10, value=result.aa_votes)
#         ws.cell(row=row_num, column=11, value=result.ad_votes)
#         ws.cell(row=row_num, column=12, value=result.adc_votes)
#         ws.cell(row=row_num, column=13, value=result.apc_votes)
#         ws.cell(row=row_num, column=14, value=result.lp_votes)
#         ws.cell(row=row_num, column=15, value=result.pdp_votes)
#         ws.cell(row=row_num, column=16, value=result.total_votes)
    
#     # Add totals row
#     total_row = len(results) + 2
#     ws.cell(row=total_row, column=1, value="TOTALS")
    
#     # Calculate totals
#     totals = results.aggregate(
#         total_aa=Sum('aa_votes'),
#         total_ad=Sum('ad_votes'),
#         total_adc=Sum('adc_votes'),
#         total_apc=Sum('apc_votes'),
#         total_lp=Sum('lp_votes'),
#         total_pdp=Sum('pdp_votes'),
#         grand_total=Sum('total_votes'),
#     )
    
#     ws.cell(row=total_row, column=10, value=totals['total_aa'])
#     ws.cell(row=total_row, column=11, value=totals['total_ad'])
#     ws.cell(row=total_row, column=12, value=totals['total_adc'])
#     ws.cell(row=total_row, column=13, value=totals['total_apc'])
#     ws.cell(row=total_row, column=14, value=totals['total_lp'])
#     ws.cell(row=total_row, column=15, value=totals['total_pdp'])
#     ws.cell(row=total_row, column=16, value=totals['grand_total'])
    
#     # Style totals row
#     for col in range(1, 17):
#         cell = ws.cell(row=total_row, column=col)
#         cell.font = Font(bold=True)
#         cell.fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
    
#     # Auto-adjust column widths
#     for column in ws.columns:
#         max_length = 0
#         column_letter = column[0].column_letter
#         for cell in column:
#             try:
#                 if len(str(cell.value)) > max_length:
#                     max_length = len(str(cell.value))
#             except:
#                 pass
#         adjusted_width = min(max_length + 2, 30)
#         ws.column_dimensions[column_letter].width = adjusted_width
    
#     # Save to BytesIO
#     output = BytesIO()
#     wb.save(output)
#     output.seek(0)
    
#     # Create response
#     filename = f"vote_allocation_{allocation.name.replace(' ', '_')}_{allocation.id}.xlsx"
#     response = HttpResponse(
#         output.getvalue(),
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
#     return response

def download_allocation_excel(request, allocation_id):
    """Download allocation results as Excel file with complete totals"""
    allocation = get_object_or_404(VoteAllocation, id=allocation_id)
    results = AllocatedResult.objects.filter(vote_allocation=allocation).select_related('polling_unit').order_by('polling_unit__sno')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Vote Allocation Results"
    
    headers = [
        'S/NO', 'STATE', 'LGA', 'RA', 'DELIM', 'REGISTER VOTER AS AT 2023',
        'REGISTERED VOTER AS AT 2024', 'NO OF PVC COLLECTED', 'BALANCE OF UNCOLLECTED PVCs',
        '45% PVC COLLECTION',
        f'AA ({allocation.aa_percentage}%)', 
        f'AD ({allocation.ad_percentage}%)', 
        f'ADC ({allocation.adc_percentage}%)', 
        f'APC ({allocation.apc_percentage}%)', 
        f'LP ({allocation.lp_percentage}%)', 
        f'PDP ({allocation.pdp_percentage}%)', 
        'TOTAL'
    ]
    
    # Style headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
    
    # Data rows
    for row_num, result in enumerate(results, 2):
        unit = result.polling_unit
        ws.cell(row=row_num, column=1, value=unit.sno)
        ws.cell(row=row_num, column=2, value=unit.state)
        ws.cell(row=row_num, column=3, value=unit.lga)
        ws.cell(row=row_num, column=4, value=unit.ra)
        ws.cell(row=row_num, column=5, value=unit.delim)
        ws.cell(row=row_num, column=6, value=unit.register_voter_2023)
        ws.cell(row=row_num, column=7, value=unit.registered_voter_2024)
        ws.cell(row=row_num, column=8, value=unit.pvc_collected)
        ws.cell(row=row_num, column=9, value=unit.balance_uncollected)
        ws.cell(row=row_num, column=10, value=int(unit.pvc_45_percent))  # Show as whole number
        ws.cell(row=row_num, column=11, value=result.aa_votes)
        ws.cell(row=row_num, column=12, value=result.ad_votes)
        ws.cell(row=row_num, column=13, value=result.adc_votes)
        ws.cell(row=row_num, column=14, value=result.apc_votes)
        ws.cell(row=row_num, column=15, value=result.lp_votes)
        ws.cell(row=row_num, column=16, value=result.pdp_votes)
        ws.cell(row=row_num, column=17, value=result.total_votes)
    
    # TOTALS ROW - Calculate totals for ALL numeric columns
    total_row = len(results) + 2
    ws.cell(row=total_row, column=1, value="TOTALS")
    
    # Calculate column totals
    total_reg_2024 = sum(unit.registered_voter_2024 for unit in PollingUnit.objects.filter(id__in=[r.polling_unit.id for r in results]))
    total_pvc_collected = sum(unit.pvc_collected for unit in PollingUnit.objects.filter(id__in=[r.polling_unit.id for r in results]))
    total_balance = sum(unit.balance_uncollected for unit in PollingUnit.objects.filter(id__in=[r.polling_unit.id for r in results]))
    total_pvc_45 = sum(unit.pvc_45_percent for unit in PollingUnit.objects.filter(id__in=[r.polling_unit.id for r in results]))
    
    vote_totals = results.aggregate(
        total_aa=Sum('aa_votes'),
        total_ad=Sum('ad_votes'),
        total_adc=Sum('adc_votes'),
        total_apc=Sum('apc_votes'),
        total_lp=Sum('lp_votes'),
        total_pdp=Sum('pdp_votes'),
        grand_total=Sum('total_votes'),
    )
    
    # Insert totals
    ws.cell(row=total_row, column=7, value=total_reg_2024)
    ws.cell(row=total_row, column=8, value=total_pvc_collected)
    ws.cell(row=total_row, column=9, value=total_balance)
    ws.cell(row=total_row, column=10, value=int(total_pvc_45))
    ws.cell(row=total_row, column=11, value=vote_totals['total_aa'])
    ws.cell(row=total_row, column=12, value=vote_totals['total_ad'])
    ws.cell(row=total_row, column=13, value=vote_totals['total_adc'])
    ws.cell(row=total_row, column=14, value=vote_totals['total_apc'])
    ws.cell(row=total_row, column=15, value=vote_totals['total_lp'])
    ws.cell(row=total_row, column=16, value=vote_totals['total_pdp'])
    ws.cell(row=total_row, column=17, value=vote_totals['grand_total'])
    
    # Style totals row
    for col in range(1, 18):
        cell = ws.cell(row=total_row, column=col)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="E8E8E8", end_color="E8E8E8", fill_type="solid")
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"vote_allocation_{allocation.name.replace(' ', '_')}_{allocation.id}.xlsx"
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# NEW - PDF Download Function
def download_allocation_pdf(request, allocation_id):
    """Download allocation results as PDF file"""
    allocation = get_object_or_404(VoteAllocation, id=allocation_id)
    results = AllocatedResult.objects.filter(vote_allocation=allocation).select_related('polling_unit').order_by('polling_unit__sno')[:100]  # Limit for PDF
    
    # Create PDF
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        alignment=1  # Center alignment
    )
    
    # Story container
    story = []
    
    # Title
    story.append(Paragraph(f"Vote Allocation Results: {allocation.name}", title_style))
    story.append(Spacer(1, 12))
    
    # Allocation details
    allocation_text = f"""
    <b>Allocation Percentages:</b><br/>
    AA: {allocation.aa_percentage}% | AD: {allocation.ad_percentage}% | ADC: {allocation.adc_percentage}%<br/>
    APC: {allocation.apc_percentage}% | LP: {allocation.lp_percentage}% | PDP: {allocation.pdp_percentage}%<br/>
    <b>Created:</b> {allocation.created_at.strftime('%Y-%m-%d %H:%M')}
    """
    story.append(Paragraph(allocation_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Table data
    table_data = [
        ['S/NO', 'State', 'LGA', 'Polling Unit', 'PVC', 'AA', 'AD', 'ADC', 'APC', 'LP', 'PDP', 'Total']
    ]
    
    for result in results:
        unit = result.polling_unit
        table_data.append([
            str(unit.sno),
            unit.state[:10],  # Truncate for PDF
            unit.lga[:10],
            unit.delim[:20],
            str(unit.pvc_collected),
            str(result.aa_votes),
            str(result.ad_votes),
            str(result.adc_votes),
            str(result.apc_votes),
            str(result.lp_votes),
            str(result.pdp_votes),
            str(result.total_votes)
        ])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Calculate totals
    totals = results.aggregate(
        total_aa=Sum('aa_votes'),
        total_ad=Sum('ad_votes'),
        total_adc=Sum('adc_votes'),
        total_apc=Sum('apc_votes'),
        total_lp=Sum('lp_votes'),
        total_pdp=Sum('pdp_votes'),
        grand_total=Sum('total_votes'),
    )
    
    # Add totals
    story.append(Spacer(1, 12))
    totals_text = f"""
    <b>TOTALS:</b><br/>
    AA: {totals['total_aa']} | AD: {totals['total_ad']} | ADC: {totals['total_adc']}<br/>
    APC: {totals['total_apc']} | LP: {totals['total_lp']} | PDP: {totals['total_pdp']}<br/>
    <b>Grand Total: {totals['grand_total']}</b>
    """
    story.append(Paragraph(totals_text, styles['Normal']))
    
    if len(results) == 100:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<i>Note: Only first 100 records shown in PDF. Download Excel for complete data.</i>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    # Return response
    output.seek(0)
    filename = f"vote_allocation_{allocation.name.replace(' ', '_')}_{allocation.id}.pdf"
    response = HttpResponse(output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@csrf_exempt
def validate_allocation(request):
    """AJAX endpoint to validate allocation percentages"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        total = (
            float(data.get('aa_percentage', 0)) +
            float(data.get('ad_percentage', 0)) +
            float(data.get('adc_percentage', 0)) +
            float(data.get('apc_percentage', 0)) +
            float(data.get('lp_percentage', 0)) +
            float(data.get('pdp_percentage', 0))
        )
        
        return JsonResponse({
            'total': round(total, 2),
            'is_valid': abs(total - 100.0) < 0.01
        })
    
    return JsonResponse({'error': 'Invalid request'})
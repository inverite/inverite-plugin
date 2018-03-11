# project/context_processors.py 
import os 

def export_vars(request):
    data = {}
    data['MERCHANT_NAME'] = os.environ.get('MERCHANT_NAME')
    return data


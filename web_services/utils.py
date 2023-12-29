def calculate_count(aop_count, uhd, high, mid, low, is_int = True):
    res = {}

    if is_int:
        res["uhd"] = int((aop_count*uhd)//100)
        res["high"] = int((aop_count*high)//100)
        res["mid"] = int((aop_count*mid)//100)
        res["low"] = int((aop_count*low)//100)
    else:
        res["uhd"] = int((aop_count*uhd)/100)
        res["high"] = int((aop_count*high)/100)
        res["mid"] = int((aop_count*mid)/100)
        res["low"] = int((aop_count*low)/100)

    print(res)
    
    return res

def slot_left(res, active_uhd, active_high, active_mid, active_low):
    print (res)
    res3 = {}
    res3["uhd"] = int(res["uhd"] - active_uhd)
    res3["high"] = int(res["high"] - active_high)
    res3["mid"] = int(res["mid"] - active_mid)
    res3["low"] = int(res["low"] - active_low)
    
    return res3
    
def get_bifercation_value(model):
    density_models_map = {
                    'uhd': {'TrueflexUHD'},
                    'high': {'TrueflexLCM', 'KIRANA'},
                    'medium': {'TRUEFLEXRegular', 'LMA', 'EFLEX'},
                    'low': {'RFK', 'CB', 'EKARTWM', 'EKARTOthers'}
                    }
    
    for dm in density_models_map:
        if model in density_models_map[dm]:
            return dm
    return False
    
    
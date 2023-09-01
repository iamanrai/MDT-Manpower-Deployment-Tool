def calculate_count(aop_count, uhd, high, mid, low, is_int = True):
    res = {}

    if is_int:
        res["uhd"] = (aop_count*uhd)//100
        res["high"] = (aop_count*high)//100
        res["mid"] = (aop_count*mid)//100
        res["low"] = (aop_count*low)//100
    else:
        res["uhd"] = (aop_count*uhd)/100
        res["high"] = (aop_count*high)/100
        res["mid"] = (aop_count*mid)/100
        res["low"] = (aop_count*low)/100

    return res

def slot_left(res, active_uhd, active_high, active_mid, active_low):
    print (res)
    res3 = {}
    res3["uhd"] = res["uhd"] - active_uhd
    res3["high"] = res["high"] - active_high
    res3["mid"] = res["mid"] - active_mid
    res3["low"] = res["low"] - active_low
    
    return res3
    
    
def is_leap_year(year):
    """
    指定された年が閏年かどうかを判断する関数です。
    
    閏年は以下の条件を満たします：
    1. 4で割り切れるが、100で割り切れない
    2. 100で割り切れるが、400で割り切れる
    
    Args:
        year (int): 判定する年
    
    Returns:
        bool: 閏年であればTrue、閏年でない場合はFalse
    """
    if year % 4 != 0:
        return False
    # 年が4で割り切れていない場合、閏年ではありません
    elif year % 100 != 0:
        return True
    # 4で割り切れるが、100で割り切れない場合、閏年です
    elif year % 100 != 0:
        return True
    # 100で割り切れるが、400で割り切れる場合、閏年です
    else:
        return year % 400 == 0

# テスト用のコード
years = range(1900, 2100)
for year in years:
    print(f"{year} は閏年です：{is_leap_year(year)}")

from convert_sql_to_csv import main
from zip_results_folder import zip_folder

# 1000000_1010000  1080000_1090000  1160000_1170000  
# 1010000_1020000  1090000_1100000  1170000_1180000  
# 1020000_1030000  1100000_1110000  1180000_1190000  
# 1030000_1040000  1110000_1120000  1190000_1200000  
# 1040000_1050000  1120000_1130000  1200000_1210000  
# 1050000_1060000  1130000_1140000  1210000_1220000  
# 1060000_1070000  1140000_1150000  1220000_1230000  
# 1070000_1080000  1150000_1160000  1230000_1240000  


index_list = [
    (610000, 620000),
    (620000, 630000),
    (630000, 640000),
    (640000, 650000),
    (650000, 660000),
    (660000, 670000),
    (670000, 680000),
    (680000, 690000),
]

for index in index_list:
    main(index[0], index[1])
    zip_folder(f'US_{index[0]}_{index[1]}', f'US_{index[0]}_{index[1]}.zip')
    print(f"US_{index[0]}_{index[1]}.zip has been created successfully")

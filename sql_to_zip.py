from convert_sql_to_csv import main
from zip_results_folder import zip_folder


index_list = [
    (730000, 740000),
    (740000, 750000),
    (750000, 760000),
    (760000, 770000),
    (770000, 780000),
    (780000, 790000),
    # (790000, 800000),
    # (800000, 810000),
    # (810000, 820000),
    # (820000, 830000),
    # (830000, 840000),
    # (840000, 850000),
    # (850000, 860000),
    # (860000, 870000),
    # (870000, 880000),
    # (880000, 890000),
    # (890000, 900000),
    # (900000, 910000),
    # (910000, 920000),
    # (920000, 930000),
    # (930000, 940000),
    # (940000, 950000),
]

for index in index_list:
    main(index[0], index[1])
    zip_folder(f'US_{index[0]}_{index[1]}', f'US_{index[0]}_{index[1]}.zip')
    print(f"US_{index[0]}_{index[1]}.zip has been created successfully")

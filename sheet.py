import gspread

sa = gspread.service_account("osu-pool-bot-46950f86d0d5.json")
sh = sa.open("osu! Pool Bot Base Sheet")
wks = sh.worksheet("Pool Base")


def column_name(number):
    result = ""
    while number >= 0:
        remainder = number % 26
        result = chr(65 + remainder) + result
        number = number // 26 - 1

    return result


def coordinate_to_range(coord1, coord2):
    # Unpack coordinates
    row1, col1 = coord1
    row2, col2 = coord2

    # Convert coordinates to column names
    col_name1 = column_name(col1)
    col_name2 = column_name(col2)

    # Construct the Google Sheets range
    sheet_range = f"{col_name1}{row1 + 1}:{col_name2}{row2 + 1}"

    return sheet_range


def generate_pool_sheet(pool):
    wks.clear()
    rows = len(pool)
    cols = len(pool[0])
    range = coordinate_to_range((0, 0), (rows, cols))
    wks.update(pool, range, value_input_option='USER_ENTERED')

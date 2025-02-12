from datetime import datetime

def extract_datetime_from_filename(filename):
    print(f"filename {filename}")
    parts = filename.split(" at ")
    date_part = parts[0].split(" ")[-1]  # Get the date part
    time_part = parts[1].split(".ogg")[0]  # Get the time part, excluding the '.ogg' extension
    time_part = time_part.replace('.', ':')
    datetime_str = f"{date_part} {time_part}"
    print(f"datetime_str {datetime_str}")
    # return datetime.strptime(datetime_str, '%Y-%m-%d %I:%M:%S %p')
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
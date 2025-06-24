import json
import os

def load_all_jsons(root_folder: str) -> dict:
    result = {}
    for town in os.listdir(root_folder):
        town_path = os.path.join(root_folder, town)
        if os.path.isdir(town_path):
            result[town] = {}
            for file in os.listdir(town_path):
                if file.endswith(".json"):
                    file_path = os.path.join(town_path, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            result[town][file] = json.load(f)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding {file_path}: {e}")
    return result

def calculate_temperatures_for_city(data: dict) -> tuple[float, float, float]:
    temperatures = []

    for file in data:
        content = data[file]
        hourly_data = content.get("hourly", [])
        for hour in hourly_data:
            try:
                temp = float(hour["temp"])
                temperatures.append(temp)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping entry in file {file} due to error: {e}")

    if not temperatures:
        return 0.0, 0.0, 0.0

    mean_temp = round(sum(temperatures) / len(temperatures), 2)
    min_temp = round(min(temperatures), 2)
    max_temp = round(max(temperatures), 2)

    return mean_temp, min_temp, max_temp

def calculate_wind_speed_for_city(data: dict) -> tuple[float, float, float]:
    wind_speeds = []

    for file in data:
        content = data[file]
        hourly_data = content.get("hourly", [])
        for hour in hourly_data:
            try:
                wind_speed = float(hour["wind_speed"])
                wind_speeds.append(wind_speed)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping entry in file {file} due to error: {e}")

    if not wind_speeds:
        return 0.0, 0.0, 0.0

    mean_wind_speed = round(sum(wind_speeds) / len(wind_speeds), 2)
    min_wind_speed = round(min(wind_speeds), 2)
    max_wind_speed = round(max(wind_speeds), 2)

    return mean_wind_speed, min_wind_speed, max_wind_speed



def main():
    data = load_all_jsons("source_data")
    print("Sample file:", data["Madrid"]["2021_09_25.json"])

    mean_temp, min_temp, max_temp = calculate_temperatures_for_city(data["Merida"])
    print(f"Mean temperature: {mean_temp:.2f}, Min temperature: {min_temp:.2f}, "
          f"Max temperature: {max_temp:.2f}")

    mean_wind_speed, min_wind_speed, max_wind_speed = calculate_wind_speed_for_city(data["Merida"])
    print(f"Mean wind speed: {mean_wind_speed:.2f}, "
          f"Min wind speed: {min_wind_speed:.2f}, Max wind speed: {max_wind_speed:.2f}")


if __name__ == "__main__":
    main()
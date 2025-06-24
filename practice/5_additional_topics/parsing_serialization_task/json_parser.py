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


def analyze_country_weather(data: dict) -> None:
    city_temps = {}
    city_winds = {}

    for city, city_data in data.items():
        mean_temp, _, _ = calculate_temperatures_for_city(city_data)
        mean_wind, _, _ = calculate_wind_speed_for_city(city_data)

        city_temps[city] = mean_temp
        city_winds[city] = mean_wind

    if not city_temps or not city_winds:
        print("No data available for analysis.")
        return

    country_mean_temp = round(sum(city_temps.values()) / len(city_temps), 2)
    country_mean_wind = round(sum(city_winds.values()) / len(city_winds), 2)

    coldest_city = min(city_temps, key=city_temps.get)
    warmest_city = max(city_temps, key=city_temps.get)
    windiest_city = max(city_winds, key=city_winds.get)

    print(f"Country-wide mean temperature: {country_mean_temp:.2f}°C")
    print(f"Country-wide mean wind speed: {country_mean_wind:.2f} m/s\n")

    print(f"Coldest city: {coldest_city} ({city_temps[coldest_city]:.2f}°C)")
    print(f"Warmest city: {warmest_city} ({city_temps[warmest_city]:.2f}°C)")
    print(f"Windiest city: {windiest_city} ({city_winds[windiest_city]:.2f} m/s)")


def main():
    data = load_all_jsons("source_data")
    analyze_country_weather(data)


if __name__ == "__main__":
    main()
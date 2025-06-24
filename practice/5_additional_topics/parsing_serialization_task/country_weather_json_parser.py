import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import re

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

def extract_values(data: dict, key: str) -> list[float]:
    values = []
    for content in data.values():
        hourly = content.get("hourly", [])
        for hour in hourly:
            try:
                values.append(float(hour[key]))
            except (KeyError, ValueError, TypeError):
                pass
    return values

def calculate_stats(data: dict, key: str) -> tuple[float, float, float]:
    values = extract_values(data, key)
    if not values:
        return 0.0, 0.0, 0.0
    return round(sum(values) / len(values), 2), round(min(values), 2), round(max(values), 2)

def sanitize_city_name(city_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', city_name)
    if re.match(r'^\d', sanitized):
        sanitized = "_" + sanitized
    return sanitized

def extract_date_from_data(data: dict) -> str:
    for city_data in data.values():
        for filename in city_data:
            try:
                base_name = filename.replace(".json", "")
                date_obj = datetime.strptime(base_name, "%Y_%m_%d")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
    return datetime.today().strftime("%Y-%m-%d")

def write_weather_to_xml(data: dict, country_name: str, output_file: str):
    date_str = extract_date_from_data(data)

    city_metrics = {}
    for city, city_files in data.items():
        city_metrics[city] = {
            "mean_temp": calculate_stats(city_files, "temp")[0],
            "min_temp": calculate_stats(city_files, "temp")[1],
            "max_temp": calculate_stats(city_files, "temp")[2],
            "mean_wind": calculate_stats(city_files, "wind_speed")[0],
            "min_wind": calculate_stats(city_files, "wind_speed")[1],
            "max_wind": calculate_stats(city_files, "wind_speed")[2],
        }

    temps = {c: m["mean_temp"] for c, m in city_metrics.items()}
    winds = {c: m["mean_wind"] for c, m in city_metrics.items()}

    mean_country_temp = round(sum(temps.values()) / len(temps), 2) if temps else 0.0
    mean_country_wind = round(sum(winds.values()) / len(winds), 2) if winds else 0.0

    coldest_city = min(temps, key=temps.get) if temps else ""
    warmest_city = max(temps, key=temps.get) if temps else ""
    windiest_city = max(winds, key=winds.get) if winds else ""

    weather = ET.Element("weather", country=country_name, date=date_str)

    ET.SubElement(
        weather,
        "summary",
        mean_temp=str(mean_country_temp),
        mean_wind_speed=str(mean_country_wind),
        coldest_place=coldest_city,
        warmest_place=warmest_city,
        windiest_place=windiest_city,
    )

    cities = ET.SubElement(weather, "cities")
    for city, metrics in city_metrics.items():
        ET.SubElement(
            cities,
            sanitize_city_name(city),
            mean_temp=str(metrics["mean_temp"]),
            mean_wind_speed=str(metrics["mean_wind"]),
            min_temp=str(metrics["min_temp"]),
            min_wind_speed=str(metrics["min_wind"]),
            max_temp=str(metrics["max_temp"]),
            max_wind_speed=str(metrics["max_wind"]),
        )

    tree = ET.ElementTree(weather)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def analyze_country_weather(data: dict) -> None:
    temps = {}
    winds = {}

    for city, city_data in data.items():
        temps[city] = calculate_stats(city_data, "temp")[0]
        winds[city] = calculate_stats(city_data, "wind_speed")[0]

    if not temps or not winds:
        print("No data available for analysis.")
        return

    country_mean_temp = round(sum(temps.values()) / len(temps), 2)
    country_mean_wind = round(sum(winds.values()) / len(winds), 2)

    coldest_city = min(temps, key=temps.get)
    warmest_city = max(temps, key=temps.get)
    windiest_city = max(winds, key=winds.get)

    print(f"Country-wide mean temperature: {country_mean_temp:.2f}°C")
    print(f"Country-wide mean wind speed: {country_mean_wind:.2f} m/s\n")

    print(f"Coldest city: {coldest_city} ({temps[coldest_city]:.2f}°C)")
    print(f"Warmest city: {warmest_city} ({temps[warmest_city]:.2f}°C)")
    print(f"Windiest city: {windiest_city} ({winds[windiest_city]:.2f} m/s)")

def main():
    data = load_all_jsons("source_data")
    analyze_country_weather(data)
    write_weather_to_xml(data, country_name="Spain", output_file="tests/weather_report.xml")

if __name__ == "__main__":
    main()

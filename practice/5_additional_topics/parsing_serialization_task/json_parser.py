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

def calculate_temperature_values(data: dict) -> tuple[float, float, float]:
    temperatures = []

    for town in data:
        for file in data[town]:
            content = data[town][file]
            hourly_data = content.get("hourly", [])
            for hour in hourly_data:
                try:
                    temp = float(hour["temp"])
                    temperatures.append(temp)
                except (KeyError, ValueError, TypeError) as e:
                    print(f"Skipping {town}/{file} entry due to error: {e}")

    if not temperatures:
        return 0.0, 0.0, 0.0

    mean_temp = sum(temperatures) / len(temperatures)
    min_temp = min(temperatures)
    max_temp = max(temperatures)

    return mean_temp, min_temp, max_temp



def main():
    data = load_all_jsons("source_data")
    print("Sample file:", data["Madrid"]["2021_09_25.json"])

    avg, min_temp, max_temp = calculate_temperature_values(data)
    print(f"Average: {avg:.2f}, Min: {min_temp:.2f}, Max: {max_temp:.2f}")


if __name__ == "__main__":
    main()
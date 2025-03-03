import os

from collections import defaultdict
from typing import Generator

ERROR_CODES = {
    0: "Battery device error",
    1: "Temperature device error",
    2: "Threshold central error"
}

SENSOR_ID_INDEX = 2
STATE_INDEX = -1
S_P1_INDEX = 6
S_P2_INDEX = 13

SENSOR_STATE_OK = "02"
SENSOR_STATE_FAILED = "DD"


def read_log_file(file_path: str) -> Generator[str, None, None]:
    """
    Reads a log file line by line and yields lines containing "BIG".
    """
    with open(file_path, "r", encoding="utf-8") as log_file:
        for line in log_file:
            if "BIG" in line:
                yield line


def parse_log_message(line: str) -> tuple:
    """
    Parses one line of a log file into parts.
    """
    parts = line.rsplit(">", 1)[-1].strip(" '\n").rstrip(";").split(";")

    sensor_id = parts[SENSOR_ID_INDEX]
    state = parts[STATE_INDEX]
    s_p1 = parts[S_P1_INDEX]
    s_p2 = parts[S_P2_INDEX]

    return sensor_id, state, s_p1, s_p2


def process_sensor_data(file_path: str) -> tuple:
    """
    Processes sensor data, identifies successful and unsuccessful sensors.
    """
    sensors_ok = defaultdict(int)
    sensors_failed = {}

    for line in read_log_file(file_path):
        sensor_id, state, s_p1, s_p2 = parse_log_message(line)

        if state == SENSOR_STATE_FAILED:
            sensors_failed[sensor_id] = (s_p1, s_p2)
            sensors_ok.pop(sensor_id, None)
            continue

        if sensor_id in sensors_failed:
            continue

        if state == SENSOR_STATE_OK:
            sensors_ok[sensor_id] += 1

    return sensors_ok, sensors_failed


def decode_error_flags(sensor_failed: dict) -> None:
    """
    Decodes sensor errors and displays messages.
    """
    for sensor_id, (s_p1, s_p2) in sensor_failed.items():
        combined_str = s_p1[:-1].lstrip("-") + s_p2.lstrip("-")
        pairs = [combined_str[i:i + 2] for i in range(0, len(combined_str), 2)]

        binary_values = [bin(int(pair))[2:].zfill(8) for pair in pairs]
        error_flags = [binary[4] for binary in binary_values]
        errors = [ERROR_CODES[i] for i, flag in enumerate(error_flags) if flag == "1"]

        print(
            f"{sensor_id} - {', '.join(errors) if errors else 'Unknown device error'}"
        )


def display_results(
        sensors_ok: dict,
        sensors_failed: dict,
) -> None:
    """
    Displays statistics and error details for sensor data processing results.
    """
    successful_sensors, failed_sensors = len(sensors_ok), len(sensors_failed)

    print(f"ALL big messages: {successful_sensors + failed_sensors}")
    print(f"Successful big messages: {successful_sensors}")
    print(f"Failed big messages: {failed_sensors}\n")

    decode_error_flags(sensors_failed)

    print("\nSuccess messages count:")
    for sensor_id, count in sensors_ok.items():
        print(f"{sensor_id}: {count}")


def process_logs(file_path: str) -> None:
    """
    Start log file processing and displays results.
    """
    sensor_ok, sensor_failed = process_sensor_data(file_path)
    display_results(sensor_ok, sensor_failed)


def main() -> None:
    file_path = os.path.join(os.path.dirname(__file__), "app_2.log")
    process_logs(file_path)


if __name__ == "__main__":
    main()

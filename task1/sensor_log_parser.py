from collections import defaultdict

ERROR_CODES = {
    0: "Battery device error",
    1: "Temperature device error",
    2: "Threshold central error"
}


def read_log_file(file_path: str) -> list:
    with open(file_path, "r", encoding="utf-8") as log_file:
        for line in log_file:
            if "BIG" in line:
                yield line


def parse_log_message(line: str) -> tuple:
    """
    Parses one line of a log file into parts.
    """
    message = line.split(">")[-1].strip()
    parts = message.split(";")

    sensor_id = parts[2]
    state = parts[-2]
    s_p1 = parts[6]
    s_p2 = parts[13]

    return sensor_id, state, s_p1, s_p2


def process_sensor_data(sensor_data: list) -> tuple:
    """
    Processes sensor data, identifies successful and unsuccessful sensors.
    """
    sensor_ok = defaultdict(int)
    sensor_failed = {}

    for line in sensor_data:
        parsed_data = parse_log_message(line)

        sensor_id, state, s_p1, s_p2 = parsed_data

        if sensor_id in sensor_failed:
            continue

        if state == "DD":
            sensor_failed[sensor_id] = (s_p1, s_p2)
            sensor_ok.pop(sensor_id, None)
            continue

        if state == "02":
            sensor_ok[sensor_id] += 1

    return sensor_ok, sensor_failed


def decode_error_flags(sensor_failed: dict) -> None:
    """
    Decodes sensor errors and displays messages.
    """
    for sensor_id, (s_p1, s_p2) in sensor_failed.items():
        combined_str = s_p1[:-1] + s_p2
        pairs = [combined_str[i:i + 2] for i in range(0, len(combined_str), 2)]

        binary_values = [bin(int(pair))[2:].zfill(8) for pair in pairs]
        error_flags = [binary[4] for binary in binary_values]
        errors = [ERROR_CODES[i] for i, flag in enumerate(error_flags) if flag == "1"]

        print(
            f"{sensor_id} - {', '.join(errors) if errors else 'Unknown device error'}"
        )


def display_results(
        sensor_ok: dict,
        sensor_failed: dict,
) -> None:
    successful_sensors, failed_sensors = len(sensor_ok), len(sensor_failed)

    print(f"ALL big messages: {successful_sensors + failed_sensors}")
    print(f"Successful big messages: {successful_sensors}")
    print(f"Failed big messages: {failed_sensors}\n")

    decode_error_flags(sensor_failed)

    print("\nSuccess messages count:")
    for sensor_id, count in sensor_ok.items():
        print(f"{sensor_id}: {count}")


def process_logs(file_path: str) -> None:
    sensor_data = read_log_file(file_path)
    sensor_ok, sensor_failed = process_sensor_data(sensor_data)
    display_results(sensor_ok, sensor_failed)


def main() -> None:
    process_logs("app_2.log")


if __name__ == "__main__":
    main()

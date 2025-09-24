import requests
import zipfile
import io
import csv

def get_septa_bus_routes():
    """
    Downloads and parses SEPTA's GTFS data to extract bus route information.

    This function fetches the latest GTFS zip file from SEPTA's website,
    finds the 'google_bus.zip' file within it, opens that nested zip file,
    and then filters the 'routes.txt' data to return information only for
    bus routes (where route_type is 3).

    Returns:
        list: A list of dictionaries, where each dictionary represents a bus route
              and contains the headers from routes.txt as keys.
              Returns an empty list if an error occurs.
    """
    # URL for SEPTA's GTFS data. This is the updated, correct URL.
    gtfs_url = "https://www3.septa.org/developer/gtfs_public.zip"
    bus_routes = []

    print(f"Downloading GTFS data from {gtfs_url}...")

    try:
        # Make an HTTP GET request to download the file
        response = requests.get(gtfs_url)
        # Raise an exception if the download failed
        response.raise_for_status()
        print("Download successful.")

        # The downloaded content is binary, so we treat it as a file in memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf_outer:
            # Check if 'google_bus.zip' is in the main zip file
            if 'google_bus.zip' not in zf_outer.namelist():
                print("Error: 'google_bus.zip' not found in the main archive.")
                return []

            print("Found 'google_bus.zip', extracting bus data...")
            # Read the nested zip file into memory
            bus_zip_data = zf_outer.read('google_bus.zip')

            # Open the nested zip file from the in-memory data
            with zipfile.ZipFile(io.BytesIO(bus_zip_data)) as zf_inner:
                # Check if 'routes.txt' is in the nested zip file
                if 'routes.txt' not in zf_inner.namelist():
                    print("Error: 'routes.txt' not found in 'google_bus.zip'.")
                    return []

                # Read the 'routes.txt' file from the zip archive
                with zf_inner.open('routes.txt', 'r') as f:
                    # The file is text, so we decode it and read it with the csv module
                    # Using io.TextIOWrapper to handle the binary-to-text conversion
                    reader = csv.DictReader(io.TextIOWrapper(f, 'utf-8'))

                    print("Parsing 'routes.txt' for bus routes...")
                    # Iterate over each row in the CSV
                    for row in reader:
                        # According to the GTFS specification, 'route_type' = 3 signifies a bus.
                        # See: https://gtfs.org/schedule/reference/#routestxt
                        if row.get('route_type') == '3':
                            bus_routes.append(row)
            
            print(f"Found {len(bus_routes)} bus routes.")
            return bus_routes

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the data: {e}")
        return []
    except zipfile.BadZipFile:
        print("Error: The downloaded file is not a valid zip archive.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == '__main__':
    # This block will run when the script is executed directly
    septa_buses = get_septa_bus_routes()

    if septa_buses:
        print("\n--- Sample of SEPTA Bus Routes ---")
        # Print the details for the first 5 bus routes found
        for route in septa_buses[:150]:
            print(
                f"Route ID: {route.get('route_id', 'N/A')}, "
                f"Short Name: {route.get('route_short_name', 'N/A')}, "
                f"Long Name: {route.get('route_long_name', 'N/A')}"
            )

        print(f"\nTotal bus routes parsed: {len(septa_buses)}")



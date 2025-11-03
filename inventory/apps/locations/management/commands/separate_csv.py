import csv
from pathlib import Path

def separate_csv(input_file_path):
    """
    Reads the input CSV and separates it into distinct District, Mandal, and Village CSVs.
    Uses the unique India codes (DstCodeInd, MndCodeInd, VillCodeIn) for uniqueness.
    If an India code is 'NA' or empty, the row is included regardless of potential duplicates.
    """
    input_path = Path(input_file_path)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return

    # Sets to track unique India codes for districts and mandals to avoid duplicates
    # (only when the code is not NA/empty)
    seen_districts_ind = set()
    seen_mandals_ind = set()
    seen_villages_ind = set() # Add set for villages based on India code

    # Output file paths
    districts_path = input_path.parent / "districts.csv"
    mandals_path = input_path.parent / "mandals.csv"
    villages_path = input_path.parent / "villages.csv"

    # Define headers for the output CSVs
    district_headers = ['State', 'StCodeAP', 'StCodeInd', 'District', 'DstCodeAP', 'DstCodeInd']
    mandal_headers = ['State', 'StCodeAP', 'StCodeInd', 'District', 'DstCodeAP', 'DstCodeInd', 'Mandal', 'MndCodeAP', 'MndCodeInd']
    village_headers = ['State', 'StCodeAP', 'StCodeInd', 'District', 'DstCodeAP', 'DstCodeInd', 'Mandal', 'MndCodeAP', 'MndCodeInd', 'Village', 'VillCodeAP', 'VillCodeIn', 'Shape_Area']

    # Counters for reporting
    district_count = 0
    mandal_count = 0
    village_count = 0

    print(f"Reading data from: {input_path}")
    print(f"Writing separated data to:\n  - {districts_path}\n  - {mandals_path}\n  - {villages_path}")

    with open(input_path, newline='', encoding='utf-8-sig') as infile, \
         open(districts_path, 'w', newline='', encoding='utf-8') as districts_file, \
         open(mandals_path, 'w', newline='', encoding='utf-8') as mandals_file, \
         open(villages_path, 'w', newline='', encoding='utf-8') as villages_file:

        reader = csv.DictReader(infile)

        # Normalize headers (remove leading/trailing spaces)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        print(f"Headers found in input file: {reader.fieldnames}")

        # Check for required columns
        required_cols = {'State', 'StCodeAP', 'StCodeInd', 'District', 'DstCodeAP', 'DstCodeInd', 'Mandal', 'MndCodeAP', 'MndCodeInd', 'Village', 'VillCodeAP', 'VillCodeIn', 'Shape_Area'}
        if not required_cols.issubset(set(reader.fieldnames)):
            missing = required_cols - set(reader.fieldnames)
            print(f"Error: Missing required columns in input file: {missing}")
            return

        # Create DictWriters for the output files
        district_writer = csv.DictWriter(districts_file, fieldnames=district_headers)
        mandal_writer = csv.DictWriter(mandals_file, fieldnames=mandal_headers)
        village_writer = csv.DictWriter(villages_file, fieldnames=village_headers)

        # Write headers to the new files
        district_writer.writeheader()
        mandal_writer.writeheader()
        village_writer.writeheader()

        for row in reader:
            # --- Extract data from the current row ---
            state = row['State'].strip()
            st_code_ap = row['StCodeAP'].strip()
            st_code_ind = row['StCodeInd'].strip()

            district_name = row['District'].strip()
            dst_code_ap = row['DstCodeAP'].strip()
            dst_code_ind_raw = row['DstCodeInd'].strip()
            dst_code_ind = dst_code_ind_raw if dst_code_ind_raw and dst_code_ind_raw != 'NA' else None

            mandal_name = row['Mandal'].strip()
            mnd_code_ap = row['MndCodeAP'].strip()
            mnd_code_ind_raw = row['MndCodeInd'].strip()
            mnd_code_ind = mnd_code_ind_raw if mnd_code_ind_raw and mnd_code_ind_raw != 'NA' else None

            village_name = row['Village'].strip().replace('"', '').replace('\n', ' ').strip() # Clean village name as in original script
            vill_code_ap = row['VillCodeAP'].strip()
            vill_code_ind_raw = row['VillCodeIn'].strip() # Note: Original script used 'VillCodeIn', header says 'VillCodeIn'
            vill_code_ind = vill_code_ind_raw if vill_code_ind_raw and vill_code_ind_raw != 'NA' else None
            shape_area = row['Shape_Area'].strip() # Assuming Shape_Area is always present

            # --- Process Village Row ---
            # Skip villages where AP code is 'NA' or empty (as per original logic)
            if vill_code_ap and vill_code_ap != 'NA':
                # Also check if district/mandal codes are missing (as per original logic)
                if dst_code_ap and mnd_code_ap and dst_code_ap != 'NA' and mnd_code_ap != 'NA':
                    # Determine if the village should be written based on India code uniqueness
                    write_village = False
                    if vill_code_ind is None: # If India code is NA/empty, always write
                        write_village = True
                    else: # If India code is present, check if it's unique
                        if vill_code_ind not in seen_villages_ind:
                            seen_villages_ind.add(vill_code_ind)
                            write_village = True
                        # else: do not write if code exists and is not NA/empty

                    if write_village:
                        village_writer.writerow({
                            'State': state,
                            'StCodeAP': st_code_ap,
                            'StCodeInd': st_code_ind,
                            'District': district_name,
                            'DstCodeAP': dst_code_ap,
                            'DstCodeInd': dst_code_ind,
                            'Mandal': mandal_name,
                            'MndCodeAP': mnd_code_ap,
                            'MndCodeInd': mnd_code_ind,
                            'Village': village_name,
                            'VillCodeAP': vill_code_ap,
                            'VillCodeIn': vill_code_ind_raw if vill_code_ind_raw != 'NA' else '', # Convert 'NA' back to empty string for clarity in output
                            'Shape_Area': shape_area
                        })
                        village_count += 1
                    # else: Skip if code exists and is not NA/empty
                else:
                    print(f"Skipping village row due to missing/NA district or mandal AP codes: {row}")
            # else: Skip this row entirely if village AP code is invalid (matches original skip logic)

            # --- Process Mandal Row ---
            # Also check if district/mandal codes are missing (as per original logic)
            if mnd_code_ap and dst_code_ap and mnd_code_ap != 'NA' and dst_code_ap != 'NA':
                # Determine if the mandal should be written based on India code uniqueness
                write_mandal = False
                if mnd_code_ind is None: # If India code is NA/empty, always write
                    write_mandal = True
                else: # If India code is present, check if it's unique
                    if mnd_code_ind not in seen_mandals_ind:
                        seen_mandals_ind.add(mnd_code_ind)
                        write_mandal = True
                    # else: do not write if code exists and is not NA/empty

                if write_mandal:
                    mandal_writer.writerow({
                        'State': state,
                        'StCodeAP': st_code_ap,
                        'StCodeInd': st_code_ind,
                        'District': district_name,
                        'DstCodeAP': dst_code_ap,
                        'DstCodeInd': dst_code_ind,
                        'Mandal': mandal_name,
                        'MndCodeAP': mnd_code_ap,
                        'MndCodeInd': mnd_code_ind_raw if mnd_code_ind_raw != 'NA' else '' # Output original 'NA' or value
                    })
                    mandal_count += 1
                # else: Skip if code exists and is not NA/empty
            # else: Skip adding mandal if AP codes are missing (matches original logic)

            # --- Process District Row ---
            # Also check if district AP code is missing (as per original logic)
            if dst_code_ap and dst_code_ap != 'NA':
                # Determine if the district should be written based on India code uniqueness
                write_district = False
                if dst_code_ind is None: # If India code is NA/empty, always write
                    write_district = True
                else: # If India code is present, check if it's unique
                    if dst_code_ind not in seen_districts_ind:
                        seen_districts_ind.add(dst_code_ind)
                        write_district = True
                    # else: do not write if code exists and is not NA/empty

                if write_district:
                    district_writer.writerow({
                        'State': state,
                        'StCodeAP': st_code_ap,
                        'StCodeInd': st_code_ind,
                        'District': district_name,
                        'DstCodeAP': dst_code_ap,
                        'DstCodeInd': dst_code_ind_raw if dst_code_ind_raw != 'NA' else '' # Output original 'NA' or value
                    })
                    district_count += 1
                # else: Skip if code exists and is not NA/empty
            # else: Skip adding district if AP code is missing (matches original logic)


    print("\nSeparation complete!")
    print(f"  - Wrote {district_count} unique districts (or districts with NA/empty Ind code) to {districts_path}")
    print(f"  - Wrote {mandal_count} unique mandals (or mandals with NA/empty Ind code) to {mandals_path}")
    print(f"  - Wrote {village_count} valid villages (or villages with NA/empty Ind code) to {villages_path}")


# --- Main execution ---
if __name__ == "__main__":
    # Specify the path to your input CSV file
    input_csv_file = "Admin_codes_AP.csv" # Change this if your file is in a different location
    separate_csv(input_csv_file)
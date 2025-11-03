import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.locations.models import District, Mandal, Village

class Command(BaseCommand):
    help = "Import Villages from villages.csv, checking uniqueness on Vill Ind code. Links Mandals using Mandal Ind code."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='villages.csv',
            help='Path to villages CSV file (default: villages.csv in same folder)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Village data before import',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_first = options['clear']

        # Resolve full path
        cmd_dir = Path(__file__).parent
        csv_path = cmd_dir / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"Village CSV file not found: {csv_path}")

        self.stdout.write(f"Loading Village data from: {csv_path}")

        # Optional: Clear existing data
        if clear_first:
            self.stdout.write("Clearing existing Village data...")
            Village.objects.all().delete()
            self.stdout.write("Cleared Villages.")

        created = 0
        skipped = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames] # Normalize headers
            self.stdout.write(f"Village CSV Headers: {reader.fieldnames}")

            required_cols = {'Village', 'VillCodeAP', 'MndCodeInd', 'DstCodeInd'} # Need Ind codes for linking and basic checks, AP code for creation
            if not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames)
                raise ValueError(f"Village CSV: Missing required columns: {missing}")

            for row in reader:
                village_name = row['Village'].strip().replace('"', '').replace('\n', ' ').strip() # Clean name as before
                vill_code_ap = row['VillCodeAP'].strip()
                mnd_code_ind_raw = row['MndCodeInd'].strip() # Use Ind code for linking
                dst_code_ind_raw = row['DstCodeInd'].strip() # Use Ind code for linking
                vill_code_ind_raw = row.get('VillCodeIn', '').strip() # Use get() in case column name varies slightly

                # Process codes, handling 'NA'
                mnd_code_ind = mnd_code_ind_raw if mnd_code_ind_raw and mnd_code_ind_raw != 'NA' else None
                dst_code_ind = dst_code_ind_raw if dst_code_ind_raw and dst_code_ind_raw != 'NA' else None
                vill_code_ind = vill_code_ind_raw if vill_code_ind_raw and vill_code_ind_raw != 'NA' else None

                # Skip rows with missing essential Ind codes (used for linking)
                # If Ind codes are missing, we cannot reliably link using Ind codes
                if mnd_code_ind is None or dst_code_ind is None:
                    self.stdout.write(f"Skipping Village row with missing/NA Ind codes (Mandal or District): {row}", self.style.WARNING)
                    skipped += 1
                    continue

                # Skip rows with missing essential Village AP code (used for creation)
                if not vill_code_ap or vill_code_ap == 'NA':
                    self.stdout.write(f"Skipping Village row with missing/NA Village AP code: {row}", self.style.WARNING)
                    skipped += 1
                    continue

                # Find the associated Mandal using the MndCodeInd
                # This assumes MndCodeInd is unique for Mandals in the database.
                try:
                    mandal = Mandal.objects.get(mandal_code_ind=mnd_code_ind)
                    # Verify the associated district Ind code matches for consistency using District Ind code from CSV
                    if mandal.district.district_code_ind != dst_code_ind:
                         self.stdout.write(f"Warning: Village's District Ind code '{dst_code_ind}' doesn't match found Mandal '{mandal.mandal_name}' -> District Ind code '{mandal.district.district_code_ind}'. Skipping.", self.style.WARNING)
                         skipped += 1
                         continue
                except Mandal.DoesNotExist:
                    self.stdout.write(f"Warning: Mandal with Ind code '{mnd_code_ind}' not found for Village '{village_name}'. Skipping.", self.style.WARNING)
                    skipped += 1
                    continue

                # Determine if the row should be processed based on Village Ind code uniqueness
                if vill_code_ind is None: # If Village Ind code is NA/empty, add the record regardless of AP code
                    # No need to check AP code uniqueness anymore based on the new requirement
                    village = Village.objects.create(
                        village_code_ap=vill_code_ap,
                        village_code_ind=vill_code_ind,
                        village_name=village_name,
                        mandal=mandal,
                        district=mandal.district, # Link to the district via the found mandal
                        is_active=True,
                    )
                    created += 1
                else: # If Village Ind code is present, check for uniqueness based on Village Ind code
                    if Village.objects.filter(village_code_ind=vill_code_ind).exists():
                        self.stdout.write(f"Skipping Village '{village_name}' (Ind code: {vill_code_ind}) - Ind code already exists.", self.style.WARNING)
                        skipped += 1
                        continue
                    # If Village Ind code doesn't exist, proceed to create
                    village = Village.objects.create(
                        village_code_ap=vill_code_ap,
                        village_code_ind=vill_code_ind,
                        village_name=village_name,
                        mandal=mandal,
                        district=mandal.district, # Link to the district via the found mandal
                        is_active=True,
                    )
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nVILLAGE IMPORT COMPLETE!\n"
                f"  Created: {created} Villages\n"
                f"  Skipped: {skipped} Villages (already existed based on Ind code, invalid, or missing Mandal link)\n"
            )
        )

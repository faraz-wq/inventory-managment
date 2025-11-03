import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.locations.models import District, Mandal

class Command(BaseCommand):
    help = "Import Mandals from mandals.csv, checking uniqueness on Ind code. If Ind code is NA/empty, add anyway."

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='mandals.csv',
            help='Path to mandals CSV file (default: mandals.csv in same folder)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing Mandal data before import',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        clear_first = options['clear']

        # Resolve full path
        cmd_dir = Path(__file__).parent
        csv_path = cmd_dir / file_path if not Path(file_path).is_absolute() else Path(file_path)

        if not csv_path.exists():
            raise FileNotFoundError(f"Mandal CSV file not found: {csv_path}")

        self.stdout.write(f"Loading Mandal data from: {csv_path}")

        # Optional: Clear existing data
        if clear_first:
            self.stdout.write("Clearing existing Mandal data...")
            Mandal.objects.all().delete()
            self.stdout.write("Cleared Mandals.")

        created = 0
        skipped = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.strip() for name in reader.fieldnames] # Normalize headers
            self.stdout.write(f"Mandal CSV Headers: {reader.fieldnames}")

            required_cols = {'Mandal', 'MndCodeAP', 'DstCodeAP'} # Need AP codes for linking and basic checks
            if not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames)
                raise ValueError(f"Mandal CSV: Missing required columns: {missing}")

            for row in reader:
                mandal_name = row['Mandal'].strip()
                mnd_code_ap = row['MndCodeAP'].strip()
                dst_code_ap = row['DstCodeAP'].strip()
                mnd_code_ind_raw = row['MndCodeInd'].strip()
                mnd_code_ind = mnd_code_ind_raw if mnd_code_ind_raw and mnd_code_ind_raw != 'NA' else None

                # Skip rows with missing essential AP codes (used for linking)
                if not mnd_code_ap or mnd_code_ap == 'NA' or not dst_code_ap or dst_code_ap == 'NA':
                    self.stdout.write(f"Skipping Mandal row with missing/NA AP codes (AP or District): {row}", self.style.WARNING)
                    skipped += 1
                    continue

                # Find the associated District using the AP code
                try:
                    district = District.objects.get(district_code_ap=dst_code_ap)
                except District.DoesNotExist:
                    self.stdout.write(f"Warning: District with AP code '{dst_code_ap}' not found for Mandal '{mandal_name}'. Skipping.", self.style.WARNING)
                    skipped += 1
                    continue

                # Determine if the row should be processed based on Ind code uniqueness
                if mnd_code_ind is None: # If Ind code is NA/empty, add the record
                    # Check if a record with the same AP code already exists (as a fallback uniqueness check)
                    # This prevents re-adding records that were previously imported using AP code
                    # if Ind code is NA and AP code matches an existing one, it's likely a duplicate
                    if Mandal.objects.filter(mandal_code_ap=mnd_code_ap).exists():
                         self.stdout.write(f"Skipping Mandal '{mandal_name}' (AP code: {mnd_code_ap}, Ind code: NA/empty) - AP code already exists.", self.style.WARNING)
                         skipped += 1
                         continue
                    # If AP code also doesn't exist, proceed to create
                    mandal = Mandal.objects.create(
                        mandal_code_ap=mnd_code_ap,
                        mandal_code_ind=mnd_code_ind,
                        mandal_name=mandal_name,
                        district=district,
                        is_active=True,
                    )
                    created += 1
                else: # If Ind code is present, check for uniqueness based on Ind code
                    if Mandal.objects.filter(mandal_code_ind=mnd_code_ind).exists():
                        self.stdout.write(f"Skipping Mandal '{mandal_name}' (Ind code: {mnd_code_ind}) - Ind code already exists.", self.style.WARNING)
                        skipped += 1
                        continue
                    # If Ind code doesn't exist, proceed to create
                    mandal = Mandal.objects.create(
                        mandal_code_ap=mnd_code_ap,
                        mandal_code_ind=mnd_code_ind,
                        mandal_name=mandal_name,
                        district=district,
                        is_active=True,
                    )
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nMANDAL IMPORT COMPLETE!\n"
                f"  Created: {created} Mandals\n"
                f"  Skipped: {skipped} Mandals (already existed based on Ind code or invalid)\n"
            )
        )

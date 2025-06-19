import csv

# Mapping from original POS file footprints to NEODEN footprints
FOOTPRINT_MAP = {
    "R_0603_1608Metric": "0603D",
    "R_0402_1005Metric": "0402D",
    "R_0201_0603Metric": "0201D",
    "LQFP-100_14x14mm_P0.5mm": "LQFP-100",
    "Fiducial_1.5mm_Mask3mm": "FIDUCIAL",
    "SOT-23": "SOT-23",
    "TO-252-2": "TO-252-2",
    # Add more mappings as needed
}

# Mapping from original designator to value (example: R -> 1K, customize as needed)
VALUE_MAP = {
    "R": "1K",
    # Add more mappings as needed, e.g. for C, Q, IC, etc.
}

def parse_value(ref, val):
    # For resistors, use VALUE_MAP, otherwise return val as is
    for prefix in VALUE_MAP:
        if ref.startswith(prefix):
            return VALUE_MAP[prefix]
    return val

def get_footprint(footprint):
    return FOOTPRINT_MAP.get(footprint, footprint)

def transform_coords(x, y):
    # Example: just pass through, but you may need to transform axis/units or offset
    return round(float(x), 2), round(float(y), 2)

def transform_rot(rot):
    # Example: round to 2 decimals, but might need to flip sign for some machines
    return f"{float(rot):.2f}"

def generate_neoden_csv(input_file, output_file):
    # Write the fixed NEODEN header
    header = [
        ["NEODEN","YY1","P&P FILE"] + [""]*10,
        [""]*13,
        ["PanelizedPCB","UnitLength","0","UnitWidth","0","Rows","1","Columns","1"] + [""]*5,
        [""]*13,
        ["Fiducial","1-X","5.20","1-Y","55.15","OverallOffsetX","0.04","OverallOffsetY","0.14"] + [""]*6,
        [""]*13,
        ["NozzleChange","OFF","BeforeComponent","1","Head1","Drop","Station2","PickUp","Station1"],
        ["NozzleChange","OFF","BeforeComponent","2","Head2","Drop","Station3","PickUp","Station2"],
        ["NozzleChange","OFF","BeforeComponent","1","Head1","Drop","Station1","PickUp","Station1"],
        ["NozzleChange","OFF","BeforeComponent","1","Head1","Drop","Station1","PickUp","Station1"],
        [""]*13,
        ["Designator","Comment","Footprint","Mid X(mm)","Mid Y(mm) ","Rotation","Head ","FeederNo","Mount Speed(%)","Pick Height(mm)","Place Height(mm)","Mode","Skip"]
    ]

    data_rows = []
    with open(input_file, newline='', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            ref = row['Ref'].strip('"')
            val = row['Val'].strip('"')
            package = row['Package'].strip('"')
            x, y = transform_coords(row['PosX'], row['PosY'])
            rot = transform_rot(row['Rot'])
            # Map value and footprint
            comment = parse_value(ref, val)
            footprint = get_footprint(package)
            # Compose row as per the NEODEN format (example)
            neoden_row = [
                ref,                     # Designator
                comment,                 # Comment
                footprint,               # Footprint
                f"{x:.2f}",              # Mid X(mm)
                f"{y:.2f}",              # Mid Y(mm)
                rot,                     # Rotation
                "0",                     # Head
                "1",                     # FeederNo
                "100",                   # Mount Speed(%)
                "0.0",                   # Pick Height(mm)
                "0.0",                   # Place Height(mm)
                "1",                     # Mode
                "0"                      # Skip
            ]
            data_rows.append(neoden_row)

    with open(output_file, "w", newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout)
        for h in header:
            writer.writerow(h)
        for row in data_rows:
            writer.writerow(row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert POS file to NEODEN CSV format")
    parser.add_argument("input_file", help="Input .pos file")
    parser.add_argument("output_file", help="Output .csv file")
    args = parser.parse_args()
    generate_neoden_csv(args.input_file, args.output_file)
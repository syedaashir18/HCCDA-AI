
from datetime import date, timedelta

# ---------- constants ----------
FIXED_CHARGES = 200.00
TV_FEE = 35.00
GST_RATE = 0.17
SURCHARGE_RATE = 0.10
DUE_DAYS = 15
BILLS_FILE = "bills.txt"

# (upper limit of slab, rate per unit)
SLABS = [(100, 10), (200, 15), (300, 22), (700, 30)]
TOP_RATE = 35  # above 700 units


# ---------- functions ----------
def energy_cost(units):
    """Cumulative slab pricing: each band is charged at its own rate."""
    cost = 0
    lower = 0
    for upper, rate in SLABS:
        if units > lower:
            cost += (min(units, upper) - lower) * rate
        lower = upper
    if units > lower:  # remainder above 700
        cost += (units - lower) * TOP_RATE
    return cost


def calculate_bill(units):
    """Return a dict with all charges (raw, unrounded numbers)."""
    energy = energy_cost(units)
    gst = energy * GST_RATE
    within_due = energy + FIXED_CHARGES + TV_FEE + gst
    after_due = within_due * (1 + SURCHARGE_RATE)
    return {
        "energy": energy,
        "fixed": FIXED_CHARGES,
        "tv": TV_FEE,
        "gst": gst,
        "within_due": within_due,
        "after_due": after_due,
    }


def make_challan(name, ref, prev, curr, units, bill, due_date):
    """Build the formatted challan as a string."""
    line = "#" * 44
    dash = "-" * 44
    return "\n".join([
        line,
        "K-Electric - Electricity BILL".center(44),
        line,
        f"Consumer : {name:<20} Ref: {ref}",
        f"Reading  : {prev} -> {curr}",
        f"Units consumed {units:>24}",
        dash,
        f"Energy cost (slabs)      Rs {bill['energy']:>10.2f}",
        f"Fixed / meter charges    Rs {bill['fixed']:>10.2f}",
        f"TV license fee           Rs {bill['tv']:>10.2f}",
        f"GST (17% of energy)      Rs {bill['gst']:>10.2f}",
        dash,
        f"Payable within due date  Rs {bill['within_due']:>10.2f}",
        f"Payable after due date   Rs {bill['after_due']:>10.2f}",
        f"Due date : {due_date}",
        line,
    ])


def read_reading(prompt):
    """Read a non-negative number; raises ValueError for bad input."""
    value = float(input(prompt))
    if value < 0:
        raise ValueError("negative reading")
    return int(value) if value == int(value) else value


# ---------- main program ----------
def main():
    consumers = []  # list of dictionaries, one per consumer
    due_date = date.today() + timedelta(days=DUE_DAYS)

    print("=== Electricity Bill & Challan Generator ===")

    while True:
        print()
        name = input("Consumer name: ").strip()
        ref = input("Reference number: ").strip()

        try:
            prev = read_reading("Previous reading: ")
            curr = read_reading("Current reading: ")
        except ValueError:
            print("Invalid reading! Please enter numbers only. Entry skipped.")
            if input("Bill another consumer? (y/n): ").strip().lower() != "y":
                break
            continue

        units = curr - prev
        if units < 0:
            print("Error: current reading is less than previous reading. Entry skipped.")
        else:
            bill = calculate_bill(units)
            challan = make_challan(name, ref, prev, curr, units, bill, due_date)
            print()
            print(challan)

            late = input("Paid after due date? (y/n): ").strip().lower() == "y"
            payable = bill["after_due"] if late else bill["within_due"]

            with open(BILLS_FILE, "a") as f:  # append every challan
                f.write(challan + "\n\n")

            consumers.append({
                "name": name,
                "ref": ref,
                "prev": prev,
                "curr": curr,
                "units": units,
                "payable": payable,
            })
            print(f"Challan saved to {BILLS_FILE}")

        if input("\nBill another consumer? (y/n): ").strip().lower() != "y":
            break

    # ---------- summary ----------
    total_units = sum(c["units"] for c in consumers)
    total_revenue = sum(c["payable"] for c in consumers)
    print("\n" + "=" * 44)
    print(f"Consumers billed : {len(consumers)}")
    print(f"Total units billed : {total_units}")
    print(f"Total revenue      : Rs {total_revenue:.2f}")
    print("=" * 44)


if __name__ == "__main__":
    main()
import csv

def load_csv(file_path):
    """Load members from a CSV file into a list of dictionaries."""
    members = []
    with open(file_path, encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Skip the header row
        for row in rows:
            member = {
                'username': row[0],
                'id': int(row[1]),
                'access_hash': int(row[2]),
                'name': row[3]
            }
            members.append(member)
    return members

def save_csv(file_path, members):
    """Save a list of members to a CSV file."""
    with open(file_path, 'w', newline='', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'id', 'access_hash', 'name'])
        for member in members:
            writer.writerow([member['username'], member['id'], member['access_hash'], member['name']])

def compare_members(group_members_file, members_to_check_file):
    """Compare members from two CSV files and save results to output files."""
    group_members = load_csv(group_members_file)
    members_to_check = load_csv(members_to_check_file)

    # Convert group member IDs to a set for faster lookup
    group_member_ids = {member['id'] for member in group_members}

    # Separate members based on their presence in the group
    already_members = [member for member in members_to_check if member['id'] in group_member_ids]
    not_members = [member for member in members_to_check if member['id'] not in group_member_ids]

    # Display results
    print(f"Total members in '{members_to_check_file}': {len(members_to_check)}")
    print(f"Already members in the group: {len(already_members)}")
    print(f"Not members in the group: {len(not_members)}")

    # Save results to CSV files
    save_csv('already_members.csv', already_members)
    save_csv('not_members.csv', not_members)

    print("Results saved to 'already_members.csv' and 'not_members.csv'.")

if __name__ == "__main__":
    # Paths to input CSV files
    group_members_file = "group_members.csv"
    members_to_check_file = "members_to_check.csv"

    # Run comparison
    compare_members(group_members_file, members_to_check_file)

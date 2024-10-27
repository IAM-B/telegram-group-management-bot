# Telegram Group Management Bot

This repository provides scripts for managing Telegram group members using the [Telethon](https://github.com/LonamiWebs/Telethon) library. The functionalities include:
1. **Sending notifications** to a list of members.
2. **Adding new members** to a Telegram group.
3. **Checking membership status** of users in a group.
4. **Scraping members** from an existing Telegram group.

## Features

### 1. Notification Bot
- Sends a message to a list of users from a CSV file.
- Tracks notified users by saving their information to `members_notified.csv`.
- Supports sending messages either by username or user ID.

### 2. Add Members to a Group
- Adds members from a CSV file to a specified Telegram group.
- Verifies user IDs and handles privacy restrictions.

### 3. Check Membership Status
- Compares two CSV files to identify which members are already in a group and which are not.
- Outputs results to `already_members.csv` and `not_members.csv`.

### 4. Scrape Group Members
- Scrapes members from a specified Telegram group and saves them to `members.csv` for further processing.

## Prerequisites

- **Python 3.7+**
- **Telethon Library**

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/IAM-B/telegram-group-management-bot.git
   cd telegram-group-management-bot
   ```

2. **Install required packages**:
   ```bash
   pip install telethon
   ```

3. **Setup Configuration**:
   - Create a file named `config.data` in the same directory.
   - Add your `api_id`, `api_hash`, and `phone` number:
     ```
     [cred]
     id = your_api_id
     hash = your_api_hash
     phone = your_phone_number
     ```

## Usage

### 1. Sending Notifications

**Run the Script**:
```bash
python3 send_notifications.py members.csv
```
Replace `members.csv` with the path to your CSV file of users.

**Choose Notification Mode**:
- `1` for user ID.
- `2` for username.

**Result**:
- Notified members are saved to `members_notified.csv`.

### 2. Adding Members to a Group

**Run the Script**:
```bash
python3 add_members.py members.csv
```
Replace `members.csv` with the list of users to add.

**Select Target Group**:
- The script will display available groups for you to choose from.
- Members are added based on their ID or username.

**Output**:
- Each added member’s information is saved to `added_members.csv`.

### 3. Checking Membership Status

**Run the Script**:
```bash
python3 check_members.py members.csv members_to_check.csv
```
Replace `members.csv` with the file containing current group members and `members_to_check.csv` with the list to verify.

**Result**:
- `already_members.csv`: Members already in the group.
- `not_members.csv`: Members not in the group.

### 4. Scraping Group Members

**Run the Script**:
```bash
python3 scrape_members.py
```

**Select Target Group**:
- The script lists available groups to scrape. Choose a group by its displayed number.

**Output**:
- `members.csv` containing the username, ID, access hash, and name of each member in the group.

## CSV Format

All CSV files should follow this format:
```csv
username,id,access_hash,name
user1,123456789,1234567890123456789,John Doe
user2,987654321,9876543210123456789,Jane Smith
```

## Configuration

Adjust `SLEEP_TIME` in the scripts to set the delay between actions to avoid flood errors:
```python
SLEEP_TIME = 30  # seconds
```

## Error Handling

The scripts handle several common Telegram errors:
- **Flood Control**: Pauses if too many messages are sent in a short time.
- **Privacy Restrictions**: Skips users with restrictive privacy settings.
- **Invalid User ID**: Skips entries with invalid IDs or access hashes.

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make changes and commit them: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-branch-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License.

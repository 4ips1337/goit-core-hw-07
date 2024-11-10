from collections import UserDict
from datetime import datetime, timedelta


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except IndexError:
            return "Error: Not enough arguments provided."
        except KeyError:
            return "Error: Contact not found."
    return wrapper



class Field:
    def __init__(self, value):
        self.value = value



class Name(Field):
    pass



class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate_phone(phone):
        return phone.isdigit() and len(phone) == 10



class Birthday(Field):
    def __init__(self, value):
        if not self.validate_birthday(value):
            raise ValueError("Birthday must be in DD.MM.YYYY format.")
        super().__init__(value)

    @staticmethod
    def validate_birthday(birthday):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
            return True
        except ValueError:
            return False



class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            self.phones[self.phones.index(phone_obj)] = Phone(new_phone)
        else:
            raise ValueError("Old phone number not found.")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today().date()
        bday_this_year = datetime.strptime(self.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
        
        if bday_this_year < today:
            bday_this_year = bday_this_year.replace(year=today.year + 1)
        
        return (bday_this_year - today).days

    def __str__(self):
        phones_str = ", ".join(phone.value for phone in self.phones)
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"{self.name.value}: {phones_str if phones_str else 'No phones'}{birthday_str}"



class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Name not found in address book.")

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        seven_days_later = today + timedelta(days=7)
        
        for record in self.data.values():
            if record.birthday:
                bday_this_year = datetime.strptime(record.birthday.value, "%d.%m.%Y").date().replace(year=today.year)
                
                if today <= bday_this_year <= seven_days_later:
                    # Перевіряємо, чи день народження випадає на вихідний
                    if bday_this_year.weekday() == 5:  # Субота
                        bday_this_year += timedelta(days=2)  # Переносимо на понеділок
                    elif bday_this_year.weekday() == 6:  # Неділя
                        bday_this_year += timedelta(days=1)  # Переносимо на понеділок
                    
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": bday_this_year
                    })

        return upcoming_birthdays

    def __str__(self):
        records = "\n".join(str(record) for record in self.data.values())
        return f"AddressBook:\n{records if records else 'No records'}"



@input_error
def handle_add(args, address_book):
    if len(args) == 2:
        name, phone = args
        record = address_book.find(name)
        if record:
            record.add_phone(phone)
        else:
            record = Record(name)
            record.add_phone(phone)
            address_book.add_record(record)
        return f"Contact '{name}' added with phone {phone}."
    return "Error: 'add' command should have two arguments [name] [phone]"


@input_error
def handle_change(args, address_book):
    if len(args) == 3:
        name, old_phone, new_phone = args
        record = address_book.find(name)
        if record:
            try:
                record.edit_phone(old_phone, new_phone)
                return f"Phone number for '{name}' changed from {old_phone} to {new_phone}."
            except ValueError as e:
                return str(e)
        return f"Error: Contact '{name}' not found."
    return "Error: 'change' command should have three arguments [name] [old phone] [new phone]"


@input_error
def handle_phone(args, address_book):
    if len(args) == 1:
        name = args[0]
        record = address_book.find(name)
        if record:
            return f"Phone numbers for {name}: " + ", ".join(phone.value for phone in record.phones)
        return f"Error: Contact '{name}' not found."
    return "Error: 'phone' command should have one argument [name]"


@input_error
def handle_all(address_book):
    return str(address_book)


@input_error
def handle_add_birthday(args, address_book):
    if len(args) == 2:
        name, birthday = args
        record = address_book.find(name)
        if record:
            try:
                record.add_birthday(birthday)
                return f"Birthday for '{name}' set to {birthday}."
            except ValueError as e:
                return str(e)
        return f"Error: Contact '{name}' not found."
    return "Error: 'add-birthday' command should have two arguments [name] [birthday]"


@input_error
def handle_show_birthday(args, address_book):
    if len(args) == 1:
        name = args[0]
        record = address_book.find(name)
        if record and record.birthday:
            return f"Birthday for {name} is {record.birthday.value}."
        return f"Error: Contact '{name}' not found or has no birthday set."
    return "Error: 'show-birthday' command should have one argument [name]"


@input_error
def handle_birthdays(address_book):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(
            f"{entry['name']}'s birthday celebration is on {entry['birthday'].strftime('%d.%m.%Y')}"
            for entry in upcoming_birthdays
        )
    return "No birthdays in the next 7 days."



def main():
    address_book = AddressBook()

    while True:
        user_input = input("Enter command: ").strip()
        command_parts = user_input.split()
        command = command_parts[0].lower()
        args = command_parts[1:]

        if command == "hello":
            print("How can I help you?")
        
        elif command == "add":
            print(handle_add(args, address_book))

        elif command == "change":
            print(handle_change(args, address_book))

        elif command == "phone":
            print(handle_phone(args, address_book))

        elif command == "all":
            print(handle_all(address_book))

        elif command == "add-birthday":
            print(handle_add_birthday(args, address_book))

        elif command == "show-birthday":
            print(handle_show_birthday(args, address_book))

        elif command == "birthdays":
            print(handle_birthdays(address_book))

        elif command in ["close", "exit"]:
            print("Good bye!")
            break
        
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()


import re
import sys

# ==========================================
# PREDEFINED SYMBOLS
# ==========================================

SYMBOL_TABLE = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

for i in range(16):
    SYMBOL_TABLE["R" + str(i)] = i


# ==========================================
# DESTINATION TABLE
# ==========================================

DEST = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}


# ==========================================
# JUMP TABLE
# ==========================================

JUMP = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# ==========================================
# COMPUTATION TABLE
# ==========================================

COMP = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",

    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}


# ==========================================
# CLEAN LINES
# ==========================================

def clean_lines(filename):
    instructions = []

    with open(filename, "r") as file:
        for line_number, line in enumerate(file, start=1):

            line = line.split("//")[0].strip()

            if line:
                instructions.append((line, line_number))

    return instructions


# ==========================================
# FIRST PASS
# ==========================================

def first_pass(instructions):

    symbol_table = SYMBOL_TABLE.copy()
    labels = {}
    rom_address = 0
    errors = []

    for line, line_number in instructions:

        if line.startswith("(") and line.endswith(")"):

            label = line[1:-1]

            if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", label):
                errors.append(
                    f"Line {line_number}: Invalid label"
                )
                continue

            if label in symbol_table:
                print(
                    f"Warning: Line {line_number}: "
                    f"Duplicate label '{label}'"
                )
                continue

            symbol_table[label] = rom_address
            labels[label] = rom_address

        else:
            rom_address += 1

    return symbol_table, labels, errors


# ==========================================
# A-INSTRUCTION
# ==========================================

def a_instruction(line, symbol_table, next_variable):

    symbol = line[1:]

    if symbol.isdigit():
        address = int(symbol)

    elif symbol in symbol_table:
        address = symbol_table[symbol]

    else:
        if not re.fullmatch(
            r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", symbol
        ):
            raise ValueError("Invalid symbol")

        address = next_variable[0]

        symbol_table[symbol] = address
        next_variable[0] += 1

    if address < 0 or address > 32767:
        raise ValueError("Address out of range")

    return format(address, "016b")


# ==========================================
# C-INSTRUCTION
# ==========================================

def c_instruction(line):

    line = re.sub(r"\s+", "", line)

    if line.count("=") > 1 or line.count(";") > 1:
        raise ValueError("Invalid C-instruction")

    if "=" in line:
        dest, remaining = line.split("=", 1)
    else:
        dest, remaining = "", line

    if ";" in remaining:
        comp, jump = remaining.split(";", 1)
    else:
        comp, jump = remaining, ""

    if dest not in DEST:
        raise ValueError("Invalid destination")

    if comp not in COMP:
        raise ValueError("Invalid computation")

    if jump not in JUMP:
        raise ValueError("Invalid jump")

    binary = "111" + COMP[comp] + DEST[dest] + JUMP[jump]

    return binary


# ==========================================
# SECOND PASS
# ==========================================

def second_pass(instructions, symbol_table):

    machine_code = []
    next_variable = [16]
    errors = []

    for line, line_number in instructions:

        if line.startswith("(") and line.endswith(")"):
            continue

        try:

            if line.startswith("@"):

                binary = a_instruction(
                    line, symbol_table, next_variable
                )

            else:

                binary = c_instruction(line)

            machine_code.append(binary)

        except ValueError as error:

            errors.append(
                f"Line {line_number}: {error}"
            )

    return machine_code, errors


# ==========================================
# SAVE SYMBOLS
# ==========================================

def save_symbols(symbol_table, labels, filename="symbols.txt"):

    with open(filename, "w") as file:

        file.write("SYMBOL\tADDRESS\n")
        file.write("-------------------\n")

        for symbol, address in labels.items():
            file.write(f"{symbol}\t{address}\n")

        file.write("\nVARIABLES\n")

        for symbol, address in symbol_table.items():

            if (
                address >= 16
                and symbol not in SYMBOL_TABLE
                and symbol not in labels
            ):
                file.write(f"{symbol}\t{address}\n")


# ==========================================
# MAIN ASSEMBLER
# ==========================================

def assemble(filename):

    try:

        instructions = clean_lines(filename)

        symbol_table, labels, first_errors = first_pass(
            instructions
        )

        machine_code, second_errors = second_pass(
            instructions, symbol_table
        )

        errors = first_errors + second_errors

        if errors:

            for error in errors:
                print(error)

            print("Assembly failed.")
            return

        output_file = filename.rsplit(".", 1)[0] + ".hack"

        with open(output_file, "w") as file:

            for instruction in machine_code:
                file.write(instruction + "\n")

        save_symbols(symbol_table, labels)

        print("Assembly successful!")
        print("Output file:", output_file)
        print("Total instructions:", len(machine_code))
        print("Symbols saved in symbols.txt")

    except FileNotFoundError:

        print("Error: Input file not found:", filename)


# ==========================================
# PROGRAM START
# ==========================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage: python3 assembler.py filename.asm")

    else:

        assemble(sys.argv[1])

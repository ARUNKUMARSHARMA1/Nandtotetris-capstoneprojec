#!/usr/bin/env python3
"""
A two-pass assembler for the Hack computer (Nand2Tetris).
For K=76, this version reports invalid instructions with their source line number.
Usage: python assembler.py input.asm [output.hack]
"""
import re
import sys
from pathlib import Path

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4,
    "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9,
    "R10": 10, "R11": 11, "R12": 12, "R13": 13,
    "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576,
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101",
    "!A": "0110001", "-D": "0001111", "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101",
}
DEST = {
    None: "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}
JUMP = {
    None: "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def clean_source(path):
    """Return (original_line_number, cleaned_instruction) pairs."""
    result = []
    with open(path, "r", encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            line = raw.split("//", 1)[0].strip()
            if line:
                result.append((line_number, re.sub(r"\s+", "", line)))
    return result


def assemble(input_path):
    lines = clean_source(input_path)
    symbols = dict(PREDEFINED)

    # Pass 1: collect labels and their ROM addresses.
    rom_address = 0
    for line_number, instruction in lines:
        if instruction.startswith("(") and instruction.endswith(")"):
            label = instruction[1:-1]
            if not SYMBOL_RE.match(label):
                raise ValueError(f"Line {line_number}: invalid label '{instruction}'")
            if label in symbols:
                raise ValueError(f"Line {line_number}: duplicate or reserved label '{label}'")
            symbols[label] = rom_address
        else:
            rom_address += 1

    # Pass 2: translate instructions and allocate variables from RAM[16].
    machine_code = []
    next_variable = 16

    for line_number, instruction in lines:
        if instruction.startswith("(") and instruction.endswith(")"):
            continue

        if instruction.startswith("@"):
            symbol = instruction[1:]
            if not symbol:
                raise ValueError(f"Line {line_number}: invalid instruction '{instruction}'")
            if symbol.isdigit():
                address = int(symbol)
            else:
                if not SYMBOL_RE.match(symbol):
                    raise ValueError(f"Line {line_number}: invalid instruction '{instruction}'")
                if symbol not in symbols:
                    symbols[symbol] = next_variable
                    next_variable += 1
                address = symbols[symbol]
            if not 0 <= address <= 32767:
                raise ValueError(f"Line {line_number}: A-instruction address out of range")
            machine_code.append(f"{address:016b}")
            continue

        # C-instruction: dest=comp;jump (either dest or jump may be omitted).
        try:
            if instruction.count("=") > 1 or instruction.count(";") > 1:
                raise KeyError
            if "=" in instruction:
                dest, remainder = instruction.split("=", 1)
                if dest not in DEST or not dest:
                    raise KeyError
            else:
                dest, remainder = None, instruction

            if ";" in remainder:
                comp, jump = remainder.split(";", 1)
                if jump not in JUMP or not jump:
                    raise KeyError
            else:
                comp, jump = remainder, None

            if comp not in COMP:
                raise KeyError
            bits = "111" + COMP[comp] + DEST[dest] + JUMP[jump]
            machine_code.append(bits)
        except (KeyError, ValueError):
            raise ValueError(
                f"Line {line_number}: invalid instruction '{instruction}'"
            )

    return machine_code


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python assembler.py input.asm [output.hack]")
        sys.exit(2)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) == 3 else input_path.with_suffix(".hack")

    try:
        code = assemble(input_path)
        output_path.write_text("\n".join(code) + "\n", encoding="utf-8")
        print(f"Assembly successful: {len(code)} instructions -> {output_path}")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

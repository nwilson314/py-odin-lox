package lox

import "core:fmt"

disassemble_chunk :: proc(chunk: ^Chunk, name: string) {
    fmt.printf("== %s ==\n", name)
    offset := 0
    for offset < len(chunk.code) {
        offset = disassemble_instruction(chunk, offset)
    }
}

disassemble_instruction :: proc(chunk: ^Chunk, offset: int) -> int {
    fmt.printf("%04d ", offset)

    if offset > 0 && chunk.lines[offset] == chunk.lines[offset - 1] {
        fmt.printf("   | ")
    } else {
        fmt.printf("%4d ", chunk.lines[offset])
    }

    instruction := chunk.code[offset]

    switch OpCode(instruction) {
        case OpCode.OP_RETURN:
            return simple_instruction("OP_RETURN", offset)
        case OpCode.OP_CONSTANT:
            return constant_instruction("OP_CONSTANT", chunk, offset)
        case:
            fmt.printf("Unknown opcode %d\n", instruction)
            return offset + 1
    }
}

simple_instruction :: proc(name: string, offset: int) -> int {
    fmt.printf("%s\n", name)
    return offset + 1
}

constant_instruction :: proc(name: string, chunk: ^Chunk, offset: int) -> int {
    constant := chunk.code[offset + 1]
    fmt.printf("%-16s %4d '", name, constant)
    print_value(chunk.constants.values[constant])
    fmt.printf("'\n")
    return offset + 2
}
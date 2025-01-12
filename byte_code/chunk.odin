package lox

Chunk :: struct {
    code: [dynamic]u8,
    lines: [dynamic]int,
    constants: ValueArray,
}

init_chunk :: proc(chunk: ^Chunk) {
    chunk.code = make([dynamic]u8)
    chunk.lines = make([dynamic]int)
    init_value_array(&chunk.constants)
}

write_chunk :: proc(chunk: ^Chunk, byte: u8, line: int) {
    append(&chunk.code, byte)
    append(&chunk.lines, line)
}

free_chunk :: proc(chunk: ^Chunk) {
    delete(chunk.code)
    delete(chunk.lines)
    free_value_array(&chunk.constants)
    init_chunk(chunk)
}

add_constant :: proc(chunk: ^Chunk, value: Value) -> int {
    write_value_array(&chunk.constants, value)
    return len(chunk.constants.values) - 1
}
package lox

main :: proc() {
    chunk: Chunk
    init_chunk(&chunk)

    constant := add_constant(&chunk, 1.2)
    write_chunk(&chunk, u8(OpCode.OP_CONSTANT), 123)
    write_chunk(&chunk, u8(constant), 123)

    write_chunk(&chunk, u8(OpCode.OP_RETURN), 123)

    disassemble_chunk(&chunk, "test chunk")

    free_chunk(&chunk)
}
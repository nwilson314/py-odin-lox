package lox

main :: proc() {
    init_vm()

    chunk: Chunk
    init_chunk(&chunk)

    constant := add_constant(&chunk, 1.2)
    write_chunk(&chunk, u8(OpCode.OP_CONSTANT), 123)
    write_chunk(&chunk, u8(constant), 123)

    constant = add_constant(&chunk, 3.4)
    write_chunk(&chunk, u8(OpCode.OP_CONSTANT), 123)
    write_chunk(&chunk, u8(constant), 123)

    write_chunk(&chunk, u8(OpCode.OP_ADD), 123)
    write_chunk(&chunk, u8(OpCode.OP_CONSTANT), 123)
    write_chunk(&chunk, u8(constant), 123)

    write_chunk(&chunk, u8(OpCode.OP_DIVIDE), 123)
    write_chunk(&chunk, u8(OpCode.OP_NEGATE), 123)
    
    write_chunk(&chunk, u8(OpCode.OP_RETURN), 123)

    disassemble_chunk(&chunk, "test chunk")
    interpret(&chunk)

    free_vm()
    free_chunk(&chunk)
}
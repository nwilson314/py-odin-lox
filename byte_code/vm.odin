package lox

import "core:fmt"

DEBUG_TRACE_EXECUTION :: false
STACK_MAX :: 256

vm: VM

VM :: struct {
    chunk: ^Chunk,
    ip: []u8,
    stack: [STACK_MAX]Value,
    stack_top: int,
}

InterpretResult :: enum {
    INTERPRET_OK,
    INTERPRET_COMPILE_ERROR,
    INTERPRET_RUNTIME_ERROR,
}

init_vm :: proc() {
    reset_stack()
}

free_vm :: proc() {

}

interpret :: proc(chunk: ^Chunk) -> InterpretResult {
    vm.chunk = chunk
    vm.ip = vm.chunk.code[:]
    return run()
}

run :: proc() -> InterpretResult {
    for {
        if DEBUG_TRACE_EXECUTION {
            fmt.printf("         ")
            for slot in vm.stack[:vm.stack_top] {
                fmt.printf("[ ")
                print_value(slot)
                fmt.printf(" ]")
            }
            fmt.println()
            disassemble_instruction(vm.chunk, len(vm.chunk.code) - len(vm.ip))
        }

        instruction := OpCode(read_byte())
        
        #partial switch instruction {
            case .OP_CONSTANT:
                constant := read_constant()
                push(constant)
            case .OP_ADD:
                a, b := binary_op(.OP_ADD)
                push(a + b)
            case .OP_SUBTRACT:
                a, b := binary_op(.OP_SUBTRACT)
                push(a - b)
            case .OP_MULTIPLY:
                a, b := binary_op(.OP_MULTIPLY)
                push(a * b)
            case .OP_DIVIDE:
                a, b := binary_op(.OP_DIVIDE)
                push(a / b)
            case .OP_NEGATE:
                op1 := pop()
                push(-op1)
            case .OP_RETURN:
                print_value(pop())
                fmt.println()
                return .INTERPRET_OK
            case:
                return .INTERPRET_COMPILE_ERROR
        }
        
    }
}

reset_stack :: proc() {
    vm.stack_top = 0
}

@(private="file")
read_byte :: proc() -> u8 {
    bite := vm.ip[0]
    vm.ip = vm.ip[1:]
    return bite
}

@(private="file")
read_constant :: proc() -> Value {
    return vm.chunk.constants.values[read_byte()]
}

@(private="file")
binary_op :: proc(op: OpCode) -> (Value, Value) {
    b := pop()
    a := pop()
    return a, b
}

push :: proc(value: Value) {
    vm.stack[vm.stack_top] = value
    vm.stack_top += 1
}

pop :: proc() -> Value {
    vm.stack_top -= 1
    return vm.stack[vm.stack_top]
}
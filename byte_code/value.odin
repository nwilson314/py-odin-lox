package lox

import "core:fmt"

Value :: f64

ValueArray :: struct {
    values: [dynamic]Value,
}

init_value_array :: proc(array: ^ValueArray) {
    array.values = make([dynamic]Value)
}

write_value_array :: proc(array: ^ValueArray, value: Value) {
    append(&array.values, value)
}

free_value_array :: proc(array: ^ValueArray) {
    delete(array.values)
}

print_value :: proc(value: Value) {
    fmt.printf("%g", value)
}
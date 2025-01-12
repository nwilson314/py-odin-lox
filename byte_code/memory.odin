package lox

reallocate :: proc($T: typeid, pointer: []T, old_size: int, new_size: int) -> []T {
    if new_size == 0 {
        if len(pointer) > 0 {
            delete(pointer)
        }
        return nil
    }

    new_data := make([]T, new_size)
    if len(pointer) > 0 {
        copy(new_data, pointer[:min(len(pointer), new_size)])
        delete(pointer)
    }
    return new_data
}

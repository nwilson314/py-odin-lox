package olox 

Scanner :: struct {
    source: string
}

TokenType :: enum {
    EOF
}

Token :: struct {
    type: TokenType,
    value: string,
    line: int
}

scan_tokens :: proc(scanner: Scanner) -> [dynamic]Token {
    tokens: [dynamic]Token

    token := Token {
        type=.EOF,
        value="",
        line=0,
    }

    append_elem(&tokens, token)

    return tokens

}
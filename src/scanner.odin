package olox 

Scanner :: struct {
    source: string,
    tokens: [dynamic]Token,
    start: int,
    current: int,
    line: int
}

TokenType :: enum {
    // Single-character tokens.
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,

    // One or two character tokens.
    BANG, BANG_EQUAL,
    EQUAL, EQUAL_EQUAL,
    GREATER, GREATER_EQUAL,
    LESS, LESS_EQUAL,
    // Literals.
    IDENTIFIER, STRING, NUMBER,

    // Keywords.
    AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,

    EOF
}

Token :: struct {
    type: TokenType,
    lexeme: string,
    literal: any,
    line: int
}

keywords := map[string]TokenType{
    "and"   = .AND,
    "class" = .CLASS,
    "else"  = .ELSE,
    "false" = .FALSE,
    "for"   = .FOR,
    "fun"   = .FUN,
    "if"    = .IF,
    "nil"   = .NIL,
    "or"    = .OR,
    "print" = .PRINT,
    "return"= .RETURN,
    "super" = .SUPER,
    "this"  = .THIS,
    "true"  = .TRUE,
    "var"   = .VAR,
    "while" = .WHILE
}

create_scanner :: proc(source: string) -> Scanner {
    return Scanner {
        source = source,
        tokens = {},
        start = 0,
        current = 0,
        line = 1,
    }
}

create_token :: proc(type: TokenType, lexeme: string, literal: any, line: int) -> Token {
    return Token {
        type = type,
        lexeme = lexeme,
        literal = literal,
        line = line,
    }
}

token_to_string :: proc(token: Token) -> string {
    // return type + " " + lexeme + " " + literal;
    return ""
}

scan_tokens :: proc() -> [dynamic]Token {
    for !is_at_end() {
        scan_token()
    }

    append_elem(&scanner.tokens, create_token(.EOF, "", nil, scanner.line))
    return scanner.tokens
}

scan_token :: proc() {
    c := advance()

    switch c {
        case '(':
            add_token(.LEFT_PAREN)
        case ')':
            add_token(.RIGHT_PAREN)
        case '{':
            add_token(.LEFT_BRACE)
        case '}':
            add_token(.RIGHT_BRACE)
        case ',':
            add_token(.COMMA)
        case '.':
            add_token(.DOT)
        case '-':
            add_token(.MINUS)
        case '+':
            add_token(.PLUS)
        case ';':
            add_token(.SEMICOLON)
        case '*':
            add_token(.STAR)
        case '!':
            if match('=') {
                add_token(.BANG_EQUAL)
            } else {
                add_token(.BANG)
            }
        case '=':
            if match('=') {
                add_token(.EQUAL_EQUAL)
            } else {
                add_token(.EQUAL)
            }
        case '<':
            if match('=') {
                add_token(.LESS_EQUAL)
            } else {
                add_token(.LESS)
            }
        case '>':
            if match('=') {
                add_token(.GREATER_EQUAL)
            } else {
                add_token(.GREATER)
            }
        case '/':
            if match('/') {
                // A comment goes until the end of the line.
                for peek() != '\n' && !is_at_end() {
                    advance()
                }
            } else {
                add_token(.SLASH)
            }
        case ' ':
        case '\r':
        case '\t':
            // Ignore whitespace.
        case '\n':
            scanner.line += 1
        case '"':
            scan_string()
        case :
            if is_digit(c) {
                scan_number()
            } else if is_alpha(c){
                scan_identifier()
            }else {
                error(scanner.line, "Unexpected character.")
            }
    }
}

is_at_end :: proc() -> bool {
    return scanner.current >= len(scanner.source)
}

advance :: proc() -> u8 {
    scanner.current += 1
    return scanner.source[scanner.current - 1]
}

add_token :: proc(type: TokenType) {
    add_token_literal(type, nil)
}

add_token_literal :: proc(type: TokenType, literal: any) {
    text := scanner.source[scanner.start:scanner.current]
    append_elem(&scanner.tokens, create_token(type, text, literal, scanner.line))
}

match :: proc(expected: u8) -> bool {
    if is_at_end() {
        return false
    }
    if scanner.source[scanner.current] != expected {
        return false
    }
    scanner.current += 1
    return true
}

peek :: proc() -> u8 {
    if is_at_end() {
        return 0
    }
    return scanner.source[scanner.current]
}

peek_next :: proc() -> u8 {
    if scanner.current + 1 >= len(scanner.source) {
        return 0
    }
    return scanner.source[scanner.current + 1]
}

scan_string :: proc() {
    for !is_at_end() && peek() != '"' {
        if peek() == '\n' {
            scanner.line += 1
        }
        advance()
    }
    if is_at_end() {
        error(scanner.line, "Unterminated string.")
        return
    }
    // The closing quote.
    advance()
    // Trim the surrounding quotes.
    value := scanner.source[scanner.start + 1:scanner.current - 1]
    add_token_literal(.STRING, value)
}

is_digit :: proc(c: u8) -> bool {
    return c >= '0' && c <= '9'
}

is_alpha :: proc(c: u8) -> bool {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_'
}

is_alpha_numeric :: proc(c: u8) -> bool {
    return is_alpha(c) || is_digit(c)
}

scan_number :: proc() {
    for is_digit(peek()) {
        advance()
    }
    // Look for a fractional part.
    if peek() == '.' && is_digit(peek_next()) {
        // Consume the "."
        advance()
        for is_digit(peek()) {
            advance()
        }
    }
    add_token_literal(.NUMBER, scanner.source[scanner.start:scanner.current])
}

scan_identifier :: proc() {
    for is_alpha_numeric(peek()) {
        advance()
    }

    text := scanner.source[scanner.start:scanner.current]
    type, ok := keywords[text]

    if !ok {
        type = .IDENTIFIER
    }

    add_token(type)
}
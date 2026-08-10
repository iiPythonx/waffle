preload:
    a: .string "It has been "
    b: .string " years since the UNIX epoch.\n"

main:

    ; Starting numbers
    ldi r1, 2026
    ldi r2, 1970

    ; Calculate difference
    sub r1, r2

    ; I/O
    ldi r3, &a
    swa r3, D_WRITE_STR  ; Send string &a to terminal
    swa r1, D_WRITE_INT  ; Send resulting number to terminal
    ldi r3, &b
    swa r3, D_WRITE_STR  ; Send string &b to terminal

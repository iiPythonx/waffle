preload:
    hello: .string "Hello, world!"

write:

    ; Load from address
    lbr r3, r1

    ; Should we die? (hit end of string)
    ldi r7, 0
    cmp r3, r7  ; r3 = current character, r7 = null (0)
    jne continue    ; hit a null string terminator
    hlt

    continue:

    ; Send character to terminal
    swa r3, D_WRITE_CHR

    ; Increment status
    ldi r8, 1
    add r1, r8  ; += 1

    ; Rinse and repeat
    jmp write

main:

    ; Store the starting string address (0x2000)
    ldi r1, &hello

    ; Start looping
    jmp write

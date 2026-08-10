preload:
    strftime: .string "The current time is %H:%M:%S %p."

terminate:
    hlt

main:

    ; Send address of format string to time driver
    ldi r1, &strftime
    swa r1, D_SET_TIME_FMT

    ; Ask time driver to write time value to 0x2100
    ldi r1, 0x2100
    swa r1, D_READ_TIME_FMT

    ; Send that string to the terminal
    swa r1, D_WRITE_STR

    ; Sleep 500ms
    ldi r1, 500
    swa r1, D_SLEEP

    ; Carriage return
    ldi r1, 13
    swa r1, D_WRITE_CHR

    ; Infinite loop
    jmp main
